from .cart import Cart
from .models import Category


def shop_globals(request):
    """Values every template needs: cart badge + category list for the Shop sidebar."""
    return {"cart_count": len(Cart(request)), "nav_categories": Category.objects.all()}
