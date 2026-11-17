"""SW-TC 'V6 Engine' (3D CAD Project 10) playlist videolarindan okunan olculerle parcalar.
Hedef: Desktop\\V6 MOTOR YENI.  Kullanim: python v6_yeni_parcalar.py [sira no ...]
Koordinat kurali (montaj icin): krank ekseni dunya Z, Y yukari, sira acisi +-45 (90 derece V).
Silindir kapagi / kulbutor kapagi / egzoz: yerel x = genislik(disa), y = yukari, z = boy."""
import math
import os
import sys
import time
import traceback

from swlib import connect, Part, bbox
from parcalar_ciz import star, revolve_y, ngon
from v6_motor_ciz import hull_loop
from v6_duzeltme import half_ring, revolve_x, timing_pulley_small, timing_pulley_big, side_cover

HEDEF = os.path.join(os.path.expanduser("~"), "Desktop", "V6 MOTOR YENI")
ONIZ = os.path.join(HEDEF, "_onizlemeler")

# ---- videodan okunan ana olculer (mm) ----
BORE = 127.0            # silindir capi / piston O127
DECK = 279.40           # krank ekseninden sira ekseni boyunca blok ust yuzu
BANK_W = 165.10         # sira genisligi
BLOCK_L = 508.0         # blok / kapak boyu
PITCH = 146.05          # silindir araligi
THROW = 63.50           # krank kol yaricapi (pim kacikligi)
ROD = 152.40            # biyel merkezler arasi
JOURNAL_R = 38.10       # ana muylu O76.20
PIN_R = 31.75           # krank pimi O63.50
CRANK_STEP = 145.96     # krank ana muylu tekrar araligi
JOURNAL_L = 27.31
WEB_T = 20.0
PIN_L = CRANK_STEP - JOURNAL_L - 2 * WEB_T
Z0 = -21.4              # blok on yuzu (dunya z)
PIN_Z = [i * CRANK_STEP + JOURNAL_L + WEB_T + PIN_L / 2 for i in range(3)]
ROD_OFF = 12.7          # ayni pimdeki iki biyelin z kaymasi
CYL_Z = {45: [z - ROD_OFF for z in PIN_Z], -45: [z + ROD_OFF for z in PIN_Z]}
PIN_ANG = [0, 120, 240]
HEAD_H = 85.70
COVER_H = 63.50

C = {
    "blok": (0.32, 0.33, 0.35), "kapak": (0.82, 0.78, 0.70), "krank": (0.58, 0.58, 0.60),
    "piston": (0.80, 0.80, 0.82), "biyel": (0.55, 0.33, 0.20), "krom": (0.86, 0.86, 0.89),
    "mor": (0.40, 0.36, 0.72), "altin": (0.85, 0.64, 0.12), "siyah": (0.09, 0.09, 0.10),
    "egzoz": (0.30, 0.27, 0.25), "emme": (0.70, 0.68, 0.64), "karter": (0.38, 0.24, 0.14),
    "turbo": (0.72, 0.72, 0.75), "celik": (0.66, 0.66, 0.68), "bronz": (0.78, 0.55, 0.25),
}


def U(phi):
    a = math.radians(phi)
    return (math.sin(a), math.cos(a))


def P(phi, s, t):
    a = math.radians(phi)
    u = (math.sin(a), math.cos(a))
    sg = 1 if phi > 0 else -1
    o = (sg * math.cos(a), -sg * math.sin(a))
    return (s * u[0] + t * o[0], s * u[1] + t * o[1])


def zp(p, z):
    """Z=z duzlemi (On duzleme paralel); negatifler icin ters duzlem."""
    if z >= 0:
        return p.plane(f"Z{z:.2f}", "front", z).Name
    return p.plane(f"Z{z:.2f}", "front", -z, flip=True).Name


def ext_z(p, z0, L, merge=True):
    """Aktif olmayan: on duzlemde cizilip z0..z0+L arasina uzatilan eskiz icin yardimci."""
    raise NotImplementedError


