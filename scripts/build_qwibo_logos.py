#!/usr/bin/env python3
"""Rebuild Qwibo logo SVGs with Inter Bold wordmark paths (brand book)."""

from __future__ import annotations

import shutil
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
LOGO_DIR = ROOT / "assets" / "images" / "logo"
SITE_LOGO_DIR = ROOT.parent / "qwibo.github.io" / "assets" / "images" / "logo"
FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\segoeuib.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]

SYMBOL = """  <g transform="translate(8,8)">
    <circle cx="22" cy="25" r="13" stroke="{accent}" stroke-width="5"/>
    <circle cx="22" cy="25" r="3" fill="{accent}"/>
    <path d="M22 38H57" stroke="{accent}" stroke-width="5" stroke-linecap="round"/>
    <path d="M22 48H57" stroke="{text}" stroke-width="5" stroke-linecap="round"/>
    <path d="M22 58H44" stroke="{text}" stroke-width="5" stroke-linecap="round"/>
  </g>"""

MARK_SYMBOL = """  <circle cx="22" cy="25" r="13" stroke="#38bdf8" stroke-width="5"/>
  <circle cx="22" cy="25" r="3" fill="#38bdf8"/>
  <path d="M22 38H57" stroke="#38bdf8" stroke-width="5" stroke-linecap="round"/>
  <path d="M22 48H57" stroke="currentColor" stroke-width="5" stroke-linecap="round"/>
  <path d="M22 58H44" stroke="currentColor" stroke-width="5" stroke-linecap="round"/>"""

# Symbol group: translate(8,8), tape lines end at local x=57 → 65px in SVG space.
SYMBOL_X_END = 65
WORDMARK_GAP = 16


def wordmark_path(
    font: TTFont,
    text: str = "qwibo",
    size: float = 40.0,
    *,
    x_offset: float = SYMBOL_X_END + WORDMARK_GAP,
) -> tuple[str, float]:
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    units_per_em = font["head"].unitsPerEm
    scale = size / units_per_em
    letter_spacing = -1.0

    x = 0.0
    chunks: list[str] = []
    for i, ch in enumerate(text):
        glyph_name = cmap.get(ord(ch))
        if not glyph_name:
            continue
        pen = SVGPathPen(glyph_set)
        tpen = TransformPen(pen, (scale, 0, 0, -scale, x + x_offset, 54.0))
        glyph_set[glyph_name].draw(tpen)
        d = pen.getCommands()
        if d:
            chunks.append(d)
        advance = font["hmtx"][glyph_name][0] * scale
        x += advance + (letter_spacing if i < len(text) - 1 else 0.0)

    total_width = x_offset + x + 8.0
    return " ".join(chunks), max(total_width, x_offset + 120.0)


def resolve_font(dest: Path) -> Path:
    for candidate in FONT_CANDIDATES:
        if candidate.is_file():
            return candidate
    raise SystemExit(
        "Nessun font trovato. Installa Inter Bold o usa Windows con Segoe UI Bold."
    )


def write_horizontal(path: Path, *, variant: str, wordmark: str, width: float) -> None:
    if variant == "dark":
        accent, text, fill = "#38bdf8", "#f0f4ff", "#f0f4ff"
        bg_desc = "sfondi scuri"
    else:
        accent, text, fill = "#0284c7", "#0f172a", "#0f172a"
        bg_desc = "sfondi chiari"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} 80" fill="none" role="img" aria-label="Qwibo">
  <title>Qwibo</title>
  <desc>Logo Qwibo per {bg_desc}: bobina che si srotola in righe di testo, wordmark in tracciati vettoriali</desc>
{SYMBOL.format(accent=accent, text=text)}
  <path fill="{fill}" fill-rule="nonzero" d="{wordmark}"/>
</svg>
"""
    path.write_text(svg, encoding="utf-8", newline="\n")


def write_mark(path: Path) -> None:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none" role="img" aria-label="Qwibo">
  <title>Qwibo</title>
  <desc>Una bobina il cui nastro si srotola e diventa righe di testo</desc>
{MARK_SYMBOL}
</svg>
"""
    path.write_text(svg, encoding="utf-8", newline="\n")


def write_favicon(path: Path) -> None:
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none" role="img" aria-label="Qwibo">
  <title>Qwibo</title>
  <rect width="64" height="64" rx="14" fill="#0f172a"/>
  <g transform="translate(9.5,9) scale(0.72)">
    <circle cx="22" cy="25" r="13" stroke="#38bdf8" stroke-width="6"/>
    <circle cx="22" cy="25" r="3.5" fill="#38bdf8"/>
    <path d="M22 38H57" stroke="#38bdf8" stroke-width="6" stroke-linecap="round"/>
    <path d="M22 49H57" stroke="#f0f4ff" stroke-width="6" stroke-linecap="round"/>
    <path d="M22 60H44" stroke="#f0f4ff" stroke-width="6" stroke-linecap="round"/>
  </g>
</svg>
"""
    path.write_text(svg, encoding="utf-8", newline="\n")


def sync_to_site() -> None:
    if not SITE_LOGO_DIR.parent.is_dir():
        return
    SITE_LOGO_DIR.mkdir(parents=True, exist_ok=True)
    for name in (
        "logo-horizontal-dark.svg",
        "logo-horizontal-light.svg",
        "logo-mark.svg",
        "favicon.svg",
        "README.md",
    ):
        src = LOGO_DIR / name
        if src.is_file():
            shutil.copy2(src, SITE_LOGO_DIR / name)
            nested = SITE_LOGO_DIR / "logo" / name
            nested.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, nested)


def main() -> int:
    font_path = resolve_font(Path())
    font = TTFont(font_path)
    wordmark, width = wordmark_path(font)

    write_horizontal(LOGO_DIR / "logo-horizontal-dark.svg", variant="dark", wordmark=wordmark, width=width)
    write_horizontal(LOGO_DIR / "logo-horizontal-light.svg", variant="light", wordmark=wordmark, width=width)
    write_mark(LOGO_DIR / "logo-mark.svg")
    write_favicon(LOGO_DIR / "favicon.svg")
    sync_to_site()
    print(f"OK logos rebuilt (viewBox width {width:.0f})")
    print(f"  {LOGO_DIR}")
    if SITE_LOGO_DIR.is_dir():
        print(f"  synced -> {SITE_LOGO_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
