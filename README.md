# webpage-to-pdf-skill

Standalone agent skill that exports a live webpage to a pixel-perfect, paginated PDF via headless Chrome screenshots — a WYSIWYG capture of exactly what's on screen (dark themes, canvases, custom fonts, JS-heavy layouts), not a print-CSS render.

This repository is structured for the open `skills` installer ecosystem and contains a single skill: `webpage-to-pdf`.

## Install

Standalone (default `skills` CLI):

```bash
npx skills add itamaker/webpage-to-pdf-skill
```

Or via the [`itamaker/skills`](https://github.com/itamaker/skills) Claude Code plugin marketplace:

```text
/plugin marketplace add itamaker/skills
/plugin install webpage-to-pdf-skill@itamaker-skills
```

## What the skill covers

- Screenshots the full page at Retina (2×) resolution and paginates it into A4/Letter/Legal pages with a title/date header and a URL/page-number footer.
- Waits for the page to settle and scrolls it first, so lazy-loaded images and infinite-scroll content actually render.
- Handles pages behind a login (`--login`), bot-hostile sites (`--headed`, `--user-data-dir`), and slow single-page apps (`--wait`).
- Ships CJK-safe font fallbacks so Chinese, Japanese, and Korean titles don't render as tofu boxes.

## Usage examples

- `Use $webpage-to-pdf to save https://example.com/article as a PDF.`
- `Use $webpage-to-pdf to archive this page, it's US Letter and needs no header/footer.`
- `Use $webpage-to-pdf to export this dashboard, it's slow to render so give it extra wait time.`

## Repository Layout

```text
skills/
  webpage-to-pdf/
    SKILL.md              # entry point read by the agent
    references/
      REFERENCE.md         # full flag reference, recipes, troubleshooting
    pyproject.toml         # packaging for the bundled `webpage2pdf` CLI
    webpage2pdf/            # CLI source (Selenium capture + Pillow pagination)
```

## License

[MIT](./LICENSE)