def prism(p, pts=None, circles=(), z0=0.0, L=10.0, merge=True, rect=None):
    """On duzleme paralel eskiz -> z0'dan +Z yonunde L kadar ekstruzyon."""
    pl = zp(p, z0) if abs(z0) > 1e-6 else None
    p.sketch(pl if pl else "front")
    if pts:
        p.poly(pts)
    if rect:
        p.rect(*rect)
    for c in circles:
        p.circle(*c)
    p.end_sketch()
    # ters (flip) duzlemde de ekstruzyon dunya +Z'ye gider (testle dogrulandi)
    return p.extrude(L, merge=merge)


def cut_z(p, circles=(), z0=0.0, L=10.0, pts=None, rect=None):
    pl = zp(p, z0) if abs(z0) > 1e-6 else None
    p.sketch(pl if pl else "front")
    if pts:
        p.poly(pts)
    if rect:
        p.rect(*rect)
    for c in circles:
        p.circle(*c)
    p.end_sketch()
    p.cut(L)


# ================================================================ PARCALAR
def engine_block(p):
    L = BLOCK_L
    prism(p, rect=(-150, -25.4, 150, 120), z0=Z0, L=L, merge=False)
    for phi in (45, -45):
        prism(p, pts=[P(phi, 40, -BANK_W / 2), P(phi, DECK, -BANK_W / 2), P(phi, DECK, BANK_W / 2),
                      P(phi, 40, BANK_W / 2)], z0=Z0, L=L)
    # krank boslugu (R120; krank donus capini aciklar)
    cut_z(p, circles=[(0, 0, 118)], z0=Z0 + 12, L=L - 24)     # 118: 120 blok ust yuzune teget olup kesmeyi bozuyordu
    p.sketch("front"); p.circle(0, 0, JOURNAL_R + 2); p.end_sketch(); p.cut(both=True)
    # 6 silindir (O127), sira ekseni boyunca dondur-kes
    for phi, zs in CYL_Z.items():
        for z in zs:
            pl = zp(p, z)
            p.sketch(pl)
            p.centerline(*P(phi, 0, 0), *P(phi, 300, 0))
            rb = BORE / 2 + 0.3            # 0.3 mm yaricap payi: piston (O127) ile temas/cakisma olmasin
            p.poly([P(phi, 110, 0), P(phi, DECK + 5, 0), P(phi, DECK + 5, rb), P(phi, 110, rb)])
            p.end_sketch()
            p.revolve(cut=True)
    p.style_all(C["blok"], shine=0.4)


def cylinder_head(p):
    # yerel: x genislik +-82.55, y 0..85.7 (y=0 blok yuzu), z 0..508
    prism(p, rect=(-BANK_W / 2, 0, BANK_W / 2, HEAD_H), z0=0, L=BLOCK_L, merge=False)
    zc = [BLOCK_L / 2 - PITCH, BLOCK_L / 2, BLOCK_L / 2 + PITCH]
    # yanma odalari O127 x 10 (alt yuzden), supap delikleri O44.45, buji O14
    p.sketch("top")
    for z in zc:
        p.circle(0, -z, BORE / 2)
    p.end_sketch(); p.cut(10, reverse=True)
    p.sketch("top")
    for z in zc:
        p.circle(-28, -z, 11); p.circle(28, -z, 11); p.circle(0, -z + 40, 7)
    p.end_sketch(); p.cut(through=True)
    # yan portlar 38.10 x 31.75 (iki yanda)
    p.sketch("right")
    for z in zc:
        for dz in (-28, 28):
            p.rect(-(z + dz) - 15.9, 25, -(z + dz) + 15.9, 63.1)
    p.end_sketch(); p.cut(both=True)
    # civata delikleri O12 (dort kose + aralar)
    p.sketch("top")
    for z in (25, zc[0] + 73, zc[1] + 73, BLOCK_L - 25):
        p.circle(-70, -z, 6); p.circle(70, -z, 6)
    p.end_sketch(); p.cut(through=True)
    p.style_all(C["kapak"], shine=0.4)


