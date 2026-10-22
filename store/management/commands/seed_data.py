from decimal import Decimal

from django.core.management.base import BaseCommand

from store.models import Category, Product
from store.seed_data import BACK_TO_SCHOOL, CATEGORIES, FEATURED, VARIANTS

# 12 prices per category, spread across the 4 filter ranges
# (50-100, 100-200, 200-300, 300-500). Avoids exact 100/200/300 so each
# product falls in only one range.
PRICES = [60, 85, 95, 120, 150, 185, 220, 250, 280, 320, 380, 450]
BULK_RATIO = Decimal("0.824")   # same discount as the old 50 -> 41.20


class Command(BaseCommand):
    help = "Load categories and demo products (safe to run many times)."

    def handle(self, *args, **options):
        for position, (cat_name, slug, items) in enumerate(CATEGORIES):
            category, _ = Category.objects.update_or_create(slug=slug, defaults={"name": cat_name, "order": position})
            for i in range(12):
                base, image = items[i % len(items)]
                variant = VARIANTS[i // len(items)]
                name = f"{base} {variant}".strip()
                price = Decimal(PRICES[i])
                bulk_price = (price * BULK_RATIO).quantize(Decimal("0.01"))
                Product.objects.update_or_create(category=category, name=name, defaults={
                    "image": image, "price": price, "bulk_qty": 3, "bulk_price": bulk_price,
                    "is_featured": variant == "" and base in FEATURED,
                    "is_back_to_school": variant == "" and base in BACK_TO_SCHOOL,
                })
        self.stdout.write(self.style.SUCCESS(f"{Category.objects.count()} categories, {Product.objects.count()} products ready."))