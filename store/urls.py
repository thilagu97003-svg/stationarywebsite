from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import StyledPasswordResetForm, StyledSetPasswordForm

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.shop, name="shop"),
    path("shop/<slug:slug>/", views.shop, name="shop_category"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.auth_view, name="auth"),
    path("signin/", views.signin_view, name="signin"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path('orders/delete/<str:order_id>/', views.delete_order_history, name='delete_order_history'),

    # Forgot password
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="store/password_reset.html",
        form_class=StyledPasswordResetForm,
        email_template_name="store/emails/password_reset_email.txt",
        subject_template_name="store/emails/password_reset_subject.txt",
        success_url=reverse_lazy("password_reset_done"),
    ), name="password_reset"),
    path("password-reset/sent/", auth_views.PasswordResetDoneView.as_view(
        template_name="store/password_reset_done.html",
    ), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="store/password_reset_confirm.html",
        form_class=StyledSetPasswordForm,
        success_url=reverse_lazy("password_reset_complete"),
    ), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="store/password_reset_complete.html",
    ), name="password_reset_complete"),

    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:pid>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:pid>/", views.cart_update, name="cart_update"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.my_orders, name="orders"),
    path("orders/<str:order_id>/", views.tracking, name="tracking"),
    path("orders/<str:order_id>/mark-delivered/", views.mark_order_delivered, name="mark_order_delivered"),
    path("orders/<str:order_id>/invoice/", views.order_invoice, name="order_invoice"),
    path("review/<int:item_id>/", views.review, name="review"),
    path("legal/<str:page_type>/", views.legal_view, name="legal_page"),
]