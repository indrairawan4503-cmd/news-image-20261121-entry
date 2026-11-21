#!/usr/bin/env python3
"""Rebuild the 21 November 2026 world-news montage (variant A).

The picture is a photo montage: a COP31 hero photograph from Antalya on
top, four story panels underneath (Kyiv, Poland/NATO, EU aid, and a
code-drawn Wellington cricket scorecard), a red ticker strip, and a
masthead/footer. Every word is typeset here with PIL and Noto Sans, so the
generated photographs never have to carry text themselves.

Running this file rewrites assets/final.png as JPEG data (quality 88,
optimised). The inputs, geometry and wording are fixed, so repeated runs
produce the identical file byte for byte.
"""

from pathlib import Path

import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont

ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "assets"

CANVAS_W, CANVAS_H = 1024, 1024

PALETTE = {
    "navy": (16, 32, 56),
    "gold": (216, 169, 78),
    "red": (176, 42, 30),
    "ticker": (142, 34, 26),
    "ink": (22, 22, 22),
    "grey": (96, 96, 96),
    "white": (255, 255, 255),
    "card": (255, 255, 255),
    "band": (10, 22, 40),
    "sub": (214, 220, 228),
    "foot": (170, 180, 192),
    "frame": (200, 200, 200),
    "green_dark": (18, 92, 52),
    "green_light": (34, 128, 74),
    "pitch": (196, 164, 110),
    "pitch_edge": (160, 128, 84),
    "stumps": (240, 200, 60),
    "ball": (178, 34, 34),
    "ball_edge": (120, 20, 20),
    "strip": (10, 30, 20),
}

HERO_FILE = "media-generation-hero-cop31-0-3d7bc38b-9bea-4b39-ae3a-4bc2e7135b80.webp"

STORIES = [
    {
        "file": "media-generation-panel-kyiv-0-a8f5880d-b39e-4a95-bb45-f50c989cf5ba.webp",
        "kicker": "UKRAINE  ·  KYIV",
        "headline": "Russia hits Kyiv’s bridges",
        "standfirst": "At least 9 dead in an overnight missile and drone attack",
    },
    {
        "file": "media-generation-panel-poland-0-b69f45f8-0740-4b22-8878-ee8ec1773bcb.webp",
        "kicker": "POLAND  ·  NATO",
        "headline": "Poland seeks NATO reinforcements",
        "standfirst": "After Russian missiles crossed its airspace; Tusk calls it a provocation",
    },
    {
        "file": "media-generation-panel-eu-aid-0-f00d6b37-f691-4045-9696-e0f367e3ac3a.webp",
        "kicker": "EU  ·  UKRAINE",
        "headline": "EU sends nearly €8bn to Kyiv",
        "standfirst": "Its largest-ever reforms disbursement",
    },
    {
        "file": None,
        "kicker": "CRICKET  ·  WELLINGTON",
        "headline": "India fight back in Wellington Test",
        "standfirst": "159/1 at stumps on Day 2, trailing by 209",
    },
]


def _font_path(bold):
    """Return the first usable Noto Sans file (DejaVu as fallback)."""
    style = "Bold" if bold else "Regular"
    search = [
        Path("/usr/share/fonts/truetype/noto") / ("NotoSans-%s.ttf" % style),
        Path("/usr/share/fonts/truetype/dejavu")
        / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
    ]
    for path in search:
        if path.is_file():
            return path
    raise SystemExit("could not locate a usable font file")


def _face(bold, size):
    return ImageFont.truetype(str(_font_path(bold)), size)


TYPE = {
    "masthead_kicker": _face(True, 18),
    "dateline": _face(True, 46),
    "hero_kicker": _face(True, 17),
    "hero_head": _face(True, 30),
    "hero_sub": _face(False, 18),
    "panel_kicker": _face(True, 13),
    "panel_head": _face(True, 20),
    "panel_sub": _face(False, 15),
    "ticker": _face(False, 17),
    "footer": _face(False, 15),
    "score": _face(True, 26),
    "day": _face(True, 15),
}


