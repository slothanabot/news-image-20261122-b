#!/usr/bin/env python3
"""The World in One Map - 22 November 2026.

A world-map-centred summary of Sunday 22 November 2026: a large simplified
world map with 34 numbered location pins, 34 numbered story callouts arranged
below it, a masthead naming the day, and a bottom ticker of sport scores and
Friday market moves. Pure standard library only; writes a deterministic
1024x1024 PNG to $MAKEFUN_OUTPUT_DIR/entry.png (else /output/entry.png).
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)   # newsprint cream
INK = (24, 32, 48)        # near-black navy ink
NAVY = (18, 42, 76)       # masthead / ticker navy
RED = (178, 34, 34)       # pin + accent red
OCEAN = (198, 216, 228)   # pale sea blue
LAND = (216, 205, 168)    # pale map land
LAND_LINE = (120, 110, 80)
GRAT = (170, 190, 205)    # graticule
GREY = (90, 96, 110)      # secondary text
WHITE = (255, 255, 255)
GOLD = (176, 141, 60)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 bits (MSB = leftmost column).
FONT = {
    "A": [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "B": [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
    "C": [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
    "D": [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
    "E": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
    "F": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
    "G": [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F],
    "H": [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "I": [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "J": [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
    "K": [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
    "L": [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
    "M": [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
    "N": [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
    "O": [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "P": [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
    "Q": [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
    "R": [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
    "S": [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
    "T": [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    "U": [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "V": [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
    "W": [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],
    "X": [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
    "Y": [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
    "Z": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
    "0": [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
    "1": [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "2": [0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F],
    "3": [0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E],
    "4": [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
    "5": [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
    "6": [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
    "7": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
    "8": [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
    "9": [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
    " ": [0, 0, 0, 0, 0, 0, 0],
    ".": [0, 0, 0, 0, 0, 0x0C, 0x0C],
    ",": [0, 0, 0, 0, 0x0C, 0x04, 0x08],
    ":": [0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0],
    ";": [0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08],
    "'": [0x04, 0x04, 0x08, 0, 0, 0, 0],
    "-": [0, 0, 0, 0x1F, 0, 0, 0],
    "!": [0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04],
    "?": [0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04],
    "/": [0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10],
    "(": [0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02],
    ")": [0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08],
    "&": [0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D],
    "%": [0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13],
    "+": [0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0],
    "=": [0, 0, 0x1F, 0, 0x1F, 0, 0],
    "$": [0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04],
    "*": [0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0],
}

# ---------------------------------------------------------------- canvas
img = bytearray(W * H * 3)


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        img[i], img[i + 1], img[i + 2] = color


def fill_rect(x0, y0, x1, y1, color):
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W, x1)
    y1 = min(H, y1)
    for y in range(y0, y1):
        base = (y * W + x0) * 3
        for x in range(x0, x1):
            i = base + (x - x0) * 3
            img[i], img[i + 1], img[i + 2] = color


def hline(x0, x1, y, color):
    for x in range(min(x0, x1), max(x0, x1) + 1):
        px(x, y, color)


def vline(x, y0, y1, color):
    for y in range(min(y0, y1), max(y0, y1) + 1):
        px(x, y, color)


def line(x0, y0, x1, y1, color):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def disc(cx, cy, r, color):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                px(x, y, color)


def ring(cx, cy, r, color):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = (x - cx) ** 2 + (y - cy) ** 2
            if r * r - 2 * r <= d <= r * r:
                px(x, y, color)


def fill_poly(points, color):
    """Scanline even-odd fill for a list of (x, y) points."""
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
        nodes = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                nodes.append(int(x0 + (y - y0) * (x1 - x0) / (y1 - y0)))
        nodes.sort()
        for k in range(0, len(nodes) - 1, 2):
            for x in range(nodes[k], nodes[k + 1] + 1):
                px(x, y, color)


def poly_outline(points, color):
    n = len(points)
    for i in range(n):
        line(points[i][0], points[i][1], points[(i + 1) % n][0],
             points[(i + 1) % n][1], color)


def glyph(ch, x, y, scale, color):
    rows = FONT.get(ch, FONT[" "])
    for r in range(7):
        bits = rows[r]
        for c in range(5):
            if bits & (1 << (4 - c)):
                fill_rect(x + c * scale, y + r * scale,
                          x + (c + 1) * scale, y + (r + 1) * scale, color)


def text_width(s, scale, spacing=None):
    if spacing is None:
        spacing = scale
    return len(s) * (5 * scale + spacing) - spacing


def text(s, x, y, scale=1, color=INK, align="left", spacing=None):
    """Draw uppercase text; returns width drawn. Unknown chars -> space."""
    if spacing is None:
        spacing = scale
    s = s.upper()
    w = text_width(s, scale, spacing)
    if align == "center":
        x -= w // 2
    elif align == "right":
        x -= w
    cx = x
    for ch in s:
        glyph(ch, cx, y, scale, color)
        cx += 5 * scale + spacing
    return w


# ---------------------------------------------------------------- map data
# Simplified continent outlines as (lon, lat) polygons.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80),
     (-80, 73), (-65, 62), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-80, 26), (-85, 20), (-90, 15), (-95, 16), (-100, 20), (-105, 22),
     (-110, 24), (-115, 30), (-120, 34), (-125, 40), (-125, 48), (-135, 58),
     (-150, 60), (-165, 60)],
    # Greenland
    [(-55, 60), (-45, 60), (-40, 65), (-30, 68), (-25, 70), (-35, 76),
     (-55, 76), (-60, 72)],
    # South America
    [(-80, 10), (-75, 11), (-70, 12), (-62, 10), (-55, 6), (-50, 0),
     (-45, -3), (-38, -5), (-35, -8), (-40, -20), (-48, -27), (-55, -35),
     (-62, -41), (-68, -50), (-70, -54), (-73, -50), (-73, -40), (-72, -30),
     (-70, -20), (-75, -15), (-80, -5), (-81, 0), (-80, 5)],
    # Africa
    [(-17, 15), (-15, 27), (-10, 31), (-5, 35), (0, 36), (10, 37), (11, 34),
     (20, 32), (32, 31), (35, 28), (37, 22), (40, 15), (43, 11), (48, 11),
     (51, 10), (46, 5), (41, -2), (40, -10), (35, -18), (32, -26), (28, -33),
     (20, -35), (17, -32), (15, -27), (12, -18), (12, -8), (9, 4), (-8, 4),
     (-13, 8), (-17, 12)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57),
     (10, 59), (5, 60), (5, 62), (12, 65), (18, 69), (25, 71), (30, 70),
     (40, 68), (50, 69), (60, 69), (70, 72), (80, 73), (90, 75), (100, 77),
     (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 70),
     (170, 67), (178, 65), (178, 62), (170, 60), (162, 56), (158, 52),
     (150, 59), (142, 55), (140, 50), (135, 43), (130, 42), (127, 40),
     (122, 38), (120, 32), (115, 23), (110, 20), (108, 18), (105, 10),
     (103, 8), (100, 8), (98, 12), (95, 16), (92, 21), (89, 22), (86, 20),
     (82, 17), (80, 13), (77, 8), (75, 12), (72, 20), (68, 23), (66, 25),
     (62, 25), (58, 25), (56, 27), (54, 26), (52, 28), (50, 29), (48, 30),
     (44, 29), (40, 31), (36, 36), (33, 36), (30, 36), (27, 37), (23, 36),
     (20, 39), (18, 40), (15, 38), (12, 44), (8, 44), (3, 43), (0, 40),
     (-2, 37), (-6, 36), (-9, 37)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 36), (140, 38),
     (141, 40), (142, 42), (144, 44), (142, 45), (140, 44), (138, 39),
     (136, 37), (133, 35), (131, 33)],
    # Sumatra
    [(95, 5), (100, 0), (104, -4), (106, -6), (101, -3), (97, 2)],
    # Borneo
    [(109, 1), (113, 4), (117, 6), (119, 1), (117, -3), (112, -3), (110, -1)],
    # New Guinea
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (146, -8),
     (141, -8), (136, -6), (132, -4)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20)],
    # New Zealand
    [(167, -45), (170, -42), (174, -40), (176, -38), (178, -38), (174, -41),
     (170, -44), (167, -46)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (44, -25),
     (43, -21)],
]

# Map frame: equirectangular, lon -180..180, lat 90..-60.
MX0, MY0, MW, MH = 40, 102, 944, 392


def project(lon, lat):
    x = MX0 + (lon + 180.0) / 360.0 * MW
    y = MY0 + (90.0 - lat) / 150.0 * MH
    return int(round(x)), int(round(y))


# Stories: (headline, caption, lon, lat, dx, dy) - dx/dy nudge the pin so
# crowded regions stay readable; a thin leader joins pin to true spot.
STORIES = [
    ("IRAN HITS US GULF BASES", "IRGC: MISSILES, DRONES HIT PATRIOT RADARS", 50.5, 26.2, -16, 14),
    ("LVIV BLAST KILLS TWO", "RUSSIAN MISSILE HITS HOMES; 10 HURT", 24.0, 49.8, 20, -18),
    ("RUSSIA'S BIGGEST RAID", "400 DRONES, 110 MISSILES IN ONE NIGHT", 30.5, 50.4, 30, -20),
    ("DRONES HIT RUSSIAN SHIP", "BALTIC CARGO VESSEL STRUCK; FINLAND ALERT", 21.0, 59.0, -30, -4),
    ("MISSILE LANDS IN POLAND", "WARSAW CALLS IT PROVOCATION; NATO ALERT", 19.0, 52.0, 8, -26),
    ("ESTONIA SHUTS BORDER", "TALLINN TO CLOSE RUSSIA FRONTIER", 25.0, 58.5, -20, -6),
    ("ZELENSKYY: NATO IS KEY", "KYIV REPEATS ALLIANCE BID AS BEST SHIELD", 31.5, 48.5, 22, 16),
    ("TRUMP: IRAN DEAL 20 YRS", "CLAIMS TEHRAN LEADERSHIP REMOVED TWICE", -80.0, 35.0, -14, -10),
    ("MELANIA PUSHES TRUCES", "WANTS MORE UKRAINE CEASEFIRES BY XMAS", -74.0, 40.7, 14, -8),
    ("UN FAILS ON ROBOT ARMS", "NO BINDING RULES FOR AUTONOMOUS WEAPONS", 6.1, 46.2, -26, 6),
    ("COP31 IN OVERTIME", "CLIMATE SUMMIT DEADLOCKED ON FOSSIL FUELS", 32.8, 39.9, 18, -16),
    ("EU-INDONESIA TRADE DEAL", "TEN YEARS OF TALKS; 98.5% TARIFFS TO GO", 4.4, 50.8, -22, -18),
    ("HONG KONG GOES TO POLLS", "5,700 ELECTORS CHOOSE ELECTION COMMITTEE", 114.2, 22.3, 14, -14),
    ("TRUMP-XI MEET IN SHENZHEN", "SUMMIT FALLOUT; JAPAN'S TAKAICHI PRESSED", 113.3, 22.4, -14, 14),
    ("ISRAEL COALITION TALKS", "EISENKOT INVITES LIKUD TO NEGOTIATE", 34.8, 32.1, 16, 14),
    ("US AIRLINES ON ALERT", "AL-QAEDA-LINKED THREAT BEFORE THANKSGIVING", -87.0, 41.9, -18, 12),
    ("TANKERS HIT OFF OMAN", "IRAN-US NAVAL TENSIONS FLARE IN THE GULF", 59.0, 22.5, 22, -12),
    ("PATRIOT CRASH PROBED", "BAHRAIN PROBES WRECK AMID DRONE REPORTS", 52.0, 24.0, 0, 26),
    ("PERU QUAKE M6.9", "ANDES SHAKE; NO DAMAGE OR CASUALTIES", -75.0, -13.0, 0, 0),
    ("MYANMAR QUAKE M4.1", "EARLY-HOURS TREMOR NEAR NAYPYITAW", 96.0, 20.0, -14, -14),
    ("SUDAN: BAU FALLS", "TASIS ALLIANCE SEIZES KEY BLUE NILE REGION", 33.5, 11.5, 0, 0),
    ("'EL CHAPO ISIDRO' SEIZED", "MEXICO NABS FBI-WANTED BOSS; 11 DIE", -107.0, 24.8, 0, 0),
    ("TOXIC LIQUOR KILLS 11", "ILLICIT ALCOHOL SICKENS 180 IN MANIPUR", 94.0, 24.5, 16, 0),
    ("PAKISTAN BLAST KILLS 5", "SUICIDE CAR BOMB AT CHECKPOINT; 13 HURT", 70.0, 32.0, 0, 0),
    ("BOLSONARO IN ICU", "JAILED EX-PRESIDENT IN CARE, BOWEL BLOCKAGE", -47.9, -15.8, 0, 0),
    ("ZAGREB MARCHES", "CROATS DEMAND JUSTICE AFTER HOSPITAL DEATH", 16.0, 45.8, -8, 22),
    ("DENMARK EXPELS RUSSIAN", "ENVOY OUSTED OVER PLOT TO KILL RAPPER", 12.6, 55.7, -24, -20),
    ("TAIWAN TURNS TO DRONES", "ISLANDERS EMBRACE DRONE WARFARE", 121.0, 23.5, 20, -20),
    ("MODI OPENS NITISH SETU", "NEW BRIDGE LINKS PATNA AND VAISHALI", 85.1, 25.6, 0, -14),
    ("CYCLONE AKVAN AFTERMATH", "14 RANCHI FLIGHTS AXED; 300,000 SHELTERED", 85.8, 20.3, 10, 18),
    ("INDONESIA RAIN ALERT", "BMKG WARNS 12 PROVINCES; W. KALIMANTAN ALERT", 114.0, -1.0, 0, 0),
    ("UAE HOSTS US MINISTER", "MBZ RECEIVES HOMELAND SECURITY'S MULLIN", 54.4, 24.5, -20, -6),
    ("FINLAND: WAR AT OUR DOOR", "PM ORPO WARNS AFTER BALTIC DRONE STRIKE", 25.0, 60.2, 0, -28),
    ("IRAN: US BLOCKADE HOSTILE", "DEPUTY FM CONDEMNS SANCTIONS SQUEEZE", 51.4, 35.7, 12, -18),
]

OCEAN_LABELS = [("PACIFIC", -150, 0), ("ATLANTIC", -30, 10),
                ("INDIAN", 75, -25), ("PACIFIC", 155, -30)]
LAND_LABELS = [("NORTH AMERICA", -100, 55), ("SOUTH AMERICA", -58, -32),
               ("AFRICA", 18, 5), ("EUROPE", 15, 55), ("ASIA", 90, 55),
               ("AUSTRALIA", 134, -25)]

TICKER_1 = "MADRID 2-1 CELTA - NEWCASTLE 2-2 ARSENAL - NAPOLI 1-0 TORINO - PSG 3-2 NICE"
TICKER_2 = "ZVEREV 7-6 6-4 MEDVEDEV - 76ERS 132-129 BUCKS - VERSTAPPEN ON LAS VEGAS POLE"
FOOTER = "MARKETS FRI: NIKKEI -5.06% - KOSPI -5.21% - GOLD $3,586.90 - CANES 7-4 OILERS - 34 STORIES - 22 NOV 2026"


# ---------------------------------------------------------------- drawing
def draw():
    fill_rect(0, 0, W, H, PAPER)

    # ---- masthead
    fill_rect(0, 0, W, 4, RED)
    text("THE WORLD IN ONE MAP", W // 2, 14, scale=5, color=NAVY, align="center")
    text("SUNDAY 22 NOVEMBER 2026", W // 2, 56, scale=3, color=RED, align="center")
    text("34 STORIES FROM ONE DAY - EVERY PIN A PLACE, EVERY NUMBER A HEADLINE",
         W // 2, 82, scale=1, color=GREY, align="center")
    hline(40, W - 40, 96, NAVY)

    # ---- map panel
    fill_rect(MX0, MY0, MX0 + MW, MY0 + MH, OCEAN)
    # graticule every 30 degrees
    for lon in range(-150, 181, 30):
        x, _ = project(lon, 90)
        vline(x, MY0, MY0 + MH - 1, GRAT)
    for lat in range(60, -61, -30):
        _, y = project(0, lat)
        hline(MX0, MX0 + MW - 1, y, GRAT)
    # land
    for poly in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in poly]
        fill_poly(pts, LAND)
        poly_outline(pts, LAND_LINE)
    # ocean + continent labels
    for name, lon, lat in OCEAN_LABELS:
        x, y = project(lon, lat)
        text(name, x, y, scale=1, color=(96, 120, 140), align="center")
    for name, lon, lat in LAND_LABELS:
        x, y = project(lon, lat)
        text(name, x, y, scale=1, color=(110, 100, 70), align="center")
    # map frame
    for x in (MX0, MX0 + MW - 1):
        vline(x, MY0, MY0 + MH - 1, NAVY)
    for y in (MY0, MY0 + MH - 1):
        hline(MX0, MX0 + MW - 1, y, NAVY)

    # ---- pins (drawn after land so they sit on top)
    pin_pos = []
    for i, (_h, _c, lon, lat, dx, dy) in enumerate(STORIES, start=1):
        x, y = project(lon, lat)
        px_, py_ = x + dx, y + dy
        pin_pos.append((px_, py_))
        if dx or dy:
            line(x, y, px_, py_, RED)
            disc(x, y, 2, RED)
        disc(px_, py_, 9, RED)
        ring(px_, py_, 9, WHITE)
        num = str(i)
        text(num, px_, py_ - 4, scale=1, color=WHITE, align="center")

    # ---- story grid: 3 columns x 12 rows
    gy0, row_h = 506, 36
    col_x = [24, 352, 680]
    for idx, (headline, caption, _lo, _la, _dx, _dy) in enumerate(STORIES):
        col = idx // 12
        row = idx % 12
        x = col_x[col]
        y = gy0 + row * row_h
        # number badge
        fill_rect(x, y + 1, x + 22, y + 23, RED)
        text(str(idx + 1), x + 11, y + 8, scale=1, color=WHITE, align="center")
        # headline (scale 2) + caption (scale 1)
        text(headline[:24], x + 28, y + 2, scale=2, color=INK)
        text(caption[:48], x + 28, y + 21, scale=1, color=GREY)

    # ---- bottom ticker
    fill_rect(0, 944, W, 1014, NAVY)
    text(TICKER_1, W // 2, 951, scale=2, color=WHITE, align="center", spacing=1)
    text(TICKER_2, W // 2, 970, scale=2, color=(255, 214, 130), align="center", spacing=1)
    text(FOOTER, W // 2, 992, scale=1, color=WHITE, align="center")
    fill_rect(0, 1012, W, 1015, GOLD)
    text("THE WORLD IN ONE MAP - SUNDAY 22 NOVEMBER 2026",
         W // 2, 1016, scale=1, color=GREY, align="center")


# ---------------------------------------------------------------- PNG out
def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += img[y * W * 3:(y + 1) * W * 3]

    def chunk(ctype, data):
        out = struct.pack(">I", len(data)) + ctype + data
        out += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    draw()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes())
    print("wrote", path)


if __name__ == "__main__":
    main()
