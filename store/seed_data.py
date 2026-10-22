"""Demo catalogue + the list of every image the templates expect (relative to static/images/)."""

# (category name, slug, [(product name, image file), ...]) - each category is filled to 12 products
CATEGORIES = [
    ("Office Basics", "office-basics", [
            ("Scientific Calculator", "products/calculator.jpg"),
            ("Heavy Duty Stapler", "products/stapler.jpg"),
            ("Desk Organiser Set", "products/desk-set.jpg"),
            ("Pen Collection", "products/pens.jpg"),
            ("Craft Scissors", "products/scissors.jpg"),
            ("Highlighter Set", "products/highlighters.jpg"),
        ]),
    ("Files & Folders", "files-folders", [
        ("Office File Set", "products/files-green.jpg"),
        ("Box File Red", "products/files-red.jpg"),
        ("Colour Lever Files", "products/files-colour.jpg"),
        ("Rainbow Folders", "products/files-multi.jpg"),
    ]),
    ("Papers & Notebook", "papers-notebook", [
        ("Ruled Notebook", "products/notebook-blue.jpg"),
        ("Desk Stationery Set", "products/notebook-stapler.jpg"),
        ("Drawing Paper", "products/paper-desk.jpg"),
        ("Spiral Planner", "products/notebook-peach.jpg"),
    ]),
    ("Pen & Writings", "pen-writings", [
        ("Ball Pen Set", "products/pens.jpg"),
        ("Colour Pencils", "products/pencils.jpg"),
        ("Spiral Notepad", "products/notepad-spiral.jpg"),
        ("Neon Spiral Notebook", "products/notebook-neon.jpg"),
    ]),
    ("School Supplies", "school-supplies", [
        ("Ruler & Pen Kit", "products/ruler-kit.jpg"),
        ("Pencil Cup", "products/pencil-cup.jpg"),
        ("Sticky Notes Set", "products/sticky-set.jpg"),
        ("Craft Ruler Kit", "products/ruler-blue.jpg"),
        ("Geometry Box", "products/geometry-box.jpg"),
    ]),
    
]
VARIANTS = ["", "Premium", "Bulk Pack", "Deluxe"]
FEATURED = {"Scientific Calculator", "Geometry Box", "Desk Organiser Set"}
BACK_TO_SCHOOL = {"Colour Pencils", "Ruled Notebook", "Spiral Planner"}

PAGE_IMAGES = [
    "logo.png",
    "home/hero-notebook.jpg", "home/backpack.png", "home/highlighters.jpg",
    "home/essential-1.jpg", "home/essential-2.jpg", "home/essential-3.jpg", "home/notepad-pen.png",
    "home/trending-1.jpg", "home/trending-2.jpg", "home/trending-3.jpg",
    "home/trending-4.jpg", "home/trending-5.jpg", "home/trending-6.jpg",
    "home/testimonial.jpg", "team/team-1.jpg", "team/team-2.jpg", "team/team-3.jpg",
    "about/hero.jpg", "about/intro-1.jpg", "about/intro-2.jpg", "about/intro-3.jpg", "about/pens.png", "about/pencils.png", "about/bag-1.png", "about/bag-2.png",
    "about/notepad.png", "about/sticky.png", "about/stapler.png",
    "shop/hero.jpg", "contact/hero.jpg", "contact/map.jpg", "auth/hero.jpg", "orders/banner.jpg",
]


def all_images():
    product_images = {img for _, _, items in CATEGORIES for _, img in items}
    return PAGE_IMAGES + sorted(product_images)