def valves_cover(p):
    # 508 x 165.10, ofset duvar 10.16, yukseklik 63.5; buji yuvalari O40.64 @120.65 ve 146.05 aralik
    prism(p, rect=(-BANK_W / 2, 0, BANK_W / 2, COVER_H), z0=0, L=BLOCK_L, merge=False)
    t = 10.16
    cut_z(p, rect=(-BANK_W / 2 + t, -1, BANK_W / 2 - t, COVER_H - t), z0=t, L=BLOCK_L - 2 * t)
    # video #201: bir uzun kenardan 63.5 derin, O40.64 yarim daire oyuklar (tarak gorunumu)
    p.plane("Xtarak", "right", BANK_W / 2 - 31.75, flip=True)
    p.sketch("Xtarak")
    for k in range(3):
        z = 120.65 + k * PITCH
        for dz in (0, 40.64 + 20):
            p.circle(-(z + dz), 0, 20.32)
    p.end_sketch(); p.cut(63.5, mid=True)
    p.sketch("top")
    for z in (12, 107.41, 254, BLOCK_L - 86.37, BLOCK_L - 12):
        p.circle(-BANK_W / 2 + 5, -z, 3.2); p.circle(BANK_W / 2 - 5, -z, 3.2)
    p.end_sketch(); p.cut(through=True)
    p.style_all(C["mor"], shine=0.6)


def oil_pan(p):
    # yerel: x genislik 330.2 (+-165.1), y 0..-101.6, z 0..508 ; ust flans 25.4
    prism(p, rect=(-165.1, 0, 165.1, 25.4), z0=0, L=BLOCK_L, merge=False)
    prism(p, pts=[(-150, 0), (150, 0), (110, -101.6), (-110, -101.6)], z0=12, L=BLOCK_L - 24)
    cut_z(p, pts=[(-140, 26), (140, 26), (100, -91.4), (-100, -91.4)], z0=22, L=BLOCK_L - 44)
    p.style_all(C["karter"], shine=0.4)


def crank_shaft(p):
    first = True
    for i in range(4):
        z = i * CRANK_STEP
        prism(p, circles=[(0, 0, JOURNAL_R)], z0=z, L=JOURNAL_L, merge=not first)
        first = False
    prism(p, circles=[(0, 0, 25)], z0=-45, L=45)                       # on uc (kasnak mili)
    for i, ang in enumerate(PIN_ANG):
        a = math.radians(ang)
        c = (THROW * math.sin(a), THROW * math.cos(a))
        z = i * CRANK_STEP + JOURNAL_L
        for zz in (z, z + WEB_T + PIN_L):
            # video: O88.90 kol ucu pim merkezinde (63.50 kacik); karsi agirlik ters yonde
            for loop in ([((0, 0), 50.8), (c, 44.45)], [((0, 0), 50.8), ((-c[0] * 0.55, -c[1] * 0.55), 62)]):
                pl = zp(p, zz)
                p.sketch(pl)
                hull_loop(p, loop)
                p.end_sketch()
                p.extrude(WEB_T, merge=True)
        prism(p, circles=[(c[0], c[1], PIN_R)], z0=z + WEB_T, L=PIN_L)
    p.style_all(C["krank"], shine=0.7)


