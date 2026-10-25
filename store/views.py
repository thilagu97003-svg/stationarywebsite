import re
import secrets
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from urllib.parse import urlencode
from django.urls import reverse

from .cart import Cart
from .forms import SigninForm, RegisterForm, CheckoutForm, ContactForm, ReviewForm
from .models import Category, Order, OrderItem, Product, Review
from .templatetags.store_extras import money

OTP_VALID_SECONDS = 300
TEAM = [("team-1.jpg", "Shop Owner"), ("team-2.jpg", "Manager"), ("team-3.jpg", "Shop Keeper")]


# ---------------------------------------------------------------- public pages
FEATURED_ORDER = ["Scientific Calculator", "Geometry Box", "Desk Organiser Set"]
SCHOOL_ORDER = ["Colour Pencils", "Ruled Notebook", "Spiral Planner"]

PRICE_RANGES = [("50-100", 50, 100), ("100-200", 100, 200), ("200-300", 200, 300), ("300-500", 300, 500)]

# category slug -> hero image (inside static/images/). Missing files fall back to shop/hero.jpg in the template.
HERO_IMAGES = {
    "office-basics": "shop/hero.jpg",                 # first category, ippo irukkura hero apdiye
    "files-folders": "products/files-multi.jpg",      # temporary (keela paaru)
    "papers-notebook": "shop/banner-notebooks.jpg",
    "pen-writings": "shop/banner-pens.jpg",
    "school-supplies": "shop/banner-school.jpg",
}


def _ordered(flag, names):
    items = Product.objects.filter(**{flag: True})
    return sorted(items, key=lambda p: names.index(p.name) if p.name in names else 99)[:3]


def home(request):
    return render(request, "store/home.html", {
        "featured": _ordered("is_featured", FEATURED_ORDER),
        "school": _ordered("is_back_to_school", SCHOOL_ORDER),
        "team": TEAM,
    })


def about(request):
    return render(request, "store/about.html", {"team": TEAM})


def shop(request, slug=None):
    query = request.GET.get("q", "").strip()
    category = None

    if query:
        products = Product.objects.filter(Q(name__icontains=query) | Q(category__name__icontains=query))
        title = f"Results for \u201c{query}\u201d"
    else:
        category = get_object_or_404(Category, slug=slug) if slug else Category.objects.first()
        products = category.products.all() if category else Product.objects.none()
        title = category.name if category else "Shop"

    # Price filter (multiple checkboxes = OR)
    selected = request.GET.getlist("price")
    price_q = Q()
    for key, lo, hi in PRICE_RANGES:
        if key in selected:
            price_q |= Q(price__gte=lo, price__lte=hi)
    if price_q:
        products = products.filter(price_q)

    params = request.GET.copy()
    params.pop("page", None)

    page = Paginator(products, 12).get_page(request.GET.get("page"))
    hero = HERO_IMAGES.get(category.slug, "shop/hero.jpg") if category else "shop/hero.jpg"

    return render(request, "store/shop.html", {
        "page": page,
        "category": category,
        "title": title,
        "query": query,
        "hero": hero,
        "price_ranges": [
            {"key": k, "label": f"Rs. {lo}-{hi}", "checked": k in selected}
            for k, lo, hi in PRICE_RANGES
        ],
        "qs": params.urlencode(),
    })


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Thanks! Your message has been sent. We will get back to you soon.")
        return redirect("contact")
    return render(request, "store/contact.html", {"form": form})


# ------------------------------------------------------------------------ auth
def _safe_next(request):
    target = request.POST.get("next") or request.GET.get("next") or ""
    ok = url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()})
    return target if ok else ""


def _auth_page(request, mode, form=None):
    if form is None:
        form = SigninForm(auto_id="login_%s") if mode == "signin" else RegisterForm(auto_id="reg_%s")
    return render(request, "store/auth.html", {"mode": mode, "form": form, "next": _safe_next(request)})


def auth_view(request):
    """Login/Register + profile icon land here: Create Account form first."""
    if request.user.is_authenticated:
        return redirect(_safe_next(request) or "home")
    return _auth_page(request, "signup")


def signin_view(request):
    if request.user.is_authenticated:
        return redirect(_safe_next(request) or "home")
    form = None
    if request.method == "POST":
        form = SigninForm(request.POST, auto_id="login_%s")
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data["username"],
                                password=form.cleaned_data["password"])
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect(_safe_next(request) or "home")
            form.add_error(None, "Invalid username or password.")
    return _auth_page(request, "signin", form)


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = None
    if request.method == "POST":
        form = RegisterForm(request.POST, auto_id="reg_%s")
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Account created successfully! Please sign in to continue.")
            nxt = _safe_next(request)
            url = reverse("signin") + (f"?{urlencode({'next': nxt})}" if nxt else "")
            return redirect(url)
    return _auth_page(request, "signup", form)


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect("home")


# ------------------------------------------------------------------------ cart
def cart_view(request):
    cart = Cart(request)
    return render(request, "store/cart.html", {"rows": cart.items(), "total": cart.total()})


