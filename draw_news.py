#!/usr/bin/env python3
"""Draw the news-image entry v2: a one-page newspaper summing up the world news
of Thursday 19 November 2026. 35 stories: 3 illustrated leads, 8 illustrated
secondaries, 24 numbered briefs, a UTC timeline and a DATE CHECK box.

Output: entry.png in this directory (PNG, at most 1 MiB, 1024x1024).
Run: python3 draw_news.py
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 233)
INK = (24, 22, 18)
NAVY = (30, 58, 95)
RED = (176, 32, 32)
GOLD = (200, 150, 40)
MUTED = (110, 105, 95)
LINE = (200, 192, 172)
WHITE = (255, 255, 255)
BLUE = (43, 108, 176)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
_cache = {}


def font(name, size):
    key = (name, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FONT_DIR + name, size)
    return _cache[key]


SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"

REGION_COLORS = {
    "ASIA": (190, 90, 30), "EUROPE": (43, 108, 176), "AMERICAS": (60, 140, 90),
    "AFRICA": (150, 110, 30), "MIDDLE EAST": (150, 60, 120), "OCEANIA": (60, 130, 150),
    "GLOBAL": (120, 60, 160),
}

# (region, topic, headline, summary, source)
LEADS = [
    ("ASIA", "SUMMIT", "Trump, Xi and Putin hold first three-way summit",
     "The three nuclear powers meet at APEC in Shenzhen; Ukraine, Iran and trade top the agenda.",
     "REUTERS \u00b7 AP"),
    ("GLOBAL", "GAMES", "GTA VI arrives after a 13-year wait",
     "Rockstar's sequel unlocks at midnight in each country, New Zealand first; 15.9m pre-orders banked.",
     "ANADOLU"),
    ("AMERICAS", "MARKETS", "Anthropic debuts in the biggest IPO on record",
     "Priced at $83, the Claude maker raised $81.3bn and is valued near $1.5tn; trading starts on Nasdaq as ANT.",
     "REUTERS"),
]

SECONDARIES = [
    ("EUROPE", "LAW", "World Court rules on Myanmar's Rohingya case",
     "The ICJ reads its judgment in The Gambia's case over the 2017 campaign.", "BBC"),
    ("GLOBAL", "CLIMATE", "COP31 enters its final 48 hours",
     "Ministers take over the text in Antalya; the $120bn adaptation fund is still open.", "UNFCCC"),
    ("ASIA", "WEATHER", "Akvan bears down as 200,000 flee the coast",
     "Red alerts in 11 districts; landfall near Puri is due Friday.", "IMD"),
    ("EUROPE", "UKRAINE WAR", "Left off the agenda, Ukraine watches Shenzhen",
     "Kyiv fears being carved up; the White House says the war was raised.", "KYIV"),
    ("ASIA", "TRADE", "APEC leaders adopt the Shenzhen Declaration",
     "Twenty-one economies back digital trade and an Asia-Pacific community.", "APEC"),
    ("AMERICAS", "WEATHER", "Flooded Florida braces for still more rain",
     "A foot of rain in 24 hours; Broward schools stay shut.", "NWS"),
    ("ASIA", "EDUCATION", "Half a million sit Korea's Suneung exam",
     "551,864 take the college exam; flights pause and a nationwide alert runs.", "YONHAP"),
    ("AMERICAS", "IRAN WAR", "Trump weighs a new Iran offensive, reports say",
     "He claims Tehran is 'looking at' biological weapons; Iran denies it.", "REUTERS"),
]

BRIEFS = [
    ("Gaza", "Israeli tanks cross the Yellow Line in a rare raid; Hamas calls it a truce breach"),
    ("Crimea", "bridge attacked again; traffic halted, Russian officials say"),
    ("Mexico City", "Banxico cuts rates to 6.25% on a 3-2 vote"),
    ("Canberra", "Australia sanctions three West Bank settler groups"),
    ("Mogadishu", "Somalia accuses the UAE of secret military bases on its soil"),
    ("Frankfurt", "Deutsche Bank handled $682m in Epstein-linked deals, FT reports"),
    ("Washington", "Senators warn AI cyber threats are outpacing defences"),
    ("Ottawa", "Carney: Canada rethinks China ties, seeking the right deal"),
    ("Tokyo", "India and Japan review defence ties at their 2+2 dialogue"),
    ("Bengaluru", "Amazon pledges $7bn for renewables in India by 2030"),
    ("Sydney", "Duckett's 133 puts England in charge of the third ODI"),
    ("Auckland", "New Zealand plays first as GTA VI unlocks at local midnight"),
    ("Baghdad", "Six French ISIL members jailed for life in Iraq"),
    ("Nairobi", "Kenya floods kill six as Ruto gives his State of the Nation address"),
    ("Caracas", "Hegseth signs a US-Venezuela military deal"),
    ("Washington", "Vance: no 'forever war' in the Gulf"),
    ("Manama", "Bapco refinery back on its feet after the attacks"),
    ("Riyadh", "Gulf leaders urge Trump not to strike Iran"),
    ("Washington", "Lu Yuming becomes the first Asian-American House Democratic chair"),
    ("Sacramento", "California braces for an atmospheric river; flood advisories out"),
    ("La Paz", "Bolivia declares an El Ni\u00f1o emergency; 78,000 families hit"),
    ("Bogot\u00e1", "Colombia's unions strike nationwide over the 'Economic Rescue' bill"),
    ("Canberra", "Australia's jobless rate rises; economists warn of recession"),
    ("Taipei", "Taiwan reports two Russian Tu-95 aircraft nearby, second time this week"),
]

BRIEF_REGIONS = [
    "MIDDLE EAST", "EUROPE", "AMERICAS", "OCEANIA", "AFRICA", "EUROPE",
    "AMERICAS", "AMERICAS", "ASIA", "ASIA", "OCEANIA", "OCEANIA",
    "MIDDLE EAST", "AFRICA", "AMERICAS", "AMERICAS", "MIDDLE EAST", "MIDDLE EAST",
    "AMERICAS", "AMERICAS", "AMERICAS", "AMERICAS", "OCEANIA", "ASIA",
]

TIMELINE = [
    ("OVERNIGHT", "Crimea bridge hit again"),
    ("MORNING", "Summit opens in Shenzhen"),
    ("10:00 UTC", "ICJ rules on the Rohingya case"),
    ("MIDDAY", "COP31 enters its final 48 hours"),
    ("14:30 UTC", "Anthropic starts trading on Nasdaq"),
    ("AFTERNOON", "Akvan nears Odisha"),
    ("EVENING", "GTA VI unlocks around the world"),
    ("LATE", "Colombia's unions strike"),
]


def region_counts():
    counts = {}
    for region, *_ in LEADS + SECONDARIES:
        counts[region] = counts.get(region, 0) + 1
    for r in BRIEF_REGIONS:
        counts[r] = counts.get(r, 0) + 1
    return counts


def text_block(draw, x, y, text, fnt, fill, max_w, line_h, max_lines):
    """Draw wrapped text, return the y just below the last line."""
    lines = []
    for para in text.split("\n"):
        lines.extend(textwrap.wrap(para, width=1000) or [""])
    wrapped = []
    for ln in lines:
        while draw.textlength(ln, font=fnt) > max_w and len(ln) > 1:
            cut = len(ln) - 1
            while cut > 0 and draw.textlength(ln[:cut], font=fnt) > max_w:
                cut -= 1
            while cut > 0 and ln[cut] != " ":
                cut -= 1
            wrapped.append(ln[:cut].rstrip())
            ln = ln[cut:].strip()
        wrapped.append(ln)
    wrapped = wrapped[:max_lines]
    for i, ln in enumerate(wrapped):
        draw.text((x, y + i * line_h), ln, font=fnt, fill=fill)
    return y + len(wrapped) * line_h


# ---------- illustrations (all drawn in code) ----------

def illo_summit(draw, x, y, w, h):
    # sunset skyline + three flags on poles
    for i in range(h):
        t = i / max(h - 1, 1)
        draw.line([(x, y + i), (x + w, y + i)],
                  fill=(int(250 - 60 * t), int(200 - 90 * t), int(120 - 20 * t)))
    draw.ellipse([x + w - 70, y + 8, x + w - 22, y + 56], fill=(255, 220, 120))
    for bx, bw, bh in [(0, 44, 52), (46, 30, 78), (80, 52, 44), (136, 34, 66), (174, 44, 58),
                       (222, 30, 82), (256, 46, 48), (306, 40, 70)]:
        draw.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(70, 60, 80))
    # three flags: US, China, Russia
    poles = [(40, "US"), (110, "CN"), (180, "RU")]
    for px, code in poles:
        draw.line([(x + px, y + h - 8), (x + px, y + 14)], fill=(60, 50, 40), width=3)
        if code == "US":
            for s in range(5):
                draw.rectangle([x + px + 2, y + 16 + s * 7, x + px + 46, y + 16 + s * 7 + 4],
                               fill=RED if s % 2 == 0 else WHITE)
            draw.rectangle([x + px + 2, y + 16, x + px + 20, y + 30], fill=NAVY)
        elif code == "CN":
            draw.rectangle([x + px + 2, y + 16, x + px + 46, y + 52], fill=(222, 41, 16))
            draw.text((x + px + 8, y + 22), "\u2605", font=font(SANS_B, 14), fill=GOLD)
        else:
            draw.rectangle([x + px + 2, y + 16, x + px + 46, y + 28], fill=WHITE)
            draw.rectangle([x + px + 2, y + 28, x + px + 46, y + 40], fill=BLUE)
            draw.rectangle([x + px + 2, y + 40, x + px + 46, y + 52], fill=RED)
    draw.rectangle([x + 8, y + h - 26, x + 150, y + h - 8], fill=INK)
    draw.text((x + 12, y + h - 25), "FIRST THREE-WAY MEETING", font=font(SANS_B, 9), fill=WHITE)


def illo_gta_lead(draw, x, y, w, h):
    # Vice City sunset: purple sky, sun, palms, skyline
    for i in range(h):
        t = i / max(h - 1, 1)
        draw.line([(x, y + i), (x + w, y + i)],
                  fill=(int(120 - 40 * t), int(30 + 20 * t), int(140 - 40 * t)))
    draw.ellipse([x + w // 2 - 34, y + 10, x + w // 2 + 34, y + 78], fill=(255, 200, 80))
    for bx, bw, bh in [(0, 40, 40), (44, 28, 62), (76, 46, 34), (200, 40, 56), (244, 30, 70), (278, 46, 38)]:
        draw.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(40, 20, 60))
    # palm silhouettes
    for px in (120, 260):
        draw.line([(x + px, y + h), (x + px + 6, y + h - 58)], fill=(30, 15, 45), width=4)
        for a in range(5):
            ang = -160 + a * 20
            import math
            ex = x + px + 6 + int(30 * math.cos(math.radians(ang)))
            ey = y + h - 58 + int(30 * math.sin(math.radians(ang)))
            draw.line([(x + px + 6, y + h - 58), (ex, ey)], fill=(30, 15, 45), width=3)
    draw.rectangle([x + 8, y + 8, x + 96, y + 26], fill=(255, 200, 80))
    draw.text((x + 12, y + 10), "OUT TODAY", font=font(SANS_B, 11), fill=(60, 20, 60))
    draw.text((x + w - 120, y + h - 30), "VICE CITY", font=font(SANS_B, 16), fill=WHITE)


def illo_ant(draw, x, y, w, h):
    # Nasdaq debut: green board, rising candlesticks, ANT $83
    draw.rectangle([x, y, x + w, y + h], fill=(16, 60, 40))
    draw.rectangle([x, y, x + w, y + 22], fill=(10, 40, 28))
    draw.text((x + 8, y + 4), "NASDAQ \u00b7 FIRST TRADES TODAY", font=font(SANS_B, 10), fill=(150, 230, 180))
    # candlesticks rising left to right
    base = y + h - 30
    for i, (low, high) in enumerate([(10, 24), (16, 32), (24, 40), (32, 48), (40, 56)]):
        cx = x + 20 + i * 30
        draw.line([(cx + 8, base - high - 6), (cx + 8, base - low + 4)], fill=(120, 220, 150), width=2)
        draw.rectangle([cx, base - high, cx + 16, base - low], fill=(60, 200, 110))
    pts = [(x + 20, base - 24), (x + 50, base - 32), (x + 80, base - 40), (x + 110, base - 48),
           (x + 140, base - 56), (x + 170, base - 64)]
    draw.line(pts, fill=GOLD, width=3)
    draw.text((x + 190, y + 30), "ANT", font=font(SANS_B, 34), fill=WHITE)
    draw.text((x + 190, y + 68), "$83", font=font(SANS_B, 28), fill=GOLD)
    draw.text((x + 190, y + 100), "BIGGEST IPO EVER", font=font(SANS_B, 9), fill=(150, 230, 180))


def illo_icj(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(220, 230, 245))
    cx = x + 60
    draw.polygon([(cx - 44, y + 16), (cx + 44, y + 16), (cx, y + 2)], fill=(120, 130, 150))
    draw.rectangle([cx - 47, y + 16, cx + 47, y + 20], fill=(120, 130, 150))
    for i in range(4):
        px = cx - 40 + i * 22
        draw.rectangle([px, y + 22, px + 8, y + 38], fill=(120, 130, 150))
    draw.rectangle([cx - 47, y + 40, cx + 47, y + 43], fill=(120, 130, 150))
    draw.text((x + 8, y + h - 14), "ICJ \u00b7 THE HAGUE", font=font(SANS_B, 10), fill=NAVY)
    draw.text((x + 130, y + h - 14), "730,000 FLED IN 2017", font=font(SANS_B, 10), fill=RED)


def illo_cop31(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(20, 90, 80))
    draw.ellipse([x + 12, y + 8, x + 52, y + 48], fill=(60, 160, 220))
    draw.ellipse([x + 22, y + 14, x + 40, y + 30], fill=(90, 180, 90))
    draw.rectangle([x + 66, y + 10, x + 74, y + 40], fill=(220, 220, 220))
    draw.ellipse([x + 62, y + 38, x + 78, y + 54], fill=RED)
    draw.rectangle([x + 66, y + 26, x + 74, y + 40], fill=RED)
    draw.text((x + 96, y + 8), "$120bn", font=font(SANS_B, 24), fill=WHITE)
    draw.text((x + 96, y + 36), "ADAPTATION FUND \u00b7 ANTALYA", font=font(SANS_B, 9), fill=(160, 230, 210))


def illo_cyclone(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(30, 50, 90))
    cx, cy = x + 60, y + h // 2
    for r in (26, 19, 12, 5):
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=200, end=560, fill=WHITE, width=3)
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=GOLD)
    draw.text((x + 100, y + 6), "AKVAN", font=font(SANS_B, 20), fill=WHITE)
    draw.text((x + 100, y + 30), "200,000 EVACUATED", font=font(SANS_B, 10), fill=GOLD)
    draw.text((x + 100, y + 46), "LANDFALL FRI \u00b7 PURI", font=font(SANS_B, 10), fill=WHITE)


def illo_ukraine(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h // 2], fill=(60, 130, 200))
    draw.rectangle([x, y + h // 2, x + w, y + h], fill=(255, 210, 60))
    draw.ellipse([x + 14, y + 10, x + 74, y + 40], fill=WHITE)
    draw.ellipse([x + 34, y + 16, x + 54, y + 34], fill=INK)
    draw.text((x + 88, y + 8), "KYIV WATCHES", font=font(SANS_B, 16), fill=WHITE)
    draw.text((x + 88, y + 30), "LEFT OFF THE AGENDA", font=font(SANS_B, 9), fill=WHITE)
    draw.text((x + 8, y + h - 18), "UKRAINE FEARS BEING CARVED UP", font=font(SANS_B, 9), fill=(90, 60, 0))


def illo_declaration(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(230, 235, 245))
    draw.rectangle([x + 12, y + 6, x + 76, y + h - 6], fill=WHITE, outline=(150, 160, 180))
    for i in range(5):
        draw.line([(x + 18, y + 14 + i * 8), (x + 70, y + 14 + i * 8)], fill=(170, 175, 185), width=2)
    draw.rectangle([x + 18, y + 8, x + 44, y + 12], fill=RED)
    draw.text((x + 88, y + 8), "SHENZHEN", font=font(SANS_B, 16), fill=NAVY)
    draw.text((x + 88, y + 28), "DECLARATION", font=font(SANS_B, 16), fill=NAVY)
    draw.text((x + 88, y + h - 16), "21 ECONOMIES SIGN", font=font(SANS_B, 9), fill=MUTED)


def illo_florida(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(70, 85, 110))
    for i in range(8):
        rx = x + 10 + i * 28
        draw.line([(rx, y + 4), (rx - 6, y + 22)], fill=(170, 200, 230), width=2)
    draw.polygon([(x + 16, y + 30), (x + 52, y + 18), (x + 88, y + 30)], fill=(40, 50, 70))
    draw.rectangle([x + 22, y + 30, x + 82, y + 52], fill=(200, 190, 160))
    draw.rectangle([x, y + h - 12, x + w, y + h], fill=(60, 130, 200))
    draw.text((x + 100, y + 8), "15 IN RAIN", font=font(SANS_B, 18), fill=WHITE)
    draw.text((x + 100, y + 30), "BROWARD SCHOOLS SHUT", font=font(SANS_B, 9), fill=(200, 220, 240))


def illo_suneung(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(245, 240, 220))
    draw.rectangle([x + 12, y + 6, x + 76, y + h - 6], fill=WHITE, outline=(150, 140, 110))
    for i in range(4):
        draw.ellipse([x + 18, y + 12 + i * 10, x + 26, y + 20 + i * 10], outline=(120, 110, 90))
        draw.line([(x + 30, y + 16 + i * 10), (x + 68, y + 16 + i * 10)], fill=(170, 160, 130), width=2)
    draw.polygon([(x + 60, y + h - 4), (x + 70, y + h - 4), (x + 65, y + h - 14)], fill=(220, 120, 40))
    draw.text((x + 88, y + 6), "551,864", font=font(SANS_B, 22), fill=NAVY)
    draw.text((x + 88, y + 32), "SIT THE SUNEUNG", font=font(SANS_B, 10), fill=INK)
    draw.text((x + 88, y + h - 16), "FLIGHTS PAUSE", font=font(SANS_B, 9), fill=MUTED)


def illo_iran_claim(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(40, 35, 45))
    draw.ellipse([x + 18, y + 8, x + 46, y + 36], fill=(200, 200, 210))
    draw.rectangle([x + 28, y + 36, x + 36, y + 50], fill=(200, 200, 210))
    draw.rounded_rectangle([x + 56, y + 6, x + 150, y + 34], radius=8, fill=WHITE)
    draw.polygon([(x + 62, y + 34), (x + 74, y + 34), (x + 62, y + 44)], fill=WHITE)
    draw.text((x + 64, y + 12), "CLAIM", font=font(SANS_B, 14), fill=RED)
    draw.text((x + 160, y + 10), "REPORTS SAY", font=font(SANS_B, 11), fill=(200, 190, 220))
    draw.text((x + 8, y + h - 18), "TEHRAN DENIES IT", font=font(SANS_B, 10), fill=(200, 190, 220))


LEAD_ILLOS = [illo_summit, illo_gta_lead, illo_ant]
SEC_ILLOS = [illo_icj, illo_cop31, illo_cyclone, illo_ukraine,
             illo_declaration, illo_florida, illo_suneung, illo_iran_claim]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.text((8, 6), "THE WORLD IN ONE DAY", font=font(SANS_B, 12), fill=RED)
    d.text((W - 8, 6), "THURSDAY'S NEWS \u00b7 ONE PAGE \u00b7 35 STORIES",
           font=font(SANS_B, 11), fill=MUTED, anchor="ra")
    d.line([(8, 26), (W - 8, 26)], fill=INK, width=2)
    d.text((8, 30), "Thursday 19 November 2026", font=font(SERIF_B, 54), fill=INK)
    # calendar badge
    d.rectangle([W - 66, 30, W - 8, 84], outline=RED, width=2)
    d.text((W - 37, 32), "19", font=font(SANS_B, 26), fill=RED, anchor="ma")
    d.text((W - 37, 62), "NOV", font=font(SANS_B, 12), fill=RED, anchor="ma")
    d.text((8, 92), "Three leaders meet in Shenzhen \u00b7 The biggest IPO ever debuts \u00b7 A court rules on Myanmar",
           font=font(SERIF, 15), fill=RED)
    d.line([(8, 116), (W - 8, 116)], fill=INK, width=2)

    # ---- region bar
    counts = region_counts()
    total = sum(counts.values())
    assert total == 35, f"story count {total} != 35"
    order = ["ASIA", "EUROPE", "AMERICAS", "AFRICA", "MIDDLE EAST", "OCEANIA", "GLOBAL"]
    x = 8
    for region in order:
        label = f"{region} {counts[region]}"
        tw = d.textlength(label, font=font(SANS_B, 10)) + 16
        d.rectangle([x, 118, x + tw, 132], fill=REGION_COLORS[region])
        d.text((x + 8, 119), label, font=font(SANS_B, 10), fill=WHITE)
        x += tw + 2

    # ---- timeline strip (two rows of four)
    d.rectangle([0, 126, W, 164], fill=(235, 230, 215))
    d.text((14, 130), "THE DAY IN UTC", font=font(SANS_B, 11), fill=RED)
    for row_i in range(2):
        tx = 130 if row_i == 0 else 14
        ty = 130 if row_i == 0 else 147
        for time, label in TIMELINE[row_i * 4:(row_i + 1) * 4]:
            d.text((tx, ty), time, font=font(SANS_B, 10), fill=RED)
            tw = d.textlength(time, font=font(SANS_B, 10))
            d.text((tx + tw + 5, ty), label, font=font(SANS, 10), fill=INK)
            tx += tw + 5 + d.textlength(label, font=font(SANS, 10)) + 22
    d.line([(0, 164), (W, 164)], fill=LINE, width=1)

    # ---- three leads
    lw = 330
    for i, (region, topic, head, summ, src) in enumerate(LEADS):
        lx = 8 + i * (lw + 4)
        ly = 168
        LEAD_ILLOS[i](d, lx, ly, lw, 120)
        d.text((lx, ly + 124), f"{i + 1}  {region} \u00b7 {topic}",
               font=font(SANS_B, 10), fill=REGION_COLORS[region])
        y = text_block(d, lx, ly + 140, head, font(SERIF_B, 20), INK, lw, 23, max_lines=2)
        text_block(d, lx, y + 2, summ, font(SANS, 12), INK, lw, 15, max_lines=2)
        d.text((lx, 452), src, font=font(SANS_B, 9), fill=MUTED)

    d.line([(8, 460), (W - 8, 460)], fill=INK, width=2)

    # ---- eight secondaries, two rows of four (124px pitch, one-line summaries)
    sw = 248
    for row in range(2):
        for col in range(4):
            i = row * 4 + col
            region, topic, head, summ, src = SECONDARIES[i]
            sx = 8 + col * (sw + 4)
            sy = 464 + row * 124
            SEC_ILLOS[i](d, sx, sy, sw, 58)
            d.text((sx, sy + 62), f"{i + 4}  {region} \u00b7 {topic}",
                   font=font(SANS_B, 9), fill=REGION_COLORS[region])
            y = text_block(d, sx, sy + 76, head, font(SERIF_B, 14), INK, sw, 16, max_lines=2)
            text_block(d, sx, y + 1, summ, font(SANS, 10), MUTED, sw, 13, max_lines=1)

    d.line([(8, 716), (W - 8, 716)], fill=INK, width=2)

    # ---- briefs
    d.text((8, 722), "ALSO ON THURSDAY 19 NOVEMBER", font=font(SANS_B, 12), fill=NAVY)
    bw = 330
    for col in range(3):
        bx = 8 + col * (bw + 6)
        for r in range(8):
            i = col * 8 + r
            place, brief = BRIEFS[i]
            by = 742 + r * 25
            d.text((bx, by), str(12 + i), font=font(SANS_B, 11), fill=REGION_COLORS[BRIEF_REGIONS[i]])
            d.text((bx + 24, by), f"{place}: ", font=font(SANS_B, 11), fill=INK)
            pw = d.textlength(f"{place}: ", font=font(SANS_B, 11))
            text_block(d, bx + 24 + pw, by, brief, font(SANS, 11), INK, bw - 24 - pw, 14, max_lines=1)

    # ---- date check box
    d.rectangle([8, 934, W - 8, 980], outline=RED, width=2)
    d.text((16, 938), "DATE CHECK", font=font(SANS_B, 11), fill=RED)
    dc = ("Left out, first reported on Wednesday 18 November: the Iranian drone interceptions \u00b7 the EU's proposed \u20ac45bn loan for Ukraine \u00b7 "
          "the House Democrats' 251-11 vote for Jeffries \u00b7 Voyager 1 crossing one light-day (10:16 GMT Wednesday) \u00b7 Peltola's Alaska win. "
          "Tuesday 17 November: the US strike on Qeshm \u00b7 the Kerch Bridge collapse. "
          "Not yet news on Thursday: Cyclone Akvan's landfall (Fri 20 Nov) \u00b7 the COP31 close (Fri 21 Nov).")
    text_block(d, 16, 954, dc, font(SANS, 10), INK, W - 32, 13, max_lines=2)

    # ---- footer
    d.text((8, 988), "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 DW \u00b7 Yonhap \u00b7 NWS \u00b7 IMD \u00b7 UNFCCC \u00b7 FT \u00b7 Anadolu \u00b7 Nature \u00b7 ICJ",
           font=font(SANS, 9), fill=MUTED)
    d.text((W - 8, 988), "Reads at three sizes: date and leads at thumbnail size \u00b7 all stories at full size.",
           font=font(SANS, 9), fill=MUTED, anchor="ra")

    img.save("entry.png", "PNG", optimize=True)
    print(f"wrote entry.png, size {img.size}, region counts {counts}")


if __name__ == "__main__":
    main()
