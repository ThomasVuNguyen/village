# Village documentation site

This folder hosts the documentation for **Village**, built on top of the Astro Chiri theme.

## Run locally

```bash
cd documentation
pnpm install
pnpm dev
```

Open the URL Astro prints (defaults to http://localhost:4321).

## Deploy

- Netlify: `pnpm add @astrojs/netlify` and set `adapter: netlify()` in `astro.config.ts`.
- Vercel: `pnpm add @astrojs/vercel` and set `adapter: vercel()` in `astro.config.ts`.
- Static export: `pnpm add @astrojs/static` and set `adapter: static()` in `astro.config.ts`.

Update `src/config.ts` with the final `site.website` value before publishing so feeds and sitemaps use the correct domain.

## Firebase Hosting

Build then deploy the static `dist` folder:

```bash
pnpm build
firebase deploy --only hosting
```

Make sure your Firebase project is initialized for hosting in this repo (`firebase init hosting`).

## Content map

- `src/content/about/about.md`: Intro shown on the homepage.
- `src/content/posts/*.md`: Docs pages (quickstart, CLI reference, architecture, security/lifecycle).

## Notes

- Theme helpers (RSS, OG images, etc.) remain; disable in `src/config.ts` if not needed.
- All commands rely on Node 16+.
