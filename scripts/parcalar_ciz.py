"""V6 motorun 27 parcasini AYRI AYRI .SLDPRT olarak sifirdan cizer.
Dosya adlari referans zip'teki adlarla birebir aynidir.
Kullanim: python parcalar_ciz.py            -> hepsi
          python parcalar_ciz.py 3 8 19     -> sadece bu sira numaralari"""
import glob
import math
import os
import sys
import time
import traceback

from swlib import connect, Part
from v6_motor_ciz import P, pin_pos, piston_s, hull_loop, COL, CYL, PAIRS, DECK, BANK_W, BORE, PISTON

HEDEF = os.path.join(os.path.expanduser("~"), "Desktop", "SOLID PARCALAR")   # kullanici yeniden adlandirdi
ONIZ = os.path.join(HEDEF, "_onizlemeler")


def zpl(p, z):
    return p.plane(f"Z{z}", "front", z)


def ypl(p, y):
    return p.plane(f"Y{y}", "top", y)


def star(n, r1, r2, phase=0.0):
    pts = []
    for i in range(2 * n):
        a = phase + math.pi * i / n
        r = r1 if i % 2 == 0 else r2
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def ngon(n, r, cx=0.0, cy=0.0, phase=0.0):
    return [(cx + r * math.cos(phase + 2 * math.pi * i / n), cy + r * math.sin(phase + 2 * math.pi * i / n))
            for i in range(n)]


def revolve_y(p, prof, plane="front", merge=True):
    """Y ekseni etrafinda dondur. prof: (yaricap, y) listesi."""
    p.sketch(plane)
    ys = [y for _, y in prof]
    p.centerline(0, min(ys) - 10, 0, max(ys) + 10)
    p.poly([(r, y) for r, y in prof])
    p.end_sketch()
    return p.revolve(merge=merge)


# ------------------------------------------------------------------ parcalar
def engine_block(p):
    p.sketch("front"); p.rect(-115, -70, 115, 50); p.end_sketch()
    p.extrude(300)
    for phi in (30, -30):
        p.sketch("front")
        p.poly([P(phi, 30, -BANK_W), P(phi, DECK, -BANK_W), P(phi, DECK, BANK_W), P(phi, 30, BANK_W)])
        p.end_sketch()
        p.extrude(300, merge=True)
    for phi, zs in CYL.items():
        for z in zs:
            zpl(p, z)
            p.sketch(f"Z{z}")
            p.centerline(*P(phi, 0, 0), *P(phi, 260, 0))
            p.poly([P(phi, 70, 0), P(phi, DECK + 10, 0), P(phi, DECK + 10, BORE), P(phi, 70, BORE)])
            p.end_sketch()
            p.revolve(cut=True)
    zpl(p, 10)
    p.sketch("Z10"); p.circle(0, 0, 76); p.end_sketch(); p.cut(280)
    p.sketch("front"); p.circle(0, 0, 26); p.end_sketch(); p.cut(through=True)
    p.style_all(COL["blok"])


def cylinder_head(p):
    p.sketch("front"); p.rect(-60, 0, 60, 42); p.end_sketch()
    p.extrude(280)
    zs = (47, 140, 233)
    p.sketch("top")
    for z in zs:
        p.circle(0, -z, 38)
    p.end_sketch(); p.cut(8)
    p.sketch("top")
    for z in zs:
        p.circle(-16, -z, 10); p.circle(16, -z, 10)
    for z in (12, 93, 187, 268):
        p.circle(-52, -z, 5); p.circle(52, -z, 5)
    p.end_sketch(); p.cut(through=True)
    p.sketch("front"); p.circle(0, 30, 13); p.end_sketch(); p.cut(through=True)
    p.style_all(COL["kapak"])


