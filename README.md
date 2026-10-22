# Supplyhive - Stationery Shop (Django)

Responsive e-commerce layout built from the Figma prototype.
Font: Roboto | Colors: `#097AFA` `#7AABF5` `#D3DFF8`

## Run locally
```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py make_placeholders   # temporary images; skip once Figma assets are in static/images/
python manage.py seed_data           # 5 categories x 12 products
python manage.py createsuperuser     # optional, for /admin/
python manage.py runserver
```
Open http://127.0.0.1:8000/

## Run the automated tests
```bash
python manage.py test
```

## Pages -> URLs
| Figma page | URL | View / template |
|---|---|---|
| Home | `/` | `home` / `home.html` |
| Shop (5 categories) | `/shop/`, `/shop/<slug>/`, `/shop/?q=pen` | `shop` / `shop.html` |
| About us | `/about/` | `about` / `about.html` |
| Contact | `/contact/` | `contact` / `contact.html` |
| Sign in | `/login/` | `auth_view` / `auth.html` |
| My Cart | `/cart/` | `cart_view` / `cart.html` |
| Billing | `/checkout/` | `checkout` / `checkout.html` |
| My Order | `/orders/` | `my_orders` / `orders.html` |
| Tracking | `/orders/<OD id>/` | `tracking` / `tracking.html` |
| Rate & Review | `/review/<item id>/` | `review` / `review.html` |

## Features
- Session cart (add via AJAX, +/- quantity, bulk price when qty >= bulk quantity)
- OTP sign-in (demo OTP shown on screen; plug an SMS provider into `views.send_otp`)
- Billing form with validation, payment options, order creation
- Order tracking timeline - change an order's status in `/admin/` to move it forward
- Contact form saved to the database, product search, category off-canvas menu, reviews

## Images
Images in `static/images/` were cropped from the Figma page screenshots (good for layout). For sharper quality replace them with the original Figma exports, keeping the same file names
(full list: `store/seed_data.py`).

## Deploy on Render
1. Push to GitHub. 2. Render -> New -> Blueprint (reads `render.yaml`) or New Web Service:
   build `./build.sh`, start `gunicorn stationery_shop.wsgi:application`.
3. Env vars: `SECRET_KEY`, `DEBUG=False`, `SHOW_DEMO_OTP=True`.
