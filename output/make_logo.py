from PIL import Image, ImageDraw, ImageFont
import math

SIZE = 500
img = Image.new("RGB", (SIZE, SIZE), (13, 17, 23))  # GitHub dark background
draw = ImageDraw.Draw(img)

# Gradient tło - okrąg z efektem chmury/kodu
for r in range(220, 0, -1):
    alpha = int(255 * (1 - r / 220))
    color = (
        int(30 + (88 - 30) * (1 - r / 220)),
        int(17 + (166 - 17) * (1 - r / 220)),
        int(23 + (255 - 23) * (1 - r / 220)),
    )
    draw.ellipse([SIZE//2 - r, SIZE//2 - r, SIZE//2 + r, SIZE//2 + r], fill=color)

# Ikona chmury (uproszczona)
cx, cy = SIZE // 2, SIZE // 2 - 40
cloud_color = (200, 230, 255)

# chmura = kilka kół połączonych
draw.ellipse([cx - 80, cy - 30, cx + 80, cy + 50], fill=cloud_color)
draw.ellipse([cx - 110, cy, cx - 20, cy + 60], fill=cloud_color)
draw.ellipse([cx + 20, cy - 10, cx + 110, cy + 60], fill=cloud_color)
draw.ellipse([cx - 50, cy - 60, cx + 50, cy + 10], fill=cloud_color)
draw.rectangle([cx - 100, cy + 20, cx + 100, cy + 60], fill=cloud_color)

# Strzałka w dół (upload/download symbol)
arrow_color = (13, 110, 253)
draw.polygon([
    (cx, cy + 30),
    (cx - 20, cy + 10),
    (cx + 20, cy + 10),
], fill=arrow_color)
draw.rectangle([cx - 8, cy - 10, cx + 8, cy + 15], fill=arrow_color)

# Nawiasy kodowe po bokach
bracket_color = (88, 166, 255)
font_bracket = None
for path in [
    "/System/Library/Fonts/Menlo.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "C:/Windows/Fonts/consola.ttf",
]:
    try:
        font_bracket = ImageFont.truetype(path, 52)
        break
    except:
        continue
if font_bracket is None:
    font_bracket = ImageFont.load_default()

draw.text((60, SIZE // 2 - 30), "<", font=font_bracket, fill=bracket_color)
draw.text((SIZE - 95, SIZE // 2 - 30), ">", font=font_bracket, fill=bracket_color)

# Nazwa YAKOBE
font_name = None
for path in [
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]:
    try:
        font_name = ImageFont.truetype(path, 72)
        break
    except:
        continue
if font_name is None:
    font_name = ImageFont.load_default()

text = "YAKOBE"
bbox = draw.textbbox((0, 0), text, font=font_name)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
tx = (SIZE - tw) // 2
ty = SIZE // 2 + 90

# Cień
draw.text((tx + 3, ty + 3), text, font=font_name, fill=(0, 0, 0))
# Tekst z gradientem (dwie warstwy)
draw.text((tx, ty), text, font=font_name, fill=(88, 166, 255))

# Podtytuł
font_sub = None
for path in [
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:/Windows/Fonts/arial.ttf",
]:
    try:
        font_sub = ImageFont.truetype(path, 22)
        break
    except:
        continue
if font_sub is None:
    font_sub = ImageFont.load_default()

sub = "code · cloud · create"
bbox2 = draw.textbbox((0, 0), sub, font=font_sub)
sw = bbox2[2] - bbox2[0]
draw.text(((SIZE - sw) // 2, ty + th + 10), sub, font=font_sub, fill=(100, 140, 180))

img.save("/Users/test/Desktop/CloudCode/Dealavo tool/output/yakobe_logo.png")
print("Logo zapisane: output/yakobe_logo.png")
