import os
from PIL import Image, ImageDraw, ImageFont
import io

# Create a simple icon
img_size = 512
img = Image.new('RGBA', (img_size, img_size), color=(0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw background circle
circle_color = (44, 62, 80)  # Dark blue
draw.ellipse((0, 0, img_size, img_size), fill=circle_color)

# Draw "P" in the center
try:
    # Try to use a system font
    font = ImageFont.truetype("Arial Bold.ttf", int(img_size * 0.6))
except:
    # Fallback to default
    font = ImageFont.load_default()

text = "P"
text_color = (255, 255, 255)  # White
text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else font.getsize(text)
position = ((img_size - text_width) / 2, (img_size - text_height) / 2 - img_size * 0.05)

draw.text(position, text, font=font, fill=text_color)

# Save icon to file
icon_path = "/Users/syedhazeena/Desktop/rag/patent_assistant_icon.png"
img.save(icon_path)

print(f"Icon saved to: {icon_path}")
