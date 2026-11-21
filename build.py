#!/usr/bin/env python3
"""Build the news-image-20261121 variant A photo-montage hero.

Composites four generated photos (hero + three story panels) plus one
code-drawn cricket scorecard panel, with all text drawn in code
(PIL + Noto Sans), so no text can garble inside generated art.
Deterministic: fixed inputs, fixed layout, fixed JPEG quality.
Writes assets/final.png (JPEG bytes; the entry program copies it verbatim).
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

W, H = 1024, 1024
NAVY = (16, 32, 56)
NAVY2 = (24, 48, 82)
GOLD = (216, 169, 78)
RED = (176, 42, 30)
TICKER_RED = (142, 34, 26)
INK = (22, 22, 22)
GREY = (96, 96, 96)
WHITE = (255, 255, 255)
CARD = (255, 255, 255)
GREEN_D = (18, 92, 52)
GREEN_L = (34, 128, 74)


def find_font(bold):
    cands = [
        "/usr/share/fonts/truetype/noto/NotoSans-%s.ttf" % ("Bold" if bold else "Regular"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    raise SystemExit("no usable font found")


def font(bold, size):
    return ImageFont.truetype(find_font(bold), size)


F_KICKER = font(True, 18)
F_DATE = font(True, 46)
F_HERO_KICKER = font(True, 17)
F_HERO_HEAD = font(True, 30)
F_HERO_SUB = font(False, 18)
F_P_KICKER = font(True, 13)
F_P_HEAD = font(True, 20)
F_P_SUB = font(False, 15)
F_TICKER_B = font(True, 17)
F_TICKER = font(False, 17)
F_FOOT = font(False, 15)


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def cover(im, tw, th):
    """Center-crop to target aspect, then resize (deterministic)."""
    sw, sh = im.size
    ta, sa = tw / th, sw / sh
    if sa > ta:
        nw = int(sh * ta)
        x0 = (sw - nw) // 2
        im = im.crop((x0, 0, x0 + nw, sh))
    else:
        nh = int(sw / ta)
        y0 = (sh - nh) // 2
        im = im.crop((0, y0, sw, y0 + nh))
    return im.resize((tw, th), Image.LANCZOS)


def load(name):
    return Image.open(os.path.join(ASSETS, name)).convert("RGB")


def cricket_panel(tw, th):
    """Code-drawn cricket scorecard graphic: pitch, stumps, ball, score."""
    img = Image.new("RGB", (tw, th), GREEN_D)
    d = ImageDraw.Draw(img)
    for y in range(th):
        g = int(GREEN_D[1] + (GREEN_L[1] - GREEN_D[1]) * y / th)
        d.line([(0, y), (tw, y)], fill=(18, g, 52))
    # pitch strip
    d.rectangle([tw * 0.30, 0, tw * 0.70, th], fill=(196, 164, 110))
    d.rectangle([tw * 0.30, 0, tw * 0.70, th], outline=(160, 128, 84), width=2)
    # crease lines
    d.line([(tw * 0.30, th * 0.30), (tw * 0.70, th * 0.30)], fill=WHITE, width=3)
    d.line([(tw * 0.30, th * 0.72), (tw * 0.70, th * 0.72)], fill=WHITE, width=3)
    # stumps (three, yellow) near the top crease
    cx = tw // 2
    for dx in (-14, 0, 14):
        d.rectangle([cx + dx - 3, th * 0.16, cx + dx + 3, th * 0.30], fill=(240, 200, 60))
    d.rectangle([cx - 17, th * 0.155, cx + 17, th * 0.165], fill=(240, 200, 60))
    # red ball with seam
    bx, by, br = int(tw * 0.62), int(th * 0.55), 13
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=(178, 34, 34),
              outline=(120, 20, 20), width=2)
    d.arc([bx - br, by - br, bx + br, by + br], start=200, end=340,
          fill=WHITE, width=2)
    # score strip
    strip = Image.new("RGBA", (tw, 44), (10, 30, 20, 225))
    img.paste(strip, (0, th - 44), strip)
    dd = ImageDraw.Draw(img)
    dd.text((10, th - 38), "IND 159/1", font=font(True, 26), fill=WHITE)
    dd.text((tw - 10, th - 34), "DAY 2", font=font(True, 15), fill=GOLD,
            anchor="ra")
    return img


def main():
    canvas = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(canvas, "RGBA")

    # ---- masthead ----
    kicker = "T H E   W O R L D   I N   O N E   D A Y"
    kw = d.textlength(kicker, font=F_KICKER)
    d.text(((W - kw) / 2, 12), kicker, font=F_KICKER, fill=GOLD)
    date = "Saturday 21 November 2026"
    dw = d.textlength(date, font=F_DATE)
    d.text(((W - dw) / 2, 36), date, font=F_DATE, fill=WHITE)
    d.rectangle([20, 92, W - 20, 95], fill=GOLD)

    # ---- hero: COP31 overtime, Antalya ----
    hero = cover(load("media-generation-hero-cop31-0-3d7bc38b-9bea-4b39-ae3a-4bc2e7135b80.webp"),
                 984, 388)
    canvas.paste(hero, (20, 104))
    d.rectangle([20, 104, 1004, 492], outline=GOLD, width=2)
    # caption band over the bottom of the hero
    d.rectangle([20, 384, 1004, 492], fill=(10, 22, 40, 222))
    d.text((36, 394), "CLIMATE  ·  ANTALYA, TURKEY", font=F_HERO_KICKER, fill=GOLD)
    head = "COP31 slips into overtime as fossil fuels vanish from draft"
    lines = wrap(d, head, F_HERO_HEAD, 952)
    y = 418
    for ln in lines[:2]:
        d.text((36, y), ln, font=F_HERO_HEAD, fill=WHITE)
        y += 34
    d.text((36, y + 2),
           "Activists chant \u201cshame\u201d as the EU warns the summit could end with no deal",
           font=F_HERO_SUB, fill=(214, 220, 228))

    # ---- four story panels ----
    panels = [
        ("media-generation-panel-kyiv-0-a8f5880d-b39e-4a95-bb45-f50c989cf5ba.webp",
         "UKRAINE  ·  KYIV",
         "Russia hits Kyiv\u2019s bridges",
         "At least 9 dead in an overnight missile and drone attack"),
        ("media-generation-panel-poland-0-b69f45f8-0740-4b22-8878-ee8ec1773bcb.webp",
         "POLAND  ·  NATO",
         "Poland seeks NATO reinforcements",
         "After Russian missiles crossed its airspace; Tusk calls it a provocation"),
        ("media-generation-panel-eu-aid-0-f00d6b37-f691-4045-9696-e0f367e3ac3a.webp",
         "EU  ·  UKRAINE",
         "EU sends nearly \u20ac8bn to Kyiv",
         "Its largest-ever reforms disbursement"),
        (None,
         "CRICKET  ·  WELLINGTON",
         "India fight back in Wellington Test",
         "159/1 at stumps on Day 2, trailing by 209"),
    ]
    px, py, pw, ph, gap = 20, 508, 237, 344, 12
    for i, (img_name, kicker_t, head_t, sub_t) in enumerate(panels):
        x = px + i * (pw + gap)
        d.rectangle([x, py, x + pw, py + ph], fill=CARD)
        if img_name is None:
            pic = cricket_panel(pw, 168)
        else:
            pic = cover(load(img_name), pw, 168)
        canvas.paste(pic, (x, py))
        d.rectangle([x, py, x + pw, py + 168], outline=(200, 200, 200), width=1)
        d.text((x + 10, py + 176), kicker_t, font=F_P_KICKER, fill=RED)
        lines = wrap(d, head_t, F_P_HEAD, pw - 20)
        y = py + 198
        for ln in lines[:2]:
            d.text((x + 10, y), ln, font=F_P_HEAD, fill=INK)
            y += 23
        lines = wrap(d, sub_t, F_P_SUB, pw - 20)
        y = py + 248
        for ln in lines[:3]:
            d.text((x + 10, y), ln, font=F_P_SUB, fill=GREY)
            y += 19

    # ---- ticker ----
    d.rectangle([20, 868, 1004, 922], fill=TICKER_RED)
    ticker = ("ALSO TODAY:   Sensex rallies nearly 898 points   \u2022   "
              "2027 Hyundai Elantra unveiled in Los Angeles   \u2022   "
              "Brazil strengthens protection of Indigenous land")
    lines = wrap(d, ticker, F_TICKER, 952)
    y = 876
    for ln in lines[:2]:
        d.text((36, y), ln, font=F_TICKER, fill=WHITE)
        y += 22

    # ---- footer ----
    foot = "All stories reported on Saturday 21 November 2026"
    fw = d.textlength(foot, font=F_FOOT)
    d.text(((W - fw) / 2, 946), foot, font=F_FOOT, fill=(170, 180, 192))

    out = os.path.join(ASSETS, "final.png")
    canvas.save(out, format="JPEG", quality=88, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
