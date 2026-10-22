import re

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Order, Product


class ShopFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_data", verbosity=0)

    def test_public_pages_load(self):
        for name in ["home", "shop", "about", "contact", "auth", "cart"]:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_protected_pages_redirect_to_login(self):
        for name in ["checkout", "orders"]:
            self.assertEqual(self.client.get(reverse(name)).status_code, 302, name)

    def test_bulk_price_applies_from_bulk_quantity(self):
        product = Product.objects.first()
        self.assertEqual(product.unit_price_for(1), product.price)
        self.assertEqual(product.unit_price_for(product.bulk_qty), product.bulk_price)

    def test_cart_add_and_update(self):
        pid = Product.objects.first().pk
        self.assertEqual(self.client.post(reverse("cart_add", args=[pid])).json()["count"], 1)
        data = self.client.post(reverse("cart_update", args=[pid]), {"qty": 10}).json()
        self.assertEqual(data["qty"], 10)
        self.assertEqual(data["line_total"], "412")  # 10 x 41.20 bulk price

    def test_login_checkout_and_tracking(self):
        pid = Product.objects.first().pk
        self.client.post(reverse("cart_add", args=[pid]))
        message = self.client.post(reverse("send_otp"), {"phone": "9876543210"}).json()["message"]
        otp = re.search(r"\d{6}", message).group()
        login = self.client.post(reverse("auth"), {
            "name": "Test User", "email": "t@example.com", "phone": "9876543210", "otp": otp})
        self.assertEqual(login.status_code, 302)
        order_resp = self.client.post(reverse("checkout"), {
            "name": "Test User", "address": "1 Main Rd", "city": "Coimbatore",
            "postal_code": "641 402", "payment_method": "cod"})
        self.assertEqual(order_resp.status_code, 302)
        order = Order.objects.get(user=get_user_model().objects.get(username="9876543210"))
        self.assertEqual(self.client.get(reverse("tracking", args=[order.order_id])).status_code, 200)

    def test_wrong_otp_rejected(self):
        self.client.post(reverse("send_otp"), {"phone": "9876543210"})
        resp = self.client.post(reverse("auth"), {
            "name": "T", "email": "t@example.com", "phone": "9876543210", "otp": "000000"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Invalid or expired OTP")
