# SP2023Lab Portfolio — Ship the Ugly One

This is a static portfolio built with plain HTML, CSS and JavaScript. It has one homepage and four reachable project case studies.

## Sitemap

- `/index.html` — homepage, About, Experience, Projects, Skills, Contact
- `/projects/reliable-agentic-ai.html`
- `/projects/interview-drill-coach.html`
- `/projects/weather-dashboard.html`
- `/projects/matrix-solver.html`

## How the files work

- `index.html`: homepage content and links to every case study.
- `projects/*.html`: individual project cases.
- `styles.css`: visual system, page layouts, responsive behaviour and accessibility states.
- `script.js`: mobile menu, sticky-header state, current year and reveal transitions.
- `assets/images/*.svg`: architecture visuals based on the actual project structures. They are SVG so they remain sharp on mobile and desktop.
- `assets/Shyam-Popat-CV-Public.pdf`: downloadable public CV supplied for the site.
- `netlify.toml`: Netlify publish directory and security headers.

## Run locally

```powershell
python -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765`.

## Deploy on the existing Netlify project

1. Extract this ZIP.
2. Open the existing `sp2023lab` project in Netlify.
3. Open Deploys.
4. Drag the entire `sp2023lab-portfolio-v2` folder into the manual deploy area.
5. Wait for the deploy to finish.
6. Test `https://sp2023lab.netlify.app` in an incognito window.

## Required public links configured

- LinkedIn: https://www.linkedin.com/in/sp2023lab/
- GitHub: https://github.com/sp2023lab
- Booking: https://cal.com/shyam-popat-redorz/portfolio-introduction-call
- CV: `assets/Shyam-Popat-CV-Public.pdf`

## Important honesty note

The architecture visuals are diagrams of the implemented or planned project structures. They are not presented as screenshots. No fake UI screenshots are included.