def piston_rod(p):
    # buyuk uc merkez (0,0), kucuk uc (0,152.4); kalinlik 24.13
    T = 24.13
    p.sketch("front")
    half_ring(p, 0, 0, 43.29, PIN_R, up=True)
    p.end_sketch(); p.extrude(T, mid=True)
    p.sketch("front"); p.rect(-55, 0, -38, 12.7); p.rect(38, 0, 55, 12.7); p.end_sketch()
    p.extrude(T, mid=True, merge=True)
    p.sketch("front"); p.circle(0, ROD, 19.05); p.circle(0, ROD, 12.7); p.end_sketch()
    p.extrude(T, mid=True, merge=True)
    p.sketch("front"); p.poly([(-19.05, 38), (19.05, 38), (10, ROD - 18), (-10, ROD - 18)]); p.end_sketch()
    p.extrude(15, mid=True, merge=True)
    p.sketch("top"); p.circle(-46.5, 0, 4); p.circle(46.5, 0, 4); p.end_sketch(); p.cut(both=True)
    p.style_all(C["biyel"], shine=0.6)


def piston_rod_cap(p):
    T = 24.13
    p.sketch("front")
    half_ring(p, 0, 0, 43.29, PIN_R, up=False)
    p.end_sketch(); p.extrude(T, mid=True)
    p.sketch("front"); p.rect(-55, -12.7, -38, 0); p.rect(38, -12.7, 55, 0); p.end_sketch()
    p.extrude(T, mid=True, merge=True)
    p.sketch("top"); p.circle(-46.5, 0, 4); p.circle(46.5, 0, 4); p.end_sketch(); p.cut(both=True)
    p.style_all(C["biyel"], shine=0.6)


def piston_head(p):
    # O127, yukseklik 81.28, 3 segman yuvasi (7.62 aralik, 2.82 derin), pim O25.4 tepeden 50.8
    R, H = BORE / 2, 81.28
    prof = [(0, 0), (R, 0)]
    y = 0
    for _ in range(3):
        prof += [(R, y - 6.35), (R - 2.82, y - 6.35), (R - 2.82, y - 9.53)]
        y -= 9.53
    prof += [(R, y), (R, -H), (0, -H)]
    revolve_y(p, prof)
    # ic oyuk O112: y=-15'ten asagi (tabanda acik). Dairesel eskiz + kesme (revolve cut guvenilmezdi)
    p.plane("Y-15", "top", 15, flip=True)
    p.sketch("Y-15"); p.circle(0, 0, 56); p.end_sketch()
    p.cut(H + 2 - 15, reverse=True)       # asagi dogru (tabana acik)
    for ad, flip in (("X18", False), ("X-18", True)):
        p.plane(ad, "right", 18, flip=flip)
        p.sketch(ad); p.rect(-22, -72, 22, -32); p.circle(0, -50.8, 12.7); p.end_sketch()
        p.extrude(38, reverse=flip, merge=True)
    p.sketch("right")
    p.sm.CreateLine(-38.1 / 1000, -90 / 1000, 0, 38.1 / 1000, -90 / 1000, 0)
    p.sm.CreateLine(38.1 / 1000, -90 / 1000, 0, 38.1 / 1000, -66 / 1000, 0)
    p.arc(0, -66, 38.1, -66, -38.1, -66, ccw=True)
    p.sm.CreateLine(-38.1 / 1000, -66 / 1000, 0, -38.1 / 1000, -90 / 1000, 0)
    p.end_sketch(); p.cut(both=True)
    p.style_all(C["piston"], shine=0.8)


def piston_pin(p):
    revolve_x(p, [(-34.9, 6.35), (-34.9, 12.7), (34.9, 12.7), (34.9, 6.35)])
    p.style_all(C["krom"], shine=0.9)


def cam_shaft(p):
    # Y ekseni boyunca 466 mm, mil O25.4, 12 kam (taban r17.3, burun +9), 4 yatak O38
    # mil O19.05: yatak burclari (ic O19.05) ve tutuculari (yuva O19.05) bu mile oturur
    p.sketch("top"); p.circle(0, 0, 9.525); p.end_sketch(); p.extrude(466)
    for k in range(3):
        for j, dy in enumerate((-28, 28)):
            y = 8 + 19.05 + 63.5 + k * 146.05 + dy
            th = math.radians(k * 120 + j * 90)
            pts = []
            for n in range(36):
                a = 2 * math.pi * n / 36
                r = 17.3 + 9 * max(0.0, math.cos(a - th)) ** 3
                pts.append((r * math.cos(a), r * math.sin(a)))
            pl = p.plane(f"Y{y:.1f}", "top", y).Name
            p.sketch(pl); p.poly(pts); p.end_sketch(); p.extrude(14, merge=True)
    p.style_all(C["krank"], shine=0.8)