def crank_shaft(p):
    p.sketch("front"); p.circle(0, 0, 24); p.end_sketch()
    p.extrude(315, depth2=45)
    for zc, th in PAIRS:
        c = pin_pos(th)
        zpl(p, zc)
        p.sketch(f"Z{zc}"); p.circle(c[0], c[1], 19); p.end_sketch()
        p.extrude(44, mid=True, merge=True)
        a = math.radians(th)
        e = (math.sin(a), math.cos(a))
        q = (e[1], -e[0])
        loc = [(62, -23), (62, 23), (0, 30), (-30, 45), (-46, 20), (-46, -20), (-30, -45), (0, -30)]
        pts = [(x * e[0] + y * q[0], x * e[1] + y * q[1]) for x, y in loc]
        for dz in (-28, 28):
            zpl(p, zc + dz)
            p.sketch(f"Z{zc + dz}"); p.poly(pts); p.end_sketch()
            p.extrude(12, mid=True, merge=True)
    p.style_all(COL["krank"], shine=0.7)


def ring(p, ro, ri, length, plane="front", **kw):
    p.sketch(plane); p.circle(0, 0, ro); p.circle(0, 0, ri); p.end_sketch()
    return p.extrude(length, **kw)


def crank_bushings(p):
    ring(p, 28, 24.5, 22)
    ring(p, 34, 24.5, 3, merge=True)
    p.style_all((0.78, 0.55, 0.25), shine=0.8)


def cam_shaft(p):
    p.sketch("front"); p.circle(0, 0, 11); p.end_sketch()
    p.extrude(280, depth2=20)
    for i in range(6):
        for j, dz in enumerate((0, 16)):
            z = 25 + i * 42 + dz
            th = math.radians(i * 120 + j * 90)
            pts = []
            for k in range(36):
                a = 2 * math.pi * k / 36
                r = 17 + 9 * max(0.0, math.cos(a - th)) ** 3
                pts.append((r * math.sin(a), r * math.cos(a)))
            zpl(p, z)
            p.sketch(f"Z{z}"); p.poly(pts); p.end_sketch()
            p.extrude(12, mid=True, merge=True)
    for z in (5, 96, 180, 270):
        zpl(p, z)
        p.sketch(f"Z{z}"); p.circle(0, 0, 16); p.end_sketch()
        p.extrude(10, mid=True, merge=True)
    p.style_all(COL["krank"], shine=0.8)


def cam_shaft_retainer(p):
    p.sketch("front")
    p.poly([(-30, -15), (30, -15), (36, -8), (36, 8), (30, 15), (-30, 15), (-36, 8), (-36, -8)])
    p.circle(0, 0, 11.5); p.circle(-26, 0, 4); p.circle(26, 0, 4)
    p.end_sketch()
    p.extrude(6)
    p.style_all((0.30, 0.30, 0.33))


def cam_bushings(p):
    ring(p, 15, 11.2, 16)
    p.style_all((0.78, 0.55, 0.25), shine=0.8)


def piston(p):
    s0, s1 = 0, 58
    prof = [(0, s0), (PISTON, s0), (PISTON, s1 - 18), (PISTON - 3, s1 - 18), (PISTON - 3, s1 - 15),
            (PISTON, s1 - 15), (PISTON, s1 - 11), (PISTON - 3, s1 - 11), (PISTON - 3, s1 - 8),
            (PISTON, s1 - 8), (PISTON, s1), (0, s1)]
    revolve_y(p, prof)
    p.sketch("front"); p.centerline(0, -20, 0, 70); p.poly([(0, -1), (34, -1), (34, 40), (0, 40)]); p.end_sketch()
    p.revolve(cut=True)
    p.sketch("right"); p.circle(0, 24, 11); p.end_sketch(); p.cut(both=True)
    p.style_all(COL["piston"], shine=0.8)


def connecting_rod(p):
    p.sketch("front"); p.circle(0, 0, 30); p.circle(0, 0, 20); p.end_sketch()
    p.extrude(20, mid=True)
    p.sketch("front"); p.circle(0, 140, 15); p.circle(0, 140, 10); p.end_sketch()
    p.extrude(18, mid=True, merge=True)
    p.sketch("front"); p.rect(-8, 26, 8, 127); p.end_sketch()
    p.extrude(14, mid=True, merge=True)
    p.sketch("front"); p.rect(-38, -6, -28, 6); p.rect(28, -6, 38, 6); p.end_sketch()
    p.extrude(16, mid=True, merge=True)
    p.style_all(COL["biyel"], shine=0.6)


