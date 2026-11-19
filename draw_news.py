#!/usr/bin/env python3
"""Draw the news-image entry: one 1024x1024 infographic summing up the world news of Thursday 19 November 2026.

Output: entry.png in this directory (PNG, at most 1 MiB, 1024x1024).
Run: python3 draw_news.py
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BG_TOP = (11, 18, 32)
BG_BOTTOM = (16, 28, 52)
CARD = (24, 38, 66)
CARD_EDGE = (52, 78, 116)
WHITE = (245, 247, 250)
MUTED = (176, 190, 210)
GOLD = (232, 184, 64)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
F_KICKER = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 30)
F_DATE = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 62)
F_TAG = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 20)
F_HEAD = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 30)
F_BODY = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 22)
F_FOOT = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 20)

STORIES = [
    ("DIPLOMACY", (56, 189, 248),
     "Trump, Xi, Putin set for Shenzhen summit",
     "First three-way meeting: nuclear arms, Ukraine and the Iran conflict on the agenda."),
    ("MIDDLE EAST", (248, 113, 113),
     "Iran and US trade strikes in the Gulf",
     "Tehran fires at US bases in Kuwait and Bahrain; a tanker is hit in the Strait of Hormuz."),
    ("GAMES", (192, 132, 252),
     "Grand Theft Auto VI launches worldwide",
     "Gamers enter Vice City as the biggest game launch in years begins its global rollout."),
    ("TRADE", (74, 222, 128),
     "EU approves Indonesia trade pact",
     "Council greenlights the deal to cut tariffs and offset US trade pressure."),
    ("ISRAEL", (251, 191, 36),
     "Eisenkot tapped to form government",
     "President Herzog bypasses Netanyahu; ex-army chief gets first shot at a coalition."),
    ("SPACE", (45, 212, 191),
     "Voyager 1 reaches a light-day away",
     "NASA's farthest spacecraft crosses a new distance milestone."),
]


def gradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h), top)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        d.line([(0, y), (w, y)],
               fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def main():
    img = gradient(W, H, BG_TOP, BG_BOTTOM)
    d = ImageDraw.Draw(img)

    # Header (date auto-fits the width)
    d.text((36, 34), "WORLD NEWS  •  ONE DAY IN ONE IMAGE", font=F_KICKER, fill=GOLD)
    date_text = "Thursday, 19 November 2026"
    date_size = 62
    while date_size > 30:
        f_date = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", date_size)
        if d.textlength(date_text, font=f_date) <= W - 72:
            break
        date_size -= 2
    d.text((36, 72), date_text, font=f_date, fill=WHITE)
    d.rectangle([36, 158, W - 36, 162], fill=GOLD)

    # Story cards: 2 columns x 3 rows
    margin, gap = 36, 20
    cw = (W - margin * 2 - gap) // 2
    ch = 238
    top0 = 186
    for i, (tag, color, head, body) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x0 = margin + col * (cw + gap)
        y0 = top0 + row * (ch + 18)
        x1, y1 = x0 + cw, y0 + ch
        d.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=CARD, outline=CARD_EDGE, width=2)
        # Tag pill
        tw = d.textlength(tag, font=F_TAG) + 24
        d.rounded_rectangle([x0 + 20, y0 + 18, x0 + 20 + tw, y0 + 50], radius=16, fill=color)
        d.text((x0 + 32, y0 + 23), tag, font=F_TAG, fill=(10, 14, 24))
        # Headline
        y = y0 + 62
        for line in wrap(d, head, F_HEAD, cw - 40)[:2]:
            d.text((x0 + 20, y), line, font=F_HEAD, fill=WHITE)
            y += 38
        # Body
        y += 6
        for line in wrap(d, body, F_BODY, cw - 40)[:3]:
            d.text((x0 + 20, y), line, font=F_BODY, fill=MUTED)
            y += 29

    # Footer
    d.text((36, H - 44), "Six stories that defined the day  •  make.fun news image",
           font=F_FOOT, fill=MUTED)

    img.save("entry.png", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