def cam_retainer(p):
    # video #192: kutu, alt yuva R9.525, delikler +-19.05, havsa O23.785 x 5
    p.sketch("right")
    p.poly([(-28.6, 0), (28.6, 0), (28.6, 12.7), (14, 12.7), (14, 22.2), (-14, 22.2), (-14, 12.7), (-28.6, 12.7)])
    p.end_sketch(); p.extrude(19.05, mid=True)
    p.sketch("right"); p.circle(0, 0, 9.525); p.end_sketch(); p.cut(both=True)
    p.sketch("top"); p.circle(0, 19.05, 3.2); p.circle(0, -19.05, 3.2); p.end_sketch(); p.cut(both=True)
    yl = p.plane("Y12.7", "top", 12.7).Name
    p.sketch(yl); p.circle(0, 19.05, 5.5); p.circle(0, -19.05, 5.5); p.end_sketch(); p.cut(5, reverse=True)
    p.style_all(C["siyah"], shine=0.4)


def cam_bushing(p):
    revolve_x(p, [(0, 9.525), (0, 12.7), (19.05, 12.7), (19.05, 9.525)])
    p.style_all(C["bronz"], shine=0.8)


def crank_bushing(p):
    revolve_x(p, [(0, JOURNAL_R), (0, JOURNAL_R + 4), (19.05, JOURNAL_R + 4), (19.05, JOURNAL_R)])
    p.style_all(C["bronz"], shine=0.8)


def engine_valve(p):
    prof = [(0, 0), (26.7, 0), (26.7, 2.5), (8, 14), (4.76, 22), (4.76, 108), (3.8, 108), (3.8, 111),
            (4.76, 111), (4.76, 115), (0, 115)]
    revolve_y(p, prof)
    p.style_all(C["krom"], shine=0.9)


def rocker_arm(p):
    # video #147: O9.53 pim deligi, sol kol 22.23 (5 kalin uc), sag kol 28.58, 25 derece, 10 genislik
    p.sketch("right")
    p.arc(0, 0, 0, -11.9, 0, 11.9, ccw=True)
    pts = [(0, 11.9), (-28.58, 5), (-28.58, 0), (-6, -11.9)]
    for a, b in zip(pts, pts[1:]):
        p.sm.CreateLine(a[0] / 1000, a[1] / 1000, 0, b[0] / 1000, b[1] / 1000, 0)
    p.sm.CreateLine(-6 / 1000, -11.9 / 1000, 0, 0, -11.9 / 1000, 0)
    p.end_sketch(); p.extrude(10, mid=True)
    p.sketch("right")
    p.poly([(0, 11.9), (22.23, 5), (22.23, -2), (0, -11.9)])
    p.end_sketch(); p.extrude(10, mid=True, merge=True)
    p.sketch("right"); p.circle(0, 0, 4.765); p.circle(-24, 2.5, 1.59); p.end_sketch(); p.cut(both=True)
    # kol ucunda catal yuvasi (makara 6 mm girer): x +-3.2, z 17..30
    p.sketch("top"); p.rect(-3.2, -30, 3.2, -17); p.end_sketch(); p.cut(both=True)
    p.style_all(C["siyah"], shine=0.5)


def rocker_roll(p):
    revolve_x(p, [(-3, 1.59), (-3, 6.4), (-2.4, 7.14), (2.4, 7.14), (3, 6.4), (3, 1.59)])      # 6 mm: kol catalina girer
    p.style_all(C["krom"], shine=0.9)


def rocker_pin(p):
    revolve_x(p, [(-9.5, 0), (-9.5, 4.0), (-8.8, 4.765), (8.8, 4.765), (9.5, 4.0), (9.5, 0)])
    p.style_all(C["krom"], shine=0.9)


def rocker_spring(p):
    # video #187: helis O24.80, h 30.30, adim 5, tel O2.45, uclarda O26.70 x 1.5 disk
    for i in range(6):
        y = 1.5 + 1.225 + i * 5.0
        p.sketch("front"); p.centerline(0, -5, 0, 40); p.circle(12.4, y, 1.225); p.end_sketch()
        p.revolve(merge=True)
    for y0 in (0, 30.3 - 1.5):
        p.sketch("front"); p.centerline(0, -5, 0, 40)
        p.poly([(6, y0), (13.35, y0), (13.35, y0 + 1.5), (6, y0 + 1.5)]); p.end_sketch()
        p.revolve(merge=True)
    p.style_all((0.12, 0.12, 0.13), shine=0.7)


def intake_manifold(p):
    # dunya cerceveli (z 0..508 yerel = blok boyu); plenum 263.53 x 71.47, runner 63.5 x 38.1
    prism(p, rect=(-45, 300, 45, 371.5), z0=40, L=428, merge=False)
    for phi, zs in CYL_Z.items():
        sg = 1 if phi > 0 else -1
        for z in zs:
            zl = z - Z0 - 19.05
            a, b = (sg * 30, 305), (sg * 30, 343)
            c, d = P(phi, 360, -BANK_W / 2 - 10), P(phi, 322, -BANK_W / 2 - 10)
            prism(p, pts=[a, b, c, d], z0=zl, L=38.1)
    prism(p, circles=[(-22, 336, 18), (22, 336, 18)], z0=0, L=40)
    p.style_all(C["emme"], shine=0.6)


def exhaust(p, sg):
    # yerel x disa (sg ile aynalanir), y sira ekseni, z boy; flans 387.35 x 63.5 x 9.52
    X = lambda v: sg * v
    zc = [BLOCK_L / 2 - PITCH, BLOCK_L / 2, BLOCK_L / 2 + PITCH]
    prism(p, pts=[(X(0), -31.75), (X(9.52), -31.75), (X(9.52), 31.75), (X(0), 31.75)],
          z0=BLOCK_L / 2 - 193.7, L=387.35, merge=False)
    for z in zc:
        prism(p, pts=[(X(9), -19.05), (X(9), 19.05), (X(75), -40), (X(60), -66)], z0=z - 19.05, L=38.1)
    prism(p, circles=[(X(75), -60, 23.8)], z0=20, L=BLOCK_L - 20)
    cut_z(p, circles=[(X(75), -60, 19)], z0=19, L=BLOCK_L)
    p.sketch("right")
    for z in zc:
        p.rect(-z - 15.9, -15.9, -z + 15.9, 15.9)
    p.end_sketch(); p.cut(both=True)
    p.style_all(C["egzoz"], shine=0.6)


def air_filter(p):
    # video #190: 20 pileli loft, boy 101.5, et 1 mm, buyuk uca 10 mm kapak; on duzlemde Z boyunca
    p.sketch("front"); p.poly(star(20, 50, 41, phase=math.pi / 20)); p.end_sketch()
    p.style(p.extrude(101.5, draft=6), "Pileli Filtre", C["altin"], shine=0.9)
    p.sketch("front"); p.circle(0, 0, 50); p.end_sketch()
    p.style(p.extrude(10, reverse=True), "Kapak", C["krom"], shine=0.9)
    pl = zp(p, 101.5)
    p.sketch(pl); p.circle(0, 0, 33); p.circle(0, 0, 26.7); p.end_sketch()
    p.style(p.extrude(30), "Boyun", C["krom"], shine=0.9)


def air_turbo(p):
    # video #198: salyangoz govde (helis+loft yaklasimi), O38 mil, cikis 63.5 x 33.27
    for k, (r1, r2) in enumerate([(55, 40), (70, 45), (85, 50)]):
        pass
    p.sketch("front"); p.circle(0, 0, 70); p.end_sketch(); p.extrude(55)
    pl = zp(p, 55)
    p.sketch(pl); p.circle(0, 0, 25); p.end_sketch(); p.extrude(35, merge=True)
    pl = zp(p, 90)
    p.sketch(pl); p.circle(0, 0, 60); p.end_sketch(); p.extrude(45, merge=True)
    p.sketch("front"); p.rect(40, 10, 103.5, 43.27); p.end_sketch(); p.extrude(55, merge=True)
    pl = zp(p, 135)
    p.sketch(pl); p.circle(0, 0, 33); p.circle(0, 0, 26.7); p.end_sketch(); p.extrude(30, merge=True)
    p.sketch("front"); p.circle(0, 0, 19); p.end_sketch(); p.extrude(20, reverse=True, merge=True)
    p.style_all(C["turbo"], shine=0.7)


# dosya adlari ve klasor yapisi, #203 montaj videosundaki parca klasoruyle ayni
PIS = "Piston parcalari\\"
ROC = "rockerarm parcalari\\"
PARCALAR = [
    ("EngineBlock", engine_block),
    ("CylinderHead", cylinder_head),
    ("Valves Cover", valves_cover),
    ("OilPan", oil_pan),
    ("Crankshaft", crank_shaft),
    (PIS + "Piston Head", piston_head),
    (PIS + "Piston Rod", piston_rod),
    (PIS + "Piston Rod Cap", piston_rod_cap),
    (PIS + "Piston Pin", piston_pin),
    ("CamShaft", cam_shaft),
    ("CamShaft Retainer", cam_retainer),
    ("CamShaft Bushing", cam_bushing),
    ("CrankShaft Bushing", crank_bushing),
    ("valve", engine_valve),
    (ROC + "Rocker arm", rocker_arm),
    (ROC + "Rocker arm roll", rocker_roll),
    (ROC + "rocker arm pin1", rocker_pin),
    ("RockerArm spring", rocker_spring),
    ("IntakeManifold2", intake_manifold),
    ("vvexhaust1", lambda p: exhaust(p, 1)),
    ("exhaust manifold2", lambda p: exhaust(p, -1)),
    ("AirFilter", air_filter),
    ("AirTurbo", air_turbo),
    ("PartR11", timing_pulley_small),
    ("PartR3", timing_pulley_big),
    ("FrontCover", side_cover),
]


def main():
    sec = [int(a) for a in sys.argv[1:]] or list(range(1, len(PARCALAR) + 1))
    os.makedirs(ONIZ, exist_ok=True)
    sw = connect()
    sw.CloseAllDocuments(True)
    ok = 0
    for i in sec:
        ad, fn = PARCALAR[i - 1]
        t0 = time.time()
        try:
            p = Part(sw)
            p.iso()
            fn(p)
            p.hide_planes(); p.hide_sketches(); p.iso()
            b = p._bodies()
            yol = os.path.join(HEDEF, ad + ".SLDPRT")
            os.makedirs(os.path.dirname(yol), exist_ok=True)
            p.m.SaveAs3(yol, 0, 1)
            p.m.SaveBMP(os.path.join(ONIZ, f"{i:02d}.bmp"), 900, 700)
            print(f"{i:2d}. {ad:26s} govde={len(b)} kutu={bbox(b[0]) if len(b) == 1 else '-'} {time.time() - t0:.1f}s",
                  flush=True)
            ok += len(b) > 0
            sw.CloseAllDocuments(True)
        except Exception:
            print(f"{i:2d}. {ad:26s} HATA")
            traceback.print_exc()
            sw.CloseAllDocuments(True)
    print("Basarili:", ok, "/", len(sec))


if __name__ == "__main__":
    main()
