# samin1554.github.io

Personal portfolio for **Sam Amin** — undergraduate software engineer.
Live at **https://samin1554.github.io**.

Built with [Astro](https://astro.build) and [Tailwind CSS](https://tailwindcss.com)
as a static site. Content lives in typed data files under `src/data/`; components
under `src/components/` are pure presentation.

## Develop

```sh
npm install
npm run dev      # http://localhost:4321
npm run build    # static output to ./dist
npm run preview  # preview the production build
```

## Deploy

Pushing to `main` triggers `.github/workflows/deploy.yml`, which builds the site
and publishes it to GitHub Pages.

## Editing content

| What | Where |
| --- | --- |
| Name, bio, links, education | `src/data/profile.ts` |
| Projects (+ cover images) | `src/data/projects.ts` |
| Experience | `src/data/experience.ts` |
| Open-source contributions | `src/data/openSource.ts` |
| Publications | `src/data/publications.ts` |
| Skills & certifications | `src/data/skills.ts` |

Images live in `public/` (hero at `public/hero-bg.jpg`, project covers in
`public/projects/`).