def piston_pin(p):
    ring(p, 11, 6.5, 70, mid=True)
    p.style_all(COL["krom"], shine=0.9)


def piston_rings(p):
    for i, y in enumerate((0, 6, 12)):
        pl = "top" if y == 0 else ypl(p, y).Name
        p.sketch(pl); p.circle(0, 0, 40); p.circle(0, 0, 36.5); p.end_sketch()
        p.extrude(2.5)
    p.sketch("right"); p.rect(-1.5, -2, 1.5, 18); p.end_sketch(); p.cut(through=True)
    p.style_all((0.25, 0.25, 0.28), shine=0.7)


def engine_valve(p):
    prof = [(0, 0), (18, 0), (18, 2), (5, 10), (4, 14), (4, 54), (3, 54), (3, 57), (4, 57), (4, 62), (0, 62)]
    revolve_y(p, prof)
    p.style_all(COL["krom"], shine=0.9)


def rocker_arm(p):
    p.sketch("front"); p.rect(-36, -7, 36, 7); p.end_sketch()
    p.extrude(12, mid=True)
    p.sketch("front"); p.circle(0, 0, 11); p.end_sketch()
    p.extrude(16, mid=True, merge=True)
    p.sketch("front"); p.circle(33, 0, 7); p.end_sketch()
    p.extrude(12, mid=True, merge=True)
    p.sketch("front"); p.circle(-33, 0, 7); p.end_sketch()
    p.extrude(12, mid=True, merge=True)
    p.sketch("front"); p.circle(0, 0, 6); p.circle(-33, 0, 2.5); p.end_sketch(); p.cut(both=True)
    p.style_all((0.45, 0.47, 0.50), shine=0.7)


def rocker_arm_spring(p):
    # tel halkalari ust uste: bobin yay gorunumu
    for i in range(6):
        y = 2 + i * 4.2
        p.sketch("front"); p.centerline(0, -10, 0, 60); p.circle(12, y, 1.9); p.end_sketch()
        p.revolve(merge=True)
    p.style_all((0.15, 0.15, 0.16), shine=0.8)


def intake_manifold(p):
    Y0 = 195
    p.sketch("front"); p.poly([(-40, 0), (40, 0), (48, 45), (-48, 45)]); p.end_sketch()
    p.extrude(270)
    for phi, zs in CYL.items():
        sg = 1 if phi > 0 else -1
        for z in zs:
            zl = z - 15
            zpl(p, zl)
            a, b = (40 * sg, 205 - Y0), (46 * sg, 232 - Y0)
            c, d = P(phi, 252, -58), P(phi, 238, -58)
            p.sketch(f"Z{zl}")
            p.poly([a, (d[0], d[1] - Y0), (c[0], c[1] - Y0), b])
            p.end_sketch()
            p.extrude(30, mid=True, merge=True)
    p.sketch("front"); p.circle(-22, 20, 15); p.circle(22, 20, 15); p.end_sketch()
    p.extrude(40, reverse=True, merge=True)
    p.style_all(COL["manifold"], shine=0.6)


def exhaust(p, sg):
    p.sketch("front"); p.circle(0, 0, 17); p.end_sketch()
    p.extrude(340)
    for z in (33, 128, 223):
        zpl(p, z)
        p.sketch(f"Z{z}"); p.poly([(0, -12), (-36 * sg, -12), (-36 * sg, 12), (0, 12)]); p.end_sketch()
        p.extrude(26, mid=True, merge=True)
    zpl(p, 5)
    p.sketch("Z5"); p.poly([(-40 * sg, -22), (-34 * sg, -22), (-34 * sg, 22), (-40 * sg, 22)]); p.end_sketch()
    p.extrude(260, merge=True)
    p.style_all(COL["egzoz"], shine=0.8)


