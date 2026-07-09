from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Save files into the same folder as this script
out_dir = Path(__file__).resolve().parent / "assets"
out_dir.mkdir(parents=True, exist_ok=True)

svg = """<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" role="img" aria-label="SP monogram logo">
  <rect width="512" height="512" rx="112" fill="#F8FAFC"/>
  <circle cx="256" cy="256" r="174" fill="none" stroke="#2563EB" stroke-width="24"/>
  <text x="256" y="294" text-anchor="middle"
        font-family="Space Grotesk, Inter, Arial, sans-serif"
        font-size="148" font-weight="700" letter-spacing="-8"
        fill="#0F172A">SP</text>
  <circle cx="386" cy="126" r="18" fill="#14B8A6"/>
</svg>
"""

svg_path = out_dir / "shyam_popat_sp_monogram_favicon.svg"
svg_path.write_text(svg, encoding="utf-8")

img = Image.new("RGBA", (512, 512), "#F8FAFC")
draw = ImageDraw.Draw(img)

draw.rounded_rectangle((0, 0, 511, 511), radius=112, fill="#F8FAFC")
draw.ellipse((82, 82, 430, 430), outline="#2563EB", width=24)

try:
    font = ImageFont.truetype("arial.ttf", 148)
except OSError:
    font = ImageFont.load_default()

text = "SP"
bbox = draw.textbbox((0, 0), text, font=font)
x = (512 - (bbox[2] - bbox[0])) / 2
y = 176

draw.text((x, y), text, font=font, fill="#0F172A")
draw.ellipse((368, 108, 404, 144), fill="#14B8A6")

png_path = out_dir / "shyam_popat_sp_monogram_favicon.png"
img.save(png_path)

md = """# Decide Once: Build Your Identity Kit

## Portfolio identity kit

### Fonts

**Heading font:** Space Grotesk  
**Body font:** Inter  

Both fonts are free Google Fonts. Space Grotesk gives the portfolio a modern technical feel, while Inter keeps the body text clean, readable, and professional.

### Palette

| Role | Colour | Hex code |
|---|---|---|
| Main colour | Engineering blue | `#2563EB` |
| Near-black text | Slate black | `#0F172A` |
| Near-white background | Soft white | `#F8FAFC` |
| Accent colour | Calm teal | `#14B8A6` |

### Logo / favicon

The logo is a simple **SP monogram** using the heading font style. It uses a blue technical ring, near-black initials, and a small teal accent dot to suggest AI/system signals without making the logo too busy.

### Two-line style note for Claude Project

Use **Space Grotesk** for headings and **Inter** for body text. Palette: `#2563EB` main blue, `#0F172A` text, `#F8FAFC` background, and `#14B8A6` as the only accent.

The mood should feel calm, technical, reliable, and modern, letting the backend and AI project proof stand out instead of competing with decorative design.
"""

md_path = out_dir / "flyrank_week3_identity_kit.md"
md_path.write_text(md, encoding="utf-8")

print("Created files:")
print(svg_path)
print(png_path)
print(md_path)