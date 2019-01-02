from unittest.mock import patch, MagicMock
import asyncio
import json
from django.contrib.auth.models import Group
from django.test import TestCase
from channels.db import database_sync_to_async
from channels.testing import (
    WebsocketCommunicator,
    HttpCommunicator,
)
from main import consumers
from main import factories


class TestConsumers(TestCase):
    def test_chat_presence_works(self):
        def init_db():
            user = factories.UserFactory(
                email="user@site.com",
                first_name="John",
                last_name="Smith",
            )
            order = factories.OrderFactory(user=user)
            cs_user = factories.UserFactory(
                email="customerservice@booktime.domain",
                first_name="Adam",
                last_name="Ford",
                is_staff=True,
            )
            employees, _ = Group.objects.get_or_create(
                name="Employees"
            )
            cs_user.groups.add(employees)

            return user, order, cs_user

        async def test_body():
            user, order, notify_user = await database_sync_to_async(
                init_db
            )()

            communicator = WebsocketCommunicator(
                consumers.ChatConsumer,
                "/ws/customer-service/%d/" % order.id,
            )
            communicator.scope["user"] = user
            communicator.scope["url_route"] = {
                "kwargs": {"order_id": order.id}
            }
            connected, _ = await communicator.connect()
            self.assertTrue(connected)

            await communicator.send_json_to(
                {"type": "heartbeat"}
            )
            await communicator.disconnect()

            communicator = HttpCommunicator(
                consumers.ChatNotifyConsumer,
                "GET",
                "/customer-service/notify/",
            )
            communicator.scope["user"] = notify_user
            communicator.scope["query_string"] = "nopoll"

            response = await communicator.get_response()
            self.assertTrue(
                response["body"].startswith(b"data: ")
            )
            payload = response["body"][6:]
            data = json.loads(payload.decode("utf8"))
            self.assertEquals(
                data,
                [
                    {
                        "link": "/customer-service/%d/" % order.id,
                        "text": "%d (user@site.com)" % order.id,
                    }
                ],
                "expecting someone in the room but noone found",
            )

            await asyncio.sleep(10)

            communicator = HttpCommunicator(
                consumers.ChatNotifyConsumer,
                "GET",
                "/customer-service/notify/",
            )
            communicator.scope["user"] = notify_user
            communicator.scope["query_string"] = "nopoll"
            response = await communicator.get_response()
            self.assertTrue(
                response["body"].startswith(b"data: ")
            )
            payload = response["body"][6:]
            data = json.loads(payload.decode("utf8"))
            self.assertEquals(
                data,
                [],
                "expecting noone in the room but someone found",
            )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_body())

    def test_chat_between_two_users_works(self):
        def init_db():
            user = factories.UserFactory(
                email="john@bestemails.com",
                first_name="John",
                last_name="Smith",
            )
            order = factories.OrderFactory(user=user)
            cs_user = factories.UserFactory(
                email="customerservice@booktime.domain",
                first_name="Adam",
                last_name="Ford",
                is_staff=True,
            )
            employees, _ = Group.objects.get_or_create(
                name="Employees"
            )
            cs_user.groups.add(employees)

            return user, order, cs_user

        async def test_body():
            user, order, cs_user = await database_sync_to_async(
                init_db
            )()

            communicator = WebsocketCommunicator(
                consumers.ChatConsumer,
                "/ws/customer-service/%d/" % order.id,
            )
            communicator.scope["user"] = user
            communicator.scope["url_route"] = {
                "kwargs": {"order_id": order.id}
            }
            connected, _ = await communicator.connect()
            self.assertTrue(connected)

            cs_communicator = WebsocketCommunicator(
                consumers.ChatConsumer,
                "/ws/customer-service/%d/" % order.id,
            )
            cs_communicator.scope["user"] = cs_user
            cs_communicator.scope["url_route"] = {
                "kwargs": {"order_id": order.id}
            }
            connected, _ = await cs_communicator.connect()
            self.assertTrue(connected)

            await communicator.send_json_to(
                {
                    "type": "message",
                    "message": "hello customer service",
                }
            )

            await asyncio.sleep(1)

            await cs_communicator.send_json_to(
                {"type": "message", "message": "hello user"}
            )

            self.assertEquals(
                await communicator.receive_json_from(),
                {"type": "chat_join", "username": "John Smith"},
            )
            self.assertEquals(
                await communicator.receive_json_from(),
                {"type": "chat_join", "username": "Adam Ford"},
            )
            self.assertEquals(
                await communicator.receive_json_from(),
                {
                    "type": "chat_message",
                    "username": "John Smith",
                    "message": "hello customer service",
                },
            )
            self.assertEquals(
                await communicator.receive_json_from(),
                {
                    "type": "chat_message",
                    "username": "Adam Ford",
                    "message": "hello user",
                },
            )

            await communicator.disconnect()
            await cs_communicator.disconnect()

            order.refresh_from_db()
            self.assertEquals(order.last_spoken_to, cs_user)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_body())

    def test_chat_blocks_unauthorized_users(self):
        def init_db():
            user = factories.UserFactory(
                email="john@bestemails.com",
                first_name="John",
                last_name="Smith",
            )
            order = factories.OrderFactory()

            return user, order

        async def test_body():
            user, order = await database_sync_to_async(init_db)()

            communicator = WebsocketCommunicator(
                consumers.ChatConsumer,
                "/ws/customer-service/%d/" % order.id,
            )
            communicator.scope["user"] = user
            communicator.scope["url_route"] = {
                "kwargs": {"order_id": order.id}
            }
            connected, _ = await communicator.connect()
            self.assertFalse(connected)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_body())

    def test_order_tracker_works(self):
        def init_db():
            user = factories.UserFactory(
                email="mobiletracker@site.com"
            )
            order = factories.OrderFactory(user=user)
            return user, order

        async def test_body():
            user, order = await database_sync_to_async(
                init_db
            )()

            awaitable_requestor = asyncio.coroutine(MagicMock(return_value=b"SHIPPED"))

            with patch.object(
                consumers.OrderTrackerConsumer, "query_remote_server"
            ) as mock_requestor:
                mock_requestor.side_effect = awaitable_requestor
                communicator = HttpCommunicator(
                    consumers.OrderTrackerConsumer,
                    "GET",
                    "/mobile-api/my-orders/%d/tracker/" % order.id,
                )
                communicator.scope["user"] = user
                communicator.scope["url_route"] = {
                    "kwargs": {"order_id": order.id}
                }

                response = await communicator.get_response()
                data = response["body"].decode("utf8")

                mock_requestor.assert_called_once()
                self.assertEquals(
                    data,
                    "SHIPPED"
                )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_body())
