import random
import string
from datetime import timedelta
from django.utils import timezone

from django.conf import settings
from django.db import models
from django.db.models import Avg
from django.utils.timezone import localtime


class Category(models.Model):
    name = models.CharField(max_length=60)
    slug = models.SlugField(unique=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=120)
    image = models.CharField(max_length=200, help_text="Path inside static/images/, e.g. products/pens.jpg")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=50)
    bulk_qty = models.PositiveSmallIntegerField(default=3, help_text="Minimum quantity for the bulk price")
    bulk_price = models.DecimalField(max_digits=8, decimal_places=2, default=41.20, help_text="Per-item price on bulk orders")
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5)
    is_featured = models.BooleanField(default=False)
    is_back_to_school = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name

    def unit_price_for(self, qty):
        return self.bulk_price if qty >= self.bulk_qty else self.price

    @property
    def stars(self):
        return int(round(self.rating))


class Order(models.Model):
    PAYMENT_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("upi", "UPI"),
        ("debit", "Debit Card"),
        ("netbanking", "Net Banking"),
        ("credit", "Credit Card"),

    ]
    STATUS_FLOW = ["confirmed", "shipped", "out_for_delivery", "delivered"]
    STATUS_CHOICES = [(s, s.replace("_", " ").title()) for s in STATUS_FLOW]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    order_id = models.CharField(max_length=12, unique=True, editable=False)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=80)
    postal_code = models.CharField(max_length=7)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="cod")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="confirmed")
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_id

    def save(self, *args, **kwargs):
        if not self.order_id:
            while True:
                oid = "OD" + "".join(random.choices(string.digits, k=9))
                if not Order.objects.filter(order_id=oid).exists():
                    break
            self.order_id = oid
        super().save(*args, **kwargs)

    @property
    def expected_delivery(self):
        return localtime(self.created_at) + timedelta(days=4)

    @property
    def steps(self):
        """Timeline rows for the tracking page."""
        done_upto = self.STATUS_FLOW.index(self.status)
        placed = localtime(self.created_at).strftime("%b %d").replace(" 0", " ")
        due = self.expected_delivery.strftime("%b %d").replace(" 0", " ")
        labels = [f"Order Confirmed, {placed}", "Shipped", "Out for Delivery", f"Delivery, {due} by 11 PM"]
        return [{"label": l, "done": i <= done_upto} for i, l in enumerate(labels)]

    @property
    def estimated_delivery_date(self):
        # created_at base panni 3 days kazhichu delivery date kaatta
        if hasattr(self, 'created_at') and self.created_at:
            return (self.created_at + timedelta(days=3)).strftime("%d %B, %Y")
        return "3 Days from order"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product} x {self.qty}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "user")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        avg = self.product.reviews.aggregate(a=Avg("rating"))["a"] or 5
        Product.objects.filter(pk=self.product_id).update(rating=round(avg, 1))


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.created_at:%d %b %Y})"
