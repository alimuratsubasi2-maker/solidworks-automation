"""V6'da yanlis cizilen 10 parcayi ORIJINAL sekil + olcu + yerel eksenlerle yeniden cizer.
(olculer orijinal dosyalardan: orijinal_incele.py)
Kullanim: python v6_duzeltme.py [sira numaralari]"""
import math
import os
import sys
import time
import traceback

from swlib import connect, Part, bbox
from parcalar_ciz import HEDEF, ONIZ, COL, star, revolve_y

CELIK = (0.66, 0.66, 0.68)


def revolve_x(p, prof):
    """X ekseni etrafinda dondur (On duzlem). prof: (x, yaricap)."""
    p.sketch("front")
    xs = [x for x, _ in prof]
    p.centerline(min(xs) - 5, 0, max(xs) + 5, 0)
    p.poly(prof)
    p.end_sketch()
    return p.revolve(merge=True)


def half_ring(p, cx, cy, ro, ri, up=True):
    """(cx,cy) merkezli yarim halka konturu; up=True: +y tarafi."""
    s = 1 if up else -1
    p.arc(cx, cy, cx + ro, cy, cx - ro, cy, ccw=up)
    p.sm.CreateLine((cx - ro) / 1000, cy / 1000, 0, (cx - ri) / 1000, cy / 1000, 0)
    p.arc(cx, cy, cx - ri, cy, cx + ri, cy, ccw=not up)
    p.sm.CreateLine((cx + ri) / 1000, cy / 1000, 0, (cx + ro) / 1000, cy / 1000, 0)


# ---------------------------------------------------------------- parcalar
def connecting_rod(p):
    """'piston' = biyel kolu. Eksen Z: kucuk uc +Z (z=87), buyuk uc acik yarim halka z=-76.2."""
    # Sag duzlem eskizi: x = -Z, y = Y
    p.sketch("right"); p.circle(-87, 0, 27); p.circle(-87, 0, 12.7); p.end_sketch()
    p.extrude(26, mid=True)
    p.sketch("right"); p.rect(-62, -13, 20, 13); p.end_sketch()
    p.extrude(8, mid=True, merge=True)                         # govde (I kesit gobegi)
    p.sketch("right"); p.rect(-62, 9, 20, 13); p.rect(-62, -13, 20, -9); p.end_sketch()
    p.extrude(20, mid=True, merge=True)                        # I kesit flanslari
    # buyuk uc: merkez Z=-76.2 (eskiz x=76.2), +Z yonune acilan yarim halka
    p.sketch("right")
    cx = 76.2
    p.arc(cx, 0, cx, 60.3, cx, -60.3, ccw=True)
    p.sm.CreateLine(cx / 1000, -60.3 / 1000, 0, cx / 1000, -47 / 1000, 0)
    p.arc(cx, 0, cx, -47, cx, 47, ccw=False)
    p.sm.CreateLine(cx / 1000, 47 / 1000, 0, cx / 1000, 60.3 / 1000, 0)
    p.end_sketch()
    p.extrude(32.6, mid=True, merge=True)
    p.sketch("right"); p.rect(62, 44, 76.2, 60.3); p.rect(62, -60.3, 76.2, -44); p.end_sketch()
    p.extrude(32.6, mid=True, merge=True)                      # civata kulaklari
    p.sketch("front"); p.circle(0, 53, 4.5); p.circle(0, -53, 4.5); p.end_sketch()
    p.cut(both=True)                                           # kapak civata delikleri
    p.style_all(COL["biyel"], shine=0.6)


def rod_cap(p):
    """'piston Part1' = biyel kapagi: Y yukari yarim halka r50.8/41, Z'de kulaklar, X kalinlik 25.8."""
    p.sketch("right")
    half_ring(p, 0, 0, 50.8, 41, up=True)
    p.end_sketch()
    p.extrude(25.8, mid=True)
    p.sketch("right"); p.rect(-60.3, -0.7, -42, 11); p.rect(42, -0.7, 60.3, 11); p.end_sketch()
    p.extrude(25.8, mid=True, merge=True)
    p.sketch("top"); p.circle(0, 53, 4.5); p.circle(0, -53, 4.5); p.end_sketch()
    p.cut(both=True)
    p.style_all(COL["biyel"], shine=0.6)


