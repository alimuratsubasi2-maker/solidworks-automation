"""FPV drone'un 10 parcasini AYRI AYRI .SLDPRT olarak sifirdan cizer.
Olculer/yerel eksenler referans zip'teki parcalarla uyumlu (montaj icin).
Kullanim: python drone_parcalar.py [sira numaralari]"""
import math
import os
import sys
import time
import traceback

from swlib import connect, Part

HEDEF = os.path.join(os.path.expanduser("~"), "Desktop", "solıd yapay zeka drone tasarlama")
ONIZ = os.path.join(HEDEF, "_onizlemeler")

TURUNCU = (0.95, 0.47, 0.08)
SIYAH = (0.08, 0.08, 0.09)
ALTIN = (0.85, 0.65, 0.15)
PIRINC = (0.72, 0.56, 0.18)
CELIK = (0.70, 0.71, 0.74)


def ngon(n, r, cx=0.0, cy=0.0, phase=0.0):
    return [(cx + r * math.cos(phase + 2 * math.pi * i / n), cy + r * math.sin(phase + 2 * math.pi * i / n))
            for i in range(n)]


def rounded_rect(p, w, h, r, cx=0.0, cy=0.0):
    a, b = w / 2, h / 2
    L = lambda x1, y1, x2, y2: p.sm.CreateLine((cx + x1) / 1000, (cy + y1) / 1000, 0, (cx + x2) / 1000, (cy + y2) / 1000, 0)
    A = lambda ox, oy, x1, y1, x2, y2: p.arc(cx + ox, cy + oy, cx + x1, cy + y1, cx + x2, cy + y2, ccw=True)
    L(-a + r, -b, a - r, -b); A(a - r, -b + r, a - r, -b, a, -b + r)
    L(a, -b + r, a, b - r);   A(a - r, b - r, a, b - r, a - r, b)
    L(a - r, b, -a + r, b);   A(-a + r, b - r, -a + r, b, -a, b - r)
    L(-a, b - r, -a, -b + r); A(-a + r, -b + r, -a, -b + r, -a + r, -b)


def ypl(p, y):
    return p.plane(f"Y{y}", "top", y).Name


# ---------------------------------------------------------------- parcalar
def arm(p):
    # yan profil (Sag duzlem: eskiz x = -Z, y = Y); kol -Z yonunde uzanir
    p.sketch("right"); p.rect(0, 0, 12, 20); p.end_sketch()
    p.extrude(18)                                            # baglanti blogu x 0..18
    p.plane("X4", "right", 4)
    p.sketch("X4"); p.rect(12, 0, 80, 9); p.end_sketch()
    p.extrude(10, merge=True)                                # kafes kiris x 4..14
    p.sketch("top"); p.circle(9, 84.7, 9.5); p.end_sketch()
    p.extrude(4, merge=True)                                 # motor tablasi
    p.sketch("X4")
    for i in range(8):
        x0 = 15 + i * 8
        if i % 2 == 0:
            p.poly([(x0, 1.8), (x0 + 6, 1.8), (x0 + 3, 7.2)])
        else:
            p.poly([(x0, 7.2), (x0 + 6, 7.2), (x0 + 3, 1.8)])
    p.end_sketch(); p.cut(through=True)                      # ucgen bosluklar
    p.sketch("top")
    p.circle(9, 84.7, 2.5)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        p.circle(9 + 5.5 * math.cos(a), 84.7 + 5.5 * math.sin(a), 1.2)
    p.rect(6, 0, 12, 12)
    p.end_sketch(); p.cut(through=True)                      # motor delikleri + catal yarigi
    p.sketch("right"); p.circle(6, 14, 1.6); p.end_sketch(); p.cut(through=True)
    p.style_all(TURUNCU, shine=0.5)


