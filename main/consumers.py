import aiohttp
import asyncio
import aioredis
import json
import logging
from django.conf import settings
from django.urls import reverse
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.generic.http import AsyncHttpConsumer
from . import models


logger = logging.getLogger(__name__)


class ChatNotifyConsumer(AsyncHttpConsumer):
    def is_employee_func(self, user):
        return not user.is_anonymous and user.is_employee

    async def handle(self, body):
        is_employee = await database_sync_to_async(
            self.is_employee_func
        )(self.scope["user"])

        if is_employee:
            logger.info(
                "Opening notify stream for user %s and params %s",
                self.scope.get("user"),
                self.scope.get("query_string"),
            )
            await self.send_headers(
                headers=[
                    ("Cache-Control", "no-cache"),
                    ("Content-Type", "text/event-stream"),
                    ("Transfer-Encoding", "chunked"),
                ]
            )
            self.is_streaming = True
            self.no_poll = (
                self.scope.get("query_string") == "nopoll"
            )
            asyncio.get_event_loop().create_task(self.stream())
        else:
            logger.info(
                "Unauthorized notify stream for user %s and params %s",
                self.scope.get("user"),
                self.scope.get("query_string"),
            )
            raise StopConsumer("Unauthorized")

    async def stream(self):
        r_conn = await aioredis.create_redis(settings.REDIS_URL)
        while self.is_streaming:
            active_chats = await r_conn.keys(
                "customer-service_*"
            )

            presences = {}
            for i in active_chats:
                _, order_id, user_email = i.decode("utf8").split(
                    "_"
                )
                if order_id in presences:
                    presences[order_id].append(user_email)
                else:
                    presences[order_id] = [user_email]

            data = []
            for order_id, emails in presences.items():
                data.append(
                    {
                        "link": reverse(
                            "cs_chat",
                            kwargs={"order_id": order_id}
                        ),
                        "text": "%s (%s)"
                        % (order_id, ", ".join(emails)),
                    }
                )

            payload = "data: %s\n\n" % json.dumps(data)
            logger.info(
                "Broadcasting presence info to user %s",
                self.scope["user"],
            )
            if self.no_poll:
                await self.send_body(payload.encode("utf-8"))
                self.is_streaming = False
            else:
                await self.send_body(
                    payload.encode("utf-8"),
                    more_body=self.is_streaming,
                )
                await asyncio.sleep(5)

    async def disconnect(self):
        logger.info(
            "Closing notify stream for user %s",
            self.scope.get("user"),
        )
        self.is_streaming = False


class ChatConsumer(AsyncJsonWebsocketConsumer):
    EMPLOYEE = 2
    CLIENT = 1

    def get_user_type(self, user, order_id):
        order = get_object_or_404(models.Order, pk=order_id)

        if user.is_employee:
            order.last_spoken_to = user
            order.save()
            return ChatConsumer.EMPLOYEE
        elif order.user == user:
            return ChatConsumer.CLIENT
        else:
            return None

    async def connect(self):
        self.order_id = self.scope["url_route"]["kwargs"][
            "order_id"
        ]
        self.room_group_name = (
            "customer-service_%s" % self.order_id
        )
        authorized = False
        if self.scope["user"].is_anonymous:
            await self.close()

        user_type = await database_sync_to_async(
            self.get_user_type
        )(self.scope["user"], self.order_id)

        if user_type == ChatConsumer.EMPLOYEE:
            logger.info(
                "Opening chat stream for employee %s",
                self.scope["user"],
            )
            authorized = True
        elif user_type == ChatConsumer.CLIENT:
            logger.info(
                "Opening chat stream for client %s",
                self.scope["user"],
            )
            authorized = True
        else:
            logger.info(
                "Unauthorized connection from %s",
                self.scope["user"],
            )
            await self.close()

        if authorized:
            self.r_conn = await aioredis.create_redis(
                settings.REDIS_URL
            )

            await self.channel_layer.group_add(
                self.room_group_name, self.channel_name
            )
            await self.accept()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_join",
                    "username": self.scope[
                        "user"
                    ].get_full_name(),
                },
            )

    async def disconnect(self, close_code):
        if not self.scope["user"].is_anonymous:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_leave",
                    "username": self.scope[
                        "user"
                    ].get_full_name(),
                },
            )
            logger.info(
                "Closing chat stream for user %s",
                self.scope["user"],
            )
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def receive_json(self, content):
        typ = content.get("type")
        if typ == "message":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "username": self.scope[
                        "user"
                    ].get_full_name(),
                    "message": content["message"],
                },
            )
        elif typ == "heartbeat":
            await self.r_conn.setex(
                "%s_%s"
                % (
                    self.room_group_name,
                    self.scope["user"].email,
                ),
                10,
                "1",
            )

    async def chat_message(self, event):
        await self.send_json(event)

    async def chat_join(self, event):
        await self.send_json(event)

    async def chat_leave(self, event):
        await self.send_json(event)


class OrderTrackerConsumer(AsyncHttpConsumer):
    def verify_user(self, user, order_id):
        order = get_object_or_404(models.Order, pk=order_id)
        return order.user == user

    async def query_remote_server(self, order_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://pastebin.com/put_url_here"
            ) as resp:
                return await resp.read()

    async def handle(self, body):
        self.order_id = self.scope["url_route"]["kwargs"][
            "order_id"
        ]
        is_authorized = await database_sync_to_async(
            self.verify_user
        )(self.scope["user"], self.order_id)

        if is_authorized:
            logger.info(
                "Order tracking request for user %s and order %s",
                self.scope.get("user"),
                self.order_id,
            )
            payload = await self.query_remote_server(
                self.order_id
            )
            logger.info(
                "Order tracking response %s for user %s and order %s",
                payload,
                self.scope.get("user"),
                self.order_id
            )
            await self.send_response(200, payload)
        else:
            raise StopConsumer("unauthorized")
