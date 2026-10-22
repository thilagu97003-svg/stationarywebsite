from PIL import Image
import shutil

p = "static/images/home/notepad-pen.png"
shutil.copy(p, p + ".bak")          # backup

im = Image.open(p).convert("RGBA")
box = im.split()[3].getbbox()       # transparent illatha area mattum
im = im.crop(box)
im.thumbnail((800, 1400))           # file size kuraiya
im.save(p, optimize=True)
print("done:", im.size)