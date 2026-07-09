from pathlib import Path

out_dir = Path(__file__).resolve().parent
out_dir.mkdir(parents=True, exist_ok=True)

palette = {
    "blue": "#2563EB",
    "black": "#0F172A",
    "bg": "#F8FAFC",
    "teal": "#14B8A6",
    "line": "#CBD5E1"
}

hero_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" role="img" aria-label="Abstract technical hero texture">
  <rect width="1600" height="900" fill="{palette['bg']}"/>
  <defs>
    <pattern id="grid" width="64" height="64" patternUnits="userSpaceOnUse">
      <path d="M 64 0 L 0 0 0 64" fill="none" stroke="{palette['line']}" stroke-width="1" opacity="0.45"/>
    </pattern>
    <radialGradient id="glow" cx="50%" cy="45%" r="60%">
      <stop offset="0%" stop-color="{palette['blue']}" stop-opacity="0.16"/>
      <stop offset="45%" stop-color="{palette['teal']}" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="{palette['bg']}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1600" height="900" fill="url(#grid)"/>
  <rect width="1600" height="900" fill="url(#glow)"/>
  <path d="M250 620 C420 470 580 710 760 540 C930 380 1090 500 1320 300" fill="none" stroke="{palette['blue']}" stroke-width="8" stroke-linecap="round" opacity="0.55"/>
  <path d="M330 360 C510 270 680 430 850 300 C1020 175 1190 245 1360 170" fill="none" stroke="{palette['teal']}" stroke-width="6" stroke-linecap="round" opacity="0.45"/>
  <circle cx="250" cy="620" r="14" fill="{palette['blue']}"/>
  <circle cx="760" cy="540" r="14" fill="{palette['blue']}"/>
  <circle cx="1320" cy="300" r="14" fill="{palette['blue']}"/>
  <circle cx="330" cy="360" r="11" fill="{palette['teal']}"/>
  <circle cx="850" cy="300" r="11" fill="{palette['teal']}"/>
  <circle cx="1360" cy="170" r="11" fill="{palette['teal']}"/>
  <text x="110" y="790" font-family="Inter, Arial, sans-serif" font-size="34" fill="{palette['black']}" opacity="0.55">reliable backend + AI systems</text>
</svg>"""

backend_icon = f"""<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" role="img" aria-label="Backend systems icon">
  <rect width="512" height="512" rx="96" fill="{palette['bg']}"/>
  <rect x="118" y="128" width="276" height="78" rx="20" fill="none" stroke="{palette['blue']}" stroke-width="22"/>
  <rect x="118" y="230" width="276" height="78" rx="20" fill="none" stroke="{palette['black']}" stroke-width="22" opacity="0.9"/>
  <rect x="118" y="332" width="276" height="78" rx="20" fill="none" stroke="{palette['teal']}" stroke-width="22"/>
  <circle cx="168" cy="167" r="12" fill="{palette['blue']}"/>
  <circle cx="168" cy="269" r="12" fill="{palette['black']}"/>
  <circle cx="168" cy="371" r="12" fill="{palette['teal']}"/>
</svg>"""

ai_validation_icon = f"""<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" role="img" aria-label="AI validation icon">
  <rect width="512" height="512" rx="96" fill="{palette['bg']}"/>
  <circle cx="256" cy="220" r="104" fill="none" stroke="{palette['blue']}" stroke-width="22"/>
  <path d="M203 220 L241 258 L315 176" fill="none" stroke="{palette['teal']}" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M154 372 H358" stroke="{palette['black']}" stroke-width="20" stroke-linecap="round" opacity="0.88"/>
  <path d="M190 412 H322" stroke="{palette['black']}" stroke-width="16" stroke-linecap="round" opacity="0.55"/>
</svg>"""

architecture_icon = f"""<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" role="img" aria-label="Architecture flow icon">
  <rect width="512" height="512" rx="96" fill="{palette['bg']}"/>
  <rect x="84" y="132" width="116" height="82" rx="18" fill="none" stroke="{palette['blue']}" stroke-width="18"/>
  <rect x="312" y="132" width="116" height="82" rx="18" fill="none" stroke="{palette['teal']}" stroke-width="18"/>
  <rect x="84" y="306" width="116" height="82" rx="18" fill="none" stroke="{palette['black']}" stroke-width="18" opacity="0.85"/>
  <rect x="312" y="306" width="116" height="82" rx="18" fill="none" stroke="{palette['blue']}" stroke-width="18"/>
  <path d="M204 173 H304" stroke="{palette['line']}" stroke-width="16" stroke-linecap="round"/>
  <path d="M370 218 V298" stroke="{palette['line']}" stroke-width="16" stroke-linecap="round"/>
  <path d="M308 347 H204" stroke="{palette['line']}" stroke-width="16" stroke-linecap="round"/>
  <path d="M142 302 V218" stroke="{palette['line']}" stroke-width="16" stroke-linecap="round"/>
</svg>"""

files = {
    "hero_texture.svg": hero_svg,
    "backend_system_icon.svg": backend_icon,
    "ai_validation_icon.svg": ai_validation_icon,
    "architecture_flow_icon.svg": architecture_icon,
}

for name, content in files.items():
    (out_dir / name).write_text(content, encoding="utf-8")

md = """# Kill Your Darlings: Curate Your Images

## Final image set: keepers

This portfolio will use real screenshots for project proof and only use generated/abstract visuals for connective design elements. The image style follows my identity kit: calm technical visuals, soft white background, engineering blue, slate text, and a small teal accent.

| Page / section | Image to use | Real or generated? | Why it belongs |
|---|---|---:|---|
| Home hero | Abstract technical hero texture | Generated connective visual | Sets a calm technical mood without pretending to be project proof. |
| Home featured proof | Screenshot of the LLM Follow-Up Question Generation Backend API response | Real capture | This is the strongest project, so the proof should be an actual working output. |
| Home/project cards | Small consistent icons for backend systems, AI validation, and architecture | Generated connective visuals | Icons help scanning, but they do not replace evidence. |
| LLM Backend Case Study | Screenshot of Swagger/OpenAPI docs or API endpoint output | Real capture | Shows the backend actually exists and is usable. |
| LLM Backend Case Study | TruLens evaluation screenshot or small results table | Real capture | Shows reliability/evaluation rather than only claiming AI quality. |
| FastAPI Backend Project | Screenshot of CRUD request/response or passing tests | Real capture | Demonstrates real implementation and test discipline. |
| AWS-style Backend Project | Screenshot of Docker Compose/LocalStack running | Real capture | Shows cloud-style backend infrastructure, not a decorative AI image. |
| WebSocket Project | Screenshot or short frame of live ticker updates | Real capture | Real-time behaviour is best shown through the actual running app. |
| SQLAlchemy Async Project | Clean architecture diagram: route → service → repository → database | Real project diagram | A diagram is useful here because the value is in the architecture pattern. |
| About Page | Professional photo of me | Real photo | The assignment says anything representing the person should use a real photo. |
| Contact Page | SP monogram/favicon | Generated/simple brand asset | Keeps the page consistent with the identity kit without distracting from the CTA. |

## Where I chose real capture over AI

For all project case studies, I chose real screenshots or real diagrams over AI-generated images. The purpose of the portfolio is to prove that I can build backend and AI systems, so screenshots of APIs, tests, evaluation results, Docker services, and architecture are more credible than generated mockups.

I would only use generated visuals for connective tissue: the hero texture, simple icons, and small brand assets. These support navigation and consistency, but they do not stand in for evidence.

## AI-generated image style

All generated visuals should use the same style:
- Soft white background: `#F8FAFC`
- Main blue: `#2563EB`
- Near-black text/linework: `#0F172A`
- Small teal accent: `#14B8A6`
- Minimal geometric shapes, thin technical lines, no realistic people, no fake UI screenshots

## Generated image I rejected

I rejected a futuristic “AI robot working at a laptop” hero image. It looked polished, but it made the portfolio feel generic and distracted from the actual proof of my work.

I also rejected fake dashboard/mock API screenshots because they could make the portfolio less trustworthy. For technical projects, real screenshots of my own running systems are stronger than attractive but artificial visuals.

## Final decision

The final image set should feel consistent, calm, and technical. Real work captures carry the proof; generated images are limited to quiet supporting visuals.
"""
md_path = out_dir / "flyrank_week3_curate_images.md"
md_path.write_text(md, encoding="utf-8")

print("Created files:")
for p in sorted(out_dir.iterdir()):
    print(p)
