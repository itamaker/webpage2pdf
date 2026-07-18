# webpage2pdf

**Pixel-perfect webpage → paginated PDF**, powered by headless Chrome screenshots.

[License: MIT](LICENSE)

`webpage2pdf` captures a full-length, high-resolution screenshot of any web page — exactly as Chrome renders it — then slices it into clean A4/Letter pages with a professional header and footer:

- **Header**: page title + capture date
- **Footer**: source URL + page numbers (`3 / 12`)

Perfect for archiving articles, saving evidence of what a page looked like, sharing docs with people who don't want links, or building a personal reading library.

```
┌────────────────────────────────────────────┐
│ Delta Serving: A Deep Dive     2026/07/18  │  ← header: title + date
├────────────────────────────────────────────┤
│                                            │
│         (page content, rendered            │
│          exactly as in Chrome,             │
│          Retina 2× resolution)             │
│                                            │
├────────────────────────────────────────────┤
│ https://example.com/blog/delta      3 / 12 │  ← footer: URL + page no.
└────────────────────────────────────────────┘
```

## Why screenshot-based?

Most HTML-to-PDF tools (`wkhtmltopdf`, Chrome's *Print to PDF*, `weasyprint`) go through the browser's **print** pipeline. Print CSS frequently breaks modern layouts: collapsed sidebars, missing backgrounds, broken web fonts, mangled charts.

`webpage2pdf` instead captures what you *actually see* on screen, at Retina (2×) resolution, and paginates the image itself. What you see is exactly what you get — dark themes, canvases, charts, custom fonts and all.

The trade-off: the output is an image-based PDF, so **text is not selectable/searchable**. If you need selectable text, use Chrome's built-in *Print to PDF* instead. See [Limitations](#limitations).

## Features

- 🖼 **True-to-screen rendering** — captures the live page, not a print stylesheet
- 📄 **Real pagination** — A4 / Letter / Legal, physically-accurate page size in the PDF
- 🏷 **Automatic header & footer** — title, date, URL and page numbers on every page
- 🔍 **Retina quality** — 2× device scale factor by default (configurable 1–3×)
- 🐢 **Lazy-load aware** — scrolls the whole page first so lazy images actually render
- 🔐 **Login support** — `--login` opens a visible browser and waits for you to sign in
- 👤 **Profile reuse** — `--user-data-dir` reuses a Chrome profile with existing sessions
- 🈶 **CJK-safe** — falls back to PingFang / Noto Sans CJK / Microsoft YaHei so Chinese, Japanese and Korean titles don't turn into tofu (□□□)
- 🧳 **Zero driver setup** — Selenium ≥ 4.6 auto-downloads the matching chromedriver

## Requirements

- Python ≥ 3.9
- Google Chrome (any recent version)

## Installation

```bash
# from source
git clone https://github.com/itamaker/webpage2pdf.git
cd webpage2pdf
pip install .

# or with pipx (recommended for CLI tools)
pipx install .
```

## Quick start

```bash
# simplest: URL in, PDF out (filename derived from the URL)
webpage2pdf https://en.wikipedia.org/wiki/PDF

# choose the output path
webpage2pdf https://example.com -o example.pdf

# page behind a login: a browser window opens, sign in, press Enter
webpage2pdf https://mysite.com/dashboard --login

# no console script? run the package directly
python3 -m webpage2pdf https://example.com
```

## CLI reference

```
webpage2pdf [options] URL [OUTPUT]
```

| Option | Default | Description |
|---|---|---|
| `URL` | — | Page to export (`https://` may be omitted) |
| `OUTPUT` / `-o PATH` | derived from URL | Output PDF path |
| `--login` | off | Open a visible browser; export after you sign in and press Enter |
| `--headed` | off | Show the browser window (some bot-hostile sites need this) |
| `--wait SECONDS` | `3` | Extra wait after page load (increase for slow/JS-heavy pages) |
| `--no-scroll` | off | Skip the pre-capture full-page scroll (faster, but lazy images may miss) |
| `--width PX` | `1400` | Browser viewport width |
| `--scale {1,2,3}` | `2` | Screenshot scale factor (2 = Retina) |
| `--page-size {a4,letter,legal}` | `a4` | Paper size |
| `--title TEXT` | page `<title>` | Override the header title |
| `--no-header` | off | Skip the header band |
| `--no-footer` | off | Skip the footer band |
| `--chrome-binary PATH` | auto-detect | Path to the Chrome executable |
| `--user-data-dir DIR` | — | Chrome user-data directory (reuse logged-in sessions) |
| `--version` | — | Print version and exit |

## Recipes

**A slow single-page app that renders after load**

```bash
webpage2pdf https://app.example.com/report --wait 10
```

**Skip login every time by reusing a dedicated profile**

```bash
# first run: sign in once, the session is saved into the profile dir
webpage2pdf https://mysite.com/dashboard --login --user-data-dir ~/.webpage2pdf-profile

# later runs: headless, already logged in
webpage2pdf https://mysite.com/dashboard --user-data-dir ~/.webpage2pdf-profile
```

> Note: Chrome refuses to share a user-data directory with a running instance —
> use a dedicated directory as above, not your daily browser profile.

**US Letter, clean pages without header/footer**

```bash
webpage2pdf https://example.com --page-size letter --no-header --no-footer
```

**Narrow, mobile-ish rendering**

```bash
webpage2pdf https://example.com --width 800
```

## How it works

1. **Launch** — Selenium starts Chrome (headless by default); Selenium Manager fetches the matching chromedriver automatically.
2. **Settle** — waits for `document.readyState === "complete"` plus `--wait` seconds, then scrolls through the entire page to trigger lazy-loaded images, and back to top.
3. **Capture** — uses the Chrome DevTools Protocol (`Page.captureScreenshot` with `captureBeyondViewport`) to shoot the page in 4000-px chunks at the chosen scale factor, then stitches the chunks into one tall image.
4. **Paginate** — slices the image into pages matching the chosen paper's aspect ratio, drawing the header/footer bands with Pillow. All metrics scale proportionally with `--width`/`--scale`, so any resolution keeps the same layout.
5. **Save** — writes a multi-page PDF whose embedded DPI makes each page physically A4/Letter/Legal-sized.

## Troubleshooting

**"Failed to launch Chrome / cannot find Chrome"**
Install Google Chrome, or point at the binary explicitly:
`webpage2pdf URL --chrome-binary "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`

**Page renders blank or half-empty**
Increase `--wait` (JS-heavy pages), or try `--headed` — a few sites serve empty shells to headless browsers.

**Site blocks the capture / shows a bot check**
Use `--headed`, or `--login` and pass the check manually, or `--user-data-dir` with a profile that already has cookies.

**CJK titles show as boxes (□□□)**
The bundled font list covers macOS (PingFang), Linux (Noto Sans CJK) and Windows (Microsoft YaHei). On minimal Linux installs: `sudo apt install fonts-noto-cjk`.

**Infinite-scroll feeds produce enormous PDFs**
The pre-capture scroll stops growing after ~200 steps, but feeds like Twitter can still get long. Use `--no-scroll` to capture only the initially loaded content.

## Limitations

- **Text is not selectable or searchable** — pages are rasterized images. This is the price of pixel-perfect fidelity.
- File sizes are larger than text-based PDFs (roughly 0.5–2 MB per page at 2×; use `--scale 1` for smaller files).
- Fixed/sticky elements (floating navbars, cookie banners) may repeat in every captured chunk, since Chrome re-renders them per viewport.
- Pages are cut at fixed heights; a line of text can be split across a page break.

## Contributing

Issues and PRs are welcome. Ideas on the roadmap:

- [ ] Smart page breaks (avoid cutting through text lines)
- [ ] Hide selectors before capture (`--hide "css,selectors"` for cookie banners)
- [ ] Batch mode: read URLs from a file, export a PDF per URL
- [ ] Optional searchable-text layer via OCR

Dev setup:

```bash
git clone https://github.com/itamaker/webpage2pdf.git
cd webpage2pdf
pip install -e .
python3 -m webpage2pdf https://example.com -o /tmp/smoke.pdf
```

## License

[MIT](LICENSE) © 2026 Zhaoyang Jia
