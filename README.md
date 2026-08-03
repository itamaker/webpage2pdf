# webpage-to-pdf (Claude Code skill)

A self-contained [Claude Code](https://claude.com/claude-code) skill that exports a live webpage to a pixel-perfect, paginated PDF via headless Chrome screenshots — not the print pipeline. It captures exactly what's on screen (dark themes, canvases, custom fonts, JS-heavy layouts) and paginates it into an A4/Letter/Legal PDF with a title/date header and a URL/page-number footer.

## Install as a skill

Clone directly into your Claude Code skills directory:

```bash
git clone https://github.com/itamaker/webpage-to-pdf-skill.git ~/.claude/skills/webpage-to-pdf
```

Claude Code picks it up automatically. See [SKILL.md](SKILL.md) for how it decides when to fire, and [REFERENCE.md](REFERENCE.md) for the full CLI flag reference, recipes, and troubleshooting.

## Standalone CLI

The skill wraps a small CLI, installable on its own:

```bash
python3 -m pip install -e .
webpage2pdf https://example.com
```

Requires Python >= 3.9 and Google Chrome; Selenium Manager fetches the matching chromedriver automatically.

## License

[MIT](LICENSE) © 2026 Zhaoyang Jia