def piston(p):
    """'piston Part3' = piston: Y ekseni, tepe y=0, etek y=-82.5, O127, pim ekseni X."""
    R = 63.5
    prof = [(0, 0), (R, 0)]
    y = 0
    for _ in range(4):
        prof += [(R, y - 4), (R - 2.5, y - 4), (R - 2.5, y - 7)]
        y -= 7
    prof += [(R, y), (R, -82.5), (0, -82.5)]
    revolve_y(p, prof)
    p.sketch("front"); p.centerline(0, -100, 0, 10); p.poly([(0, -83), (56, -83), (56, -16), (0, -16)]); p.end_sketch()
    p.revolve(cut=True)                                        # ici bos
    # etek pencereleri (+-X yanlari): |Z|<38, ustu yarim daire (tepesi y=-27, segmanlarin altinda)
    p.sketch("right")
    p.sm.CreateLine(-38 / 1000, -90 / 1000, 0, 38 / 1000, -90 / 1000, 0)
    p.sm.CreateLine(38 / 1000, -90 / 1000, 0, 38 / 1000, -65 / 1000, 0)
    p.arc(0, -65, 38, -65, -38, -65, ccw=True)
    p.sm.CreateLine(-38 / 1000, -65 / 1000, 0, -38 / 1000, -90 / 1000, 0)
    p.end_sketch()
    p.cut(both=True)
    # pim yuvalari (iki taraf), O25.4 pim deligi
    for ad, flip in (("X18", False), ("X-18", True)):
        p.plane(ad, "right", 18, flip=flip)
        p.sketch(ad); p.rect(-22, -74, 22, -34); p.circle(0, -52, 12.7); p.end_sketch()
        p.extrude(40, reverse=flip, merge=True)
    p.style_all(COL["piston"], shine=0.8)


def bushing_small(p):
    """'Part 1': O9.6 x 9 burc, X ekseni, pahli, O3.8 delik."""
    revolve_x(p, [(-4.5, 1.9), (-4.5, 4.3), (-4.0, 4.8), (4.0, 4.8), (4.5, 4.3), (4.5, 1.9)])
    p.style_all(CELIK, shine=0.7)


def cross_pin(p):
    """'Part 3': O9.6 x 19 pim, X ekseni, pahli, Y yonunde O6.8 delik."""
    revolve_x(p, [(-9.5, 0), (-9.5, 4.3), (-9.0, 4.8), (9.0, 4.8), (9.5, 4.3), (9.5, 0)])
    p.sketch("top"); p.circle(0, 0, 3.4); p.end_sketch(); p.cut(both=True)
    p.style_all(CELIK, shine=0.7)


def thin_pin(p):
    """'Part 4': O3.2 x 15.8 pim, X ekseni, pahli."""
    revolve_x(p, [(-7.9, 0), (-7.9, 1.2), (-7.5, 1.6), (7.5, 1.6), (7.9, 1.2), (7.9, 0)])
    p.style_all(CELIK, shine=0.7)


def timing_pulley_small(p):
    """'engine belt 1': O60.2 disli kasnak, Z ekseni z=-40..0.6, flansli, gobekli, O12 delik."""
    p.sketch("front"); p.circle(0, 0, 30.1); p.end_sketch()
    p.extrude(0.6, depth2=1.0)                                 # on flans z -1..0.6
    p.sketch("front"); p.poly(star(20, 27.2, 24.6, phase=math.pi / 20)); p.end_sketch()
    p.extrude(27, reverse=True, merge=True)                    # disler z -27..0
    p.plane("Z-27", "front", 27, flip=True)
    p.sketch("Z-27"); p.circle(0, 0, 30.1); p.end_sketch()
    p.extrude(1.6, reverse=True, merge=True)                   # arka flans
    p.sketch("Z-27"); p.circle(0, 0, 19); p.end_sketch()
    p.extrude(13, reverse=True, merge=True)                    # gobek z -40..-27
    p.sketch("front"); p.circle(0, 0, 6); p.end_sketch(); p.cut(both=True)
    p.style_all(CELIK, shine=0.8)