def air_turbo(p):
    p.sketch("front"); p.circle(0, 0, 50); p.end_sketch(); p.extrude(40)
    zpl(p, 40)
    p.sketch("Z40"); p.circle(0, 0, 28); p.end_sketch(); p.extrude(40, merge=True)
    zpl(p, 80)
    p.sketch("Z80"); p.circle(0, 0, 46); p.end_sketch(); p.extrude(34, merge=True)
    p.sketch("right"); p.circle(-20, 32, 15); p.end_sketch(); p.extrude(95, merge=True)
    p.sketch("top"); p.circle(0, -97, 18); p.end_sketch(); p.extrude(85, reverse=True, merge=True)
    p.sketch("front"); p.circle(0, 0, 32); p.end_sketch(); p.extrude(25, reverse=True, merge=True)
    p.sketch("front"); p.circle(0, 0, 26); p.end_sketch(); p.cut(30, reverse=True)
    zpl(p, 114)
    p.sketch("Z114"); p.circle(0, 0, 30); p.circle(0, 0, 24); p.end_sketch(); p.extrude(22, merge=True)
    p.style_all(COL["manifold"], shine=0.7)


def air_filter(p):
    p.sketch("front"); p.poly(star(24, 48, 42)); p.end_sketch()
    p.style(p.extrude(90, draft=6), "Pileli Filtre", COL["altin"], shine=0.9)
    zpl(p, 90)
    p.sketch("Z90"); p.circle(0, 0, 40); p.end_sketch()
    p.style(p.extrude(8), "Uc Kapak", COL["krom"], shine=0.9)
    p.sketch("front"); p.circle(0, 0, 50); p.circle(0, 0, 26); p.end_sketch()
    p.style(p.extrude(10, reverse=True), "Taban Halkasi", COL["krom"], shine=0.9)
    p.sketch("front"); p.circle(0, 0, 26); p.circle(0, 0, 22); p.end_sketch()
    p.style(p.extrude(45, reverse=True), "Boyun", COL["krom"], shine=0.9)


def belt1(p):
    cams = [P(30, 250, 0), P(-30, 250, 0)]
    p.sketch("front")
    hull_loop(p, [((0, 0), 61), (cams[0], 44), (cams[1], 44)])
    hull_loop(p, [((0, 0), 55.5), (cams[0], 38.5), (cams[1], 38.5)])
    p.end_sketch()
    p.extrude(22)
    p.style_all(COL["kayis"], shine=0.1)


def belt3(p):
    pul = [((0, 0), 60), ((-150, 70), 36)]
    inner = [((0, 0), 55), ((-150, 70), 31)]
    p.sketch("front"); hull_loop(p, pul); hull_loop(p, inner); p.end_sketch()
    p.extrude(18)
    p.style_all(COL["kayis"], shine=0.1)


def valves_cover(p):
    top = [(26, 42)]
    for t in (27, 0, -27):
        top += [(26, t + 3), (32, t + 3), (32, t - 3), (26, t - 3)]
    top += [(26, -42)]
    prof = [(0, -50), (0, 50), (18, 50)] + top + [(18, -50)]
    p.sketch("front"); p.poly([(t, s) for s, t in prof]); p.end_sketch()
    p.style(p.extrude(260), "Kulbutor Kapagi", COL["kulbutor"], shine=0.8)
    zpl(p, 8)
    p.sketch("Z8"); p.rect(-46, -1, 46, 18); p.end_sketch(); p.cut(244)
    ypl(p, 26)
    p.sketch("Y26"); p.circle(13.5, -200, 9); p.end_sketch()
    p.style(p.extrude(14), "Yag Doldurma Kapagi", (0.08, 0.08, 0.08), shine=0.5)


def side_cover(p):
    cams = [P(30, 250, 0), P(-30, 250, 0)]
    p.sketch("front")
    hull_loop(p, [((0, 0), 72), (cams[0], 54), (cams[1], 54)])
    p.circle(0, 0, 20)
    p.end_sketch()
    p.extrude(8)
    p.sketch("front")
    hull_loop(p, [((0, 0), 72), (cams[0], 54), (cams[1], 54)])
    hull_loop(p, [((0, 0), 66), (cams[0], 48), (cams[1], 48)])
    p.end_sketch()
    p.extrude(30, merge=True)
    p.style_all((0.40, 0.41, 0.44), shine=0.5)


