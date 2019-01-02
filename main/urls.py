from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from rest_framework import routers
from rest_framework.authtoken import views as authtoken_views
from main import views
from main import models
from main import forms
from main import endpoints
from main import admin


router = routers.DefaultRouter()
router.register(r"orderlines", endpoints.PaidOrderLineViewSet)
router.register(r"orders", endpoints.PaidOrderViewSet)


urlpatterns = [
    path(
        "order/done/",
        TemplateView.as_view(template_name="order_done.html"),
        name="checkout_done",
    ),
    path(
        "order/address_select/",
        views.AddressSelectionView.as_view(),
        name="address_select",
    ),
    path("basket/", views.manage_basket, name="basket"),
    path(
        "add_to_basket/",
        views.add_to_basket,
        name="add_to_basket",
    ),
    path(
        "address/",
        views.AddressListView.as_view(),
        name="address_list",
    ),
    path(
        "address/create/",
        views.AddressCreateView.as_view(),
        name="address_create",
    ),
    path(
        "address/<int:pk>/",
        views.AddressUpdateView.as_view(),
        name="address_update",
    ),
    path(
        "address/<int:pk>/delete/",
        views.AddressDeleteView.as_view(),
        name="address_delete",
    ),
    path(
        "product/<slug:slug>/",
        DetailView.as_view(model=models.Product),
        name="product",
    ),
    path(
        "products/<slug:tag>/",
        views.ProductListView.as_view(),
        name="products",
    ),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="login.html",
            form_class=forms.AuthenticationForm,
        ),
        name="login",
    ),
    path(
        "logout/", auth_views.LogoutView.as_view(), name="logout"
    ),
    path(
        "contact-us/",
        views.ContactUsView.as_view(),
        name="contact_us",
    ),
    path(
        "about-us/",
        TemplateView.as_view(template_name="about_us.html"),
        name="about_us",
    ),
    path(
        "",
        TemplateView.as_view(template_name="home.html"),
        name="home",
    ),
    path(
        "order-dashboard/",
        views.OrderView.as_view(),
        name="order_dashboard",
    ),
    path("api/", include(router.urls)),
    path("admin/", admin.main_admin.urls),
    path("office-admin/", admin.central_office_admin.urls),
    path("dispatch-admin/", admin.dispatchers_admin.urls),
    path(
        "customer-service/",
        TemplateView.as_view(
            template_name="customer_service.html"
        ),
        name="cs_main",
    ),
    path(
        "customer-service/<int:order_id>/",
        views.room,
        name="cs_chat",
    ),
    path(
        "mobile-api/auth/",
        authtoken_views.obtain_auth_token,
        name="mobile_token",
    ),
    path(
        "mobile-api/my-orders/",
        endpoints.my_orders,
        name="mobile_my_orders",
    ),
]