def split_lines(pen, text, face, limit):
    """Greedy word wrap measured with the real font; returns the lines."""
    rows = []
    current = ""
    for token in text.split():
        candidate = (current + " " + token).strip()
        if pen.textlength(candidate, font=face) <= limit:
            current = candidate
        else:
            if current:
                rows.append(current)
            current = token
    if current:
        rows.append(current)
    return rows


def fit_cover(picture, width, height):
    """Centre-crop `picture` to the target aspect, then resize it."""
    src_w, src_h = picture.size
    wanted = width / height
    actual = src_w / src_h
    if actual > wanted:
        keep_w = int(src_h * wanted)
        left = (src_w - keep_w) // 2
        picture = picture.crop((left, 0, left + keep_w, src_h))
    else:
        keep_h = int(src_w / wanted)
        top = (src_h - keep_h) // 2
        picture = picture.crop((0, top, src_w, top + keep_h))
    return picture.resize((width, height), Image.LANCZOS)


def open_photo(name):
    return Image.open(ASSET_DIR / name).convert("RGB")


def draw_scorecard(width, height):
    """Paint the Wellington cricket panel: pitch, stumps, ball, score."""
    panel = Image.new("RGB", (width, height), PALETTE["green_dark"])
    pen = ImageDraw.Draw(panel)
    dark_g = PALETTE["green_dark"][1]
    light_g = PALETTE["green_light"][1]
    for row in range(height):
        shade = int(dark_g + (light_g - dark_g) * row / height)
        pen.line([(0, row), (width, row)], fill=(18, shade, 52))
    # pale pitch strip down the middle
    pen.rectangle([width * 0.30, 0, width * 0.70, height],
                  fill=PALETTE["pitch"])
    pen.rectangle([width * 0.30, 0, width * 0.70, height],
                  outline=PALETTE["pitch_edge"], width=2)
    # crease lines
    pen.line([(width * 0.30, height * 0.30), (width * 0.70, height * 0.30)],
             fill=PALETTE["white"], width=3)
    pen.line([(width * 0.30, height * 0.72), (width * 0.70, height * 0.72)],
             fill=PALETTE["white"], width=3)
    # three stumps and the bails by the top crease
    middle = width // 2
    for offset in (-14, 0, 14):
        pen.rectangle([middle + offset - 3, height * 0.16,
                       middle + offset + 3, height * 0.30],
                      fill=PALETTE["stumps"])
    pen.rectangle([middle - 17, height * 0.155, middle + 17, height * 0.165],
                  fill=PALETTE["stumps"])
    # red ball with a seam arc
    ball_x, ball_y, ball_r = int(width * 0.62), int(height * 0.55), 13
    pen.ellipse([ball_x - ball_r, ball_y - ball_r,
                 ball_x + ball_r, ball_y + ball_r],
                fill=PALETTE["ball"], outline=PALETTE["ball_edge"], width=2)
    pen.arc([ball_x - ball_r, ball_y - ball_r,
             ball_x + ball_r, ball_y + ball_r],
            start=200, end=340, fill=PALETTE["white"], width=2)
    # translucent score strip along the bottom
    strip = Image.new("RGBA", (width, 44), PALETTE["strip"] + (225,))
    panel.paste(strip, (0, height - 44), strip)
    overlay = ImageDraw.Draw(panel)
    overlay.text((10, height - 38), "IND 159/1", font=TYPE["score"],
                 fill=PALETTE["white"])
    overlay.text((width - 10, height - 34), "DAY 2", font=TYPE["day"],
                 fill=PALETTE["gold"], anchor="ra")
    return panel


def paint_masthead(pen):
    """Centred kicker and dateline with a gold rule across the top."""
    kicker = "T H E   W O R L D   I N   O N E   D A Y"
    kicker_w = pen.textlength(kicker, font=TYPE["masthead_kicker"])
    pen.text(((CANVAS_W - kicker_w) / 2, 12), kicker,
             font=TYPE["masthead_kicker"], fill=PALETTE["gold"])
    dateline = "Saturday 21 November 2026"
    date_w = pen.textlength(dateline, font=TYPE["dateline"])
    pen.text(((CANVAS_W - date_w) / 2, 36), dateline,
             font=TYPE["dateline"], fill=PALETTE["white"])
    pen.rectangle([20, 92, CANVAS_W - 20, 95], fill=PALETTE["gold"])