def oil_pan(p):
    p.sketch("front"); p.poly([(-108, 0), (108, 0), (96, -65), (-96, -65)]); p.end_sketch()
    p.extrude(270, mid=True)
    p.sketch("top"); p.rect(-100, -127, 100, 127); p.end_sketch(); p.cut(58, reverse=True)
    p.sketch("top"); p.rect(-118, -140, 118, 140); p.rect(-100, -127, 100, 127); p.end_sketch()
    p.extrude(6, merge=True)
    p.style_all(COL["karter"], shine=0.5)


def head_bolt(p):
    p.sketch("top"); p.poly(ngon(6, 9)); p.end_sketch(); p.extrude(8)
    p.sketch("top"); p.circle(0, 0, 11); p.end_sketch(); p.extrude(2, merge=True)
    p.sketch("top"); p.circle(0, 0, 5.5); p.end_sketch(); p.extrude(95, reverse=True, merge=True)
    p.style_all((0.20, 0.20, 0.22), shine=0.7)


def crank_pulley(p):
    zr = [(0, 0), (0, 55), (3, 55), (6, 50), (9, 55), (12, 55), (15, 50), (18, 55), (21, 55), (24, 50),
          (27, 55), (30, 55), (30, 16), (45, 16), (45, 0)]
    p.sketch("right"); p.centerline(10, 0, -60, 0); p.poly([(-z, r) for z, r in zr]); p.end_sketch()
    p.revolve()
    p.sketch("front")
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        p.circle(30 * math.cos(a), 30 * math.sin(a), 4.5)
    p.circle(0, 0, 8)
    p.end_sketch(); p.cut(through=True)
    p.style_all(COL["kasnak"], shine=0.6)


def spark_plug(p):
    metal = [(0, -5), (1.2, -5), (1.2, 0), (7, 0), (7, 19), (9.5, 19), (9.5, 21), (10, 21), (10, 33), (0, 33)]
    p.style(revolve_y(p, metal, merge=False), "Govde", COL["krom"], shine=0.9)
    ins = [(0, 33), (6, 33), (6, 37), (5.2, 39), (6, 41), (5.2, 43), (6, 45), (5.2, 47), (6, 49), (5.2, 51),
           (5.5, 56), (3, 58), (3, 66), (0, 66)]
    p.style(revolve_y(p, ins, merge=False), "Seramik", (0.95, 0.95, 0.93), shine=0.6)


PARCALAR = [
    ("engine block", engine_block),
    ("cylinder head", cylinder_head),
    ("crank shaft", crank_shaft),
    ("crank bushings", crank_bushings),
    ("cam shaft", cam_shaft),
    ("cam shaft retainer", cam_shaft_retainer),
    ("cam bushings", cam_bushings),
    ("piston", piston),
    ("piston Part1", connecting_rod),
    ("piston Part2", piston_pin),
    ("piston   Part3", piston_rings),
    ("engine valve", engine_valve),
    ("rocker arm", rocker_arm),
    ("rocker arm spring", rocker_arm_spring),
    ("INTAKE MANIFOLD", intake_manifold),
    ("exhuast manifold", lambda p: exhaust(p, 1)),
    ("exhaust manifold left", lambda p: exhaust(p, -1)),
    ("air turbo", air_turbo),
    ("engine air filter", air_filter),
    ("engine belt 1", belt1),
    ("engine belt 3", belt3),
    ("valves cover", valves_cover),
    ("SIDE COVER", side_cover),
    ("OIL PAN", oil_pan),
    ("Part     1", head_bolt),
    ("Part    3", crank_pulley),
    ("Part      4", spark_plug),
]


def main():
    sec = [int(a) for a in sys.argv[1:]] or list(range(1, len(PARCALAR) + 1))
    os.makedirs(ONIZ, exist_ok=True)
    sw = connect()
    sw.CloseAllDocuments(True)
    sonuc = []
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
            print(f"{i:2d}. {ad:24s} {'OK' if ok else 'HATA'}  govde={n}  {time.time() - t0:.1f}s", flush=True)
            sonuc.append((i, ad, ok))
            sw.CloseDoc(p.m.GetTitle())
        except Exception:
            print(f"{i:2d}. {ad:24s} HATA")
            traceback.print_exc()
            sonuc.append((i, ad, False))
    print("Basarili:", sum(1 for s in sonuc if s[2]), "/", len(sonuc))


if __name__ == "__main__":
    main()