def base(p):
    s, c = 36.1, 11
    p.sketch("top")
    p.poly([(-s + c, -s), (s - c, -s), (s, -s + c), (s, s - c), (s - c, s), (-s + c, s), (-s, s - c), (-s, -s + c)])
    p.end_sketch(); p.extrude(4)
    p.sketch("top")
    p.rect(-10, 21, 10, 27); p.rect(-10, -27, 10, -21); p.rect(21, -10, 27, 10); p.rect(-27, -10, -21, 10)
    p.circle(0, 0, 6)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.circle(sx * 22.6, sy * 31.1, 1.6); p.circle(sx * 31.1, sy * 22.6, 1.6)
            p.circle(sx * 15.3, sy * 15.3, 1.6)
    p.end_sketch(); p.cut(through=True)
    ypl(p, 4)
    p.sketch("Y4")
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.circle(sx * 15.3, sy * 15.3, 4); p.circle(sx * 15.3, sy * 15.3, 1.6)
    p.end_sketch(); p.extrude(1.5, merge=True)
    p.style_all(TURUNCU, shine=0.5)


def battery_case(p):
    p.sketch("front"); rounded_rect(p, 71, 18.6, 5); rounded_rect(p, 68.6, 16.2, 3.8); p.end_sketch()
    p.extrude(34)
    p.style_all((0.05, 0.18, 0.92), shine=0.7)


def blade(p):
    p.sketch("top"); p.circle(0, 0, 2.9); p.end_sketch(); p.extrude(3)
    leaf = [(-1.3, 1.5), (1.4, 2.2), (2.6, 7.5), (2.0, 13.5), (0.6, 14.6), (-0.6, 13.8), (-1.2, 8.0)]
    ypl(p, 1)
    p.sketch("Y1")
    p.poly(leaf)
    p.poly([(-x, -y) for x, y in leaf])
    p.end_sketch(); p.extrude(0.8, merge=True)
    p.style_all((0.80, 0.80, 0.82), shine=0.6)


def electrical_conductor(p):
    p.sketch("top"); rounded_rect(p, 26, 18, 3); p.end_sketch()
    p.style(p.extrude(7, reverse=True), "ESC Govde", (0.85, 0.05, 0.05), shine=0.8)
    p.sketch("right"); p.circle(-4.5, -3.5, 1.8); p.circle(4.5, -3.5, 1.8); p.end_sketch()
    p.extrude(32, mid=True)
    p.sketch("right"); p.rect(-3, -4.5, 3, -2.5); p.end_sketch()
    p.extrude(36, mid=True)
    p.style_all(ALTIN, shine=0.9)


def electrical_unit2(p):
    p.sketch("right"); p.rect(-14, 2, 0, 4.5); p.end_sketch()
    p.style(p.extrude(5, mid=True), "Plastik Govde", SIYAH, shine=0.3)
    zs = [1.27 + 2.54 * i for i in range(6)]
    h = 0.32
    p.sketch("top")
    for z in zs:
        p.rect(1.27 - h, -z - h, 1.27 + h, -z + h)
    p.end_sketch(); p.extrude(10.7)
    p.sketch("top")
    for z in zs:
        p.rect(-1.27 - h, -z - h, -1.27 + h, -z + h)
    p.end_sketch(); p.extrude(8.5 + h)
    p.sketch("right")
    for z in zs:
        p.rect(-z - h, 8.5 - h, -z + h, 8.5 + h)
    p.end_sketch(); p.extrude(9.4, reverse=True)
    p.style_all(ALTIN, shine=0.9)