def timing_pulley_big(p):
    """'engine belt 3': O166 ince disli kasnak, Z ekseni z=-45..0.6, O100 delik, gobek."""
    p.sketch("front"); p.circle(0, 0, 83); p.circle(0, 0, 50); p.end_sketch()
    p.extrude(0.6, depth2=1.0)
    p.sketch("front"); p.poly(star(60, 83, 81)); p.circle(0, 0, 50); p.end_sketch()
    p.extrude(15, reverse=True, merge=True)
    p.plane("Z-15", "front", 15, flip=True)
    p.sketch("Z-15"); p.circle(0, 0, 62); p.circle(0, 0, 50); p.end_sketch()
    p.extrude(30, reverse=True, merge=True)
    p.style_all(CELIK, shine=0.8)


def side_cover(p):
    """'SIDE COVER': V seklinde (yarasa kanadi) yan plaka, XY'de, Z 0..52; alt yarim daire krank boslugu."""
    top = [(-239.4, 305.2), (-150, 250), (-30, 205), (30, 205), (150, 250), (239.4, 305.2)]
    out = top + [(165, -10.5)]
    p.sketch("front")
    for a, b in zip(out, out[1:]):
        p.sm.CreateLine(a[0] / 1000, a[1] / 1000, 0, b[0] / 1000, b[1] / 1000, 0)
    p.sm.CreateLine(165 / 1000, -10.5 / 1000, 0, 105 / 1000, -10.5 / 1000, 0)
    p.arc(0, -10.5, 105, -10.5, -105, -10.5, ccw=True)
    p.sm.CreateLine(-105 / 1000, -10.5 / 1000, 0, -165 / 1000, -10.5 / 1000, 0)
    p.sm.CreateLine(-165 / 1000, -10.5 / 1000, 0, -239.4 / 1000, 305.2 / 1000, 0)
    p.circle(-110, 150, 15); p.circle(110, 150, 15)
    p.end_sketch()
    p.extrude(10)                                              # ana plaka
    # ust kenar flansi: V kenari boyunca 6 kalin serit, 52 yukseklik (tek kapali kontur)
    p.sketch("front")
    p.poly(top + [(x, y - 6) for x, y in reversed(top)])
    p.end_sketch()
    p.extrude(52.1, merge=True)
    # delik cevresi gobekler
    p.sketch("front")
    for x in (-110, 110):
        p.circle(x, 150, 26); p.circle(x, 150, 15)
    p.end_sketch()
    p.extrude(20, merge=True)
    p.style_all((0.30, 0.30, 0.32), shine=0.5)


def cam_retainer(p):
    """'cam shaft retainer': yatak kapagi; Y 0..19, Z +-25.4, X +-9.5; altta R9.5 yuva, 2 civata deligi."""
    p.sketch("right")
    p.poly([(-25.4, 0), (25.4, 0), (25.4, 10.5), (11, 10.5), (11, 19), (-11, 19), (-11, 10.5), (-25.4, 10.5)])
    p.end_sketch()
    p.extrude(19, mid=True)
    p.sketch("right"); p.circle(0, 0, 9.5); p.end_sketch(); p.cut(both=True)
    p.sketch("top"); p.circle(0, 18.5, 2.5); p.circle(0, -18.5, 2.5); p.end_sketch(); p.cut(both=True)
    p.style_all((0.10, 0.10, 0.11), shine=0.4)


PARCALAR = [
    ("piston", connecting_rod),
    ("piston Part1", rod_cap),
    ("piston   Part3", piston),
    ("Part     1", bushing_small),
    ("Part    3", cross_pin),
    ("Part      4", thin_pin),
    ("engine belt 1", timing_pulley_small),
    ("engine belt 3", timing_pulley_big),
    ("SIDE COVER", side_cover),
    ("cam shaft retainer", cam_retainer),
]


def main():
    sec = [int(a) for a in sys.argv[1:]] or list(range(1, len(PARCALAR) + 1))
    os.makedirs(ONIZ, exist_ok=True)
    sw = connect()
    sw.CloseAllDocuments(True)
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
            p.m.SaveAs3(yol, 0, 1)
            p.m.SaveBMP(os.path.join(ONIZ, f"duz_{i:02d}.bmp"), 900, 700)
            kutu = bbox(b[0]) if len(b) == 1 else "-"
            print(f"{i:2d}. {ad:20s} govde={len(b)} kutu={kutu} {time.time() - t0:.1f}s", flush=True)
            sw.CloseAllDocuments(True)
        except Exception:
            print(f"{i:2d}. {ad:20s} HATA")
            traceback.print_exc()


if __name__ == "__main__":
    main()
