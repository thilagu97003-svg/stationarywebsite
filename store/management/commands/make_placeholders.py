import hashlib

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from store.seed_data import all_images


class Command(BaseCommand):
    help = "Create temporary placeholder images for every missing file. Replace them with the Figma assets (same file names)."

    def handle(self, *args, **options):
        root = settings.BASE_DIR / "static" / "images"
        font = ImageFont.load_default(size=34)
        created = 0
        for rel in all_images():
            path = root / rel
            if path.exists():
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.md5(rel.encode()).digest()
            colour = tuple(150 + digest[i] % 90 for i in range(3))
            size = (400, 400) if rel == "logo.png" else (800, 600)
            img = Image.new("RGB", size, colour)
            draw = ImageDraw.Draw(img)
            label = rel.rsplit("/", 1)[-1]
            box = draw.textbbox((0, 0), label, font=font)
            draw.text(((size[0] - box[2]) / 2, (size[1] - box[3]) / 2), label, fill=(40, 40, 40), font=font)
            img.save(path, "PNG" if rel.endswith(".png") else "JPEG", quality=85)
            created += 1
        self.stdout.write(self.style.SUCCESS(f"{created} placeholder images created in static/images/"))