def motor(p):
    prof = [(0, -1.8), (11.3, -1.8), (11.3, 0.5), (10.4, 1.0), (10.4, 2.0), (11.3, 2.5), (11.3, 5),
            (10.9, 5.4), (11.3, 5.8), (11.3, 19.5), (9.5, 22), (0, 22)]
    p.sketch("front"); p.centerline(0, -5, 0, 30); p.poly(prof); p.end_sketch()
    p.revolve()
    ypl(p, 22)
    p.sketch("Y22")
    for k in range(6):
        a = k * math.pi / 3
        p.circle(6 * math.cos(a), 6 * math.sin(a), 1.9)
    p.circle(0, 0, 2.6)
    p.end_sketch(); p.cut(4, reverse=True)
    p.style_all(SIYAH, shine=0.4)
    p.sketch("front"); p.centerline(0, -5, 0, 30); p.poly([(0, 16.5), (10, 16.5), (10, 19), (0, 19)]); p.end_sketch()
    p.style(p.revolve(), "Stator", TURUNCU, shine=0.5)
    p.sketch("front"); p.centerline(0, -5, 0, 30); p.poly([(0, 17), (1.5, 17), (1.5, 21.5), (0, 21.5)]); p.end_sketch()
    p.style(p.revolve(), "Mil", CELIK, shine=0.9)


def perforated_tube(p):
    p.sketch("right"); p.circle(0, 0, 8.5); p.circle(0, 0, 7.5); p.end_sketch()
    p.extrude(150, mid=True)
    p.sketch("top")
    for i in range(21):
        p.circle(-70 + 7 * i, 0, 1.2)
    p.end_sketch(); p.cut(both=True)
    p.sketch("front")
    for i in range(20):
        p.circle(-66.5 + 7 * i, 0, 1.2)
    p.end_sketch(); p.cut(both=True)
    p.style_all(CELIK, shine=0.7)


def piller(p):
    p.sketch("top"); p.poly(ngon(6, 2.9, phase=math.pi / 2)); p.end_sketch()
    p.style(p.extrude(7, reverse=True), "Altigen Ara Direk", PIRINC, shine=0.8)
    p.sketch("top"); p.circle(0, 0, 1.5); p.end_sketch()
    p.style(p.extrude(11.3, reverse=True), "Vida Ucu", CELIK, shine=0.8)
    p.sketch("top"); p.circle(0, 0, 1.4); p.end_sketch(); p.cut(4, reverse=True)


def spacer(p):
    p.sketch("top"); p.circle(0, 0, 2.5); p.circle(0, 0, 1.6); p.end_sketch()
    p.extrude(6, reverse=True)
    p.style_all(CELIK, shine=0.6)


PARCALAR = [
    ("Arm", arm),
    ("Base", base),
    ("Battery Case", battery_case),
    ("Blade", blade),
    ("Electrical Conductor", electrical_conductor),
    ("Electrical Unit II", electrical_unit2),
    ("Motor", motor),
    ("Perforated Tube", perforated_tube),
    ("Piller", piller),
    ("Spacer", spacer),
]


def main():
    sec = [int(a) for a in sys.argv[1:]] or list(range(1, len(PARCALAR) + 1))
    os.makedirs(ONIZ, exist_ok=True)
    sw = connect()
    sw.CloseAllDocuments(True)
    ok_say = 0
    for i in sec:
        ad, fn = PARCALAR[i - 1]
        t0 = time.time()
        try:
            p = Part(sw)
            p.iso()
            fn(p)
            p.hide_planes(); p.hide_sketches(); p.iso()
            n = len(p._bodies())
            yol = os.path.join(HEDEF, ad + ".SLDPRT")
            p.m.SaveAs3(yol, 0, 1)
            p.m.SaveBMP(os.path.join(ONIZ, f"{i:02d}.bmp"), 900, 700)
            ok = n > 0 and os.path.exists(yol)
            ok_say += ok
            print(f"{i:2d}. {ad:22s} {'OK' if ok else 'HATA'}  govde={n}  {time.time() - t0:.1f}s", flush=True)
            sw.CloseAllDocuments(True)
        except Exception:
            print(f"{i:2d}. {ad:22s} HATA")
            traceback.print_exc()
    print("Basarili:", ok_say, "/", len(sec))


if __name__ == "__main__":
    main()