def cart_add(request, pid):
    product = get_object_or_404(Product, pk=pid)
    cart = Cart(request)

    # Cart class signature maariyirundhaalum work aaga
    try:
        cart.add(pid)
    except TypeError:
        try:
            cart.add(pid, 1)
        except TypeError:
            cart.add(product)

    # Product cards (AJAX POST) -> JSON for badge + toast
    if request.method == "POST":
        return JsonResponse({"ok": True, "count": len(cart), "message": f"{product.name} added to cart"})

    # Normal link click (product detail page) -> redirect back
    messages.success(request, f"{product.name} added to cart!")
    return redirect(request.META.get("HTTP_REFERER", "cart"))


@require_POST
def cart_update(request, pid):
    get_object_or_404(Product, pk=pid)
    try:
        qty = int(request.POST.get("qty", ""))
    except ValueError:
        return JsonResponse({"ok": False}, status=400)
    cart = Cart(request)
    cart.set(pid, qty)
    row = next((r for r in cart.items() if r["product"].pk == pid), None)
    return JsonResponse({
        "ok": True,
        "count": len(cart),
        "qty": row["qty"] if row else 0,
        "unit_price": money(row["unit_price"]) if row else "0",
        "line_total": money(row["line_total"]) if row else "0",
        "total": money(cart.total()),
    })


# -------------------------------------------------------------------- checkout
@login_required(login_url="/login/")
def checkout(request):
    pid = request.GET.get("pid") or request.POST.get("pid")
    cart = Cart(request)

    if pid:
        # Single Product Direct Buy Flow (Cart-la irukka theva illa)
        cart_row = next((r for r in cart.items() if str(r["product"].pk) == str(pid)), None)
        if cart_row:
            row = cart_row
        else:
            product = get_object_or_404(Product, pk=pid)
            row = {
                "product": product,
                "qty": 1,
                "unit_price": product.price,
                "line_total": product.price,
            }
        checkout_items = [row]
        total_amount = row["line_total"]
    else:
        # Full Cart Checkout Flow
        checkout_items = cart.items()
        total_amount = cart.total()

    if not checkout_items:
        messages.info(request, "Your cart is empty. Add something first.")
        return redirect("cart")

    form = CheckoutForm(
        request.POST or None,
        initial={
            "name": request.user.first_name or request.user.username,
            "payment_method": "cod",
        },
    )

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            order = form.save(commit=False)
            order.user = request.user
            order.total = total_amount
            order.save()

            for r in checkout_items:
                OrderItem.objects.create(
                    order=order,
                    product=r["product"],
                    qty=r["qty"],
                    unit_price=r["unit_price"],
                    line_total=r["line_total"],
                )

            # Order complete aana udane cart update
            if pid:
                cart.set(pid, 0)
            else:
                cart.clear()

            messages.success(request, f"Order #{order.order_id} placed successfully!")
            return redirect(f"/orders/{order.order_id}/?confirmed=1")

    return render(
        request,
        "store/checkout.html",
        {
            "form": form,
            "rows": checkout_items,
            "total": total_amount,
            "is_single": bool(pid),
            "pid": pid or "",
        },
    )


@login_required
def my_orders(request):
    orders = request.user.orders.filter(is_deleted_by_user=False).prefetch_related("items__product")
    return render(request, "store/orders.html", {"orders": orders})

@login_required
def delete_order_history(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    if order.status.lower() in ['delivered', 'completed']:
        order.is_deleted_by_user = True
        order.save()
        messages.success(request, f"Order #{order.order_id} removed from your history.")
    return redirect("orders")  # unga urls.py-la name='orders' nu irukku
@login_required
def tracking(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), order_id=order_id, user=request.user)
    return render(request, "store/tracking.html", {"order": order})

@login_required
def review(request, item_id):
    item = get_object_or_404(OrderItem.objects.select_related("product", "order"), pk=item_id, order__user=request.user)
    existing = Review.objects.filter(product=item.product, user=request.user).first()
    form = ReviewForm(request.POST or None, initial={"rating": existing.rating, "comment": existing.comment} if existing else None)
    if request.method == "POST" and form.is_valid():
        Review.objects.update_or_create(
            product=item.product, user=request.user,
            defaults={"rating": int(form.cleaned_data["rating"]), "comment": form.cleaned_data["comment"]})
        messages.success(request, "Thanks for your review!")
        return redirect("orders")
    return render(request, "store/review.html", {"form": form, "item": item})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Related products from same category
    related_products = Product.objects.filter(category=product.category).exclude(pk=pk)[:4]
    return render(request, "store/product_detail.html", {
        "product": product,
        "related_products": related_products,
    })


def mark_order_delivered(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order.status = "delivered"  # or 'completed' as per your model status choices
    order.save()
    return JsonResponse({"status": "success"})


@login_required
def order_invoice(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, "store/invoice.html", {"order": order})

def legal_view(request, page_type):
    titles = {
        "terms": "Terms & Conditions",
        "cookie-policy": "Cookie Policy",
        "privacy-policy": "Privacy Policy",
    }
    title = titles.get(page_type, "Legal Information")
    return render(request, "store/legal.html", {"title": title, "page_type": page_type})