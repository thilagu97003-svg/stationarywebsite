from decimal import Decimal

from .models import Product


class Cart:
    """Session-backed cart: {product_id: quantity}. Works for guests; checkout needs login."""

    KEY = "cart"

    def __init__(self, request):
        self.session = request.session
        self.data = self.session.get(self.KEY, {})

    def _save(self):
        self.session[self.KEY] = self.data
        self.session.modified = True

    def add(self, pid, qty=1):
        pid = str(pid)
        self.data[pid] = min(self.data.get(pid, 0) + qty, 999)
        self._save()

    def set(self, pid, qty):
        pid = str(pid)
        if qty <= 0:
            self.data.pop(pid, None)
        else:
            self.data[pid] = min(qty, 999)
        self._save()

    def clear(self):
        self.data = {}
        self._save()

    def __len__(self):
        return sum(self.data.values())

    def items(self):
        products = Product.objects.in_bulk([int(k) for k in self.data])
        rows = []
        for key, qty in self.data.items():
            product = products.get(int(key))
            if product:
                unit = product.unit_price_for(qty)
                rows.append({"product": product, "qty": qty, "unit_price": unit, "line_total": unit * qty})
        return rows

    def total(self):
        return sum((r["line_total"] for r in self.items()), Decimal("0"))