def paint_hero(sheet, pen):
    """COP31 hero photo with its caption band laid over the bottom."""
    photo = fit_cover(open_photo(HERO_FILE), 984, 388)
    sheet.paste(photo, (20, 104))
    pen.rectangle([20, 104, 1004, 492], outline=PALETTE["gold"], width=2)
    pen.rectangle([20, 384, 1004, 492], fill=PALETTE["band"] + (222,))
    pen.text((36, 394), "CLIMATE  ·  ANTALYA, TURKEY",
             font=TYPE["hero_kicker"], fill=PALETTE["gold"])
    headline = "COP31 slips into overtime as fossil fuels vanish from draft"
    rows = split_lines(pen, headline, TYPE["hero_head"], 952)
    cursor = 418
    for row in rows[:2]:
        pen.text((36, cursor), row, font=TYPE["hero_head"],
                 fill=PALETTE["white"])
        cursor += 34
    pen.text((36, cursor + 2),
             "Activists chant “shame” as the EU warns the summit could end with no deal",
             font=TYPE["hero_sub"], fill=PALETTE["sub"])


def paint_panels(sheet, pen):
    """Four story cards in a row under the hero."""
    left, top, card_w, card_h, gutter = 20, 508, 237, 344, 12
    photo_h = 168
    text_w = card_w - 20
    for index, story in enumerate(STORIES):
        x = left + index * (card_w + gutter)
        pen.rectangle([x, top, x + card_w, top + card_h], fill=PALETTE["card"])
        if story["file"] is None:
            picture = draw_scorecard(card_w, photo_h)
        else:
            picture = fit_cover(open_photo(story["file"]), card_w, photo_h)
        sheet.paste(picture, (x, top))
        pen.rectangle([x, top, x + card_w, top + photo_h],
                      outline=PALETTE["frame"], width=1)
        pen.text((x + 10, top + 176), story["kicker"],
                 font=TYPE["panel_kicker"], fill=PALETTE["red"])
        rows = split_lines(pen, story["headline"], TYPE["panel_head"], text_w)
        cursor = top + 198
        for row in rows[:2]:
            pen.text((x + 10, cursor), row, font=TYPE["panel_head"],
                     fill=PALETTE["ink"])
            cursor += 23
        rows = split_lines(pen, story["standfirst"], TYPE["panel_sub"], text_w)
        cursor = top + 248
        for row in rows[:3]:
            pen.text((x + 10, cursor), row, font=TYPE["panel_sub"],
                     fill=PALETTE["grey"])
            cursor += 19


def paint_ticker(pen):
    """Red strip with the day's other headlines."""
    pen.rectangle([20, 868, 1004, 922], fill=PALETTE["ticker"])
    ticker = ("ALSO TODAY:   Sensex rallies nearly 898 points   •   "
              "2027 Hyundai Elantra unveiled in Los Angeles   •   "
              "Brazil strengthens protection of Indigenous land")
    rows = split_lines(pen, ticker, TYPE["ticker"], 952)
    cursor = 876
    for row in rows[:2]:
        pen.text((36, cursor), row, font=TYPE["ticker"],
                 fill=PALETTE["white"])
        cursor += 22


def paint_footer(pen):
    """Centred closing line at the bottom of the page."""
    note = "All stories reported on Saturday 21 November 2026"
    note_w = pen.textlength(note, font=TYPE["footer"])
    pen.text(((CANVAS_W - note_w) / 2, 946), note,
             font=TYPE["footer"], fill=PALETTE["foot"])


def build():
    sheet = Image.new("RGB", (CANVAS_W, CANVAS_H), PALETTE["navy"])
    pen = ImageDraw.Draw(sheet, "RGBA")
    paint_masthead(pen)
    paint_hero(sheet, pen)
    paint_panels(sheet, pen)
    paint_ticker(pen)
    paint_footer(pen)
    target = ASSET_DIR / "final.png"
    sheet.save(str(target), "JPEG", quality=88, optimize=True)
    print("wrote", target, target.stat().st_size, "bytes")


if __name__ == "__main__":
    build()
