"""27 parcadan montaj dosyalari (.SLDASM). Dosya adlari referans zip ile ayni.
Kullanim: python montaj_ciz.py [piston] [rocker] [asm1] [complete]"""
import math
import os
import sys

from swlib import connect, T
from asmlib import Asm
from parcalar_ciz import HEDEF
from v6_motor_ciz import P, pin_pos, CYL, PAIRS

ROD = 140.0                         # biyel parcasinin merkezler arasi boyu
HEAD_Z = {30: 0, -30: 24}           # silindir kapaklarinin z kaymasi
CHAMBER = (47, 140, 233)            # kapak icindeki yanma odasi z'leri (yerel)


def U(phi):
    a = math.radians(phi)
    return (math.sin(a), math.cos(a), 0.0)


def bank(phi):
    u = U(phi)
    return dict(x=(u[1], -u[0], 0), y=u)


def axial(phi):
    return dict(x=(0, 0, 1), y=U(phi))


def at(xy, z):
    return (xy[0], xy[1], z)


def piston_s(phi, c):
    u = U(phi)
    w = (u[1], -u[0])
    cu = c[0] * u[0] + c[1] * u[1]
    cw = c[0] * w[0] + c[1] * w[1]
    return cu + math.sqrt(ROD ** 2 - cw ** 2)


def F(n):
    return n + ".SLDPRT"


# ---------------------------------------------------------------- alt montajlar
def piston_assembly(sw):
    a = Asm(sw, HEDEF)
    a.add(F("piston"))
    a.add(F("piston Part2"), origin=(0, 24, 0), x=(0, 1, 0), y=(0, 0, 1))
    a.add(F("piston Part1"), origin=(0, 24 - ROD, 0), x=(0, 0, -1), y=(0, 1, 0))
    a.add(F("piston   Part3"), origin=(0, 38, 0))
    return a.save("piston assembly.SLDASM")


def rocker_assembly(sw):
    a = Asm(sw, HEDEF)
    a.add(F("engine valve"))
    a.add(F("rocker arm spring"), origin=(0, 34, 0))
    a.add(F("rocker arm"), origin=(0, 72, 0), x=(0, 0, 1), y=(0, 1, 0))
    return a.save("rocker arm assembly.SLDASM")


# ---------------------------------------------------------------- donen grup
def rotating_group(a):
    a.add(F("crank shaft"))
    a.add(F("crank bushings"), origin=(0, 0, 0))
    a.add(F("crank bushings"), origin=(0, 0, 278))
    for phi, zs in CYL.items():
        u = U(phi)
        for k, z in enumerate(zs):
            c = pin_pos(PAIRS[k][1])
            s = piston_s(phi, c)
            pp = P(phi, s, 0)
            a.add(F("piston"), origin=at(P(phi, s - 24, 0), z), **axial(phi))
            a.add(F("piston Part2"), origin=at(pp, z))
            a.add(F("piston   Part3"), origin=at(P(phi, s - 24 + 38, 0), z), **axial(phi))
            d = (pp[0] - c[0], pp[1] - c[1], 0)
            n = math.hypot(d[0], d[1])
            d = (d[0] / n, d[1] / n, 0)
            a.add(F("piston Part1"), origin=at(c, z), x=(d[1], -d[0], 0), y=d)


def assembly1(sw):
    a = Asm(sw, HEDEF)
    rotating_group(a)
    return a.save("Assembly    1.SLDASM")


# ---------------------------------------------------------------- tam motor
def engine_complete(sw):
    a = Asm(sw, HEDEF)
    a.add(F("engine block"))
    rotating_group(a)
    for phi in (30, -30):
        hz = HEAD_Z[phi]
        sg = 1 if phi > 0 else -1
        a.add(F("cylinder head"), origin=at(P(phi, 230, 0), hz), **bank(phi))
        a.add(F("valves cover"), origin=at(P(phi, 272, 0), hz + 5), **bank(phi))
        cam = P(phi, 260, 0)
        a.add(F("cam shaft"), origin=at(cam, hz))
        a.add(F("cam bushings"), origin=at(cam, hz - 20))
        a.add(F("cam shaft retainer"), origin=at(cam, hz - 26))
        for zc in CHAMBER:
            for t in (-16, 16):
                a.add("rocker arm assembly.SLDASM", origin=at(P(phi, 215, t), hz + zc), **bank(phi))
            a.add(F("Part      4"), origin=at(P(phi, 262, 50), hz + zc + 28), x=(0, -sg, 0), y=(sg, 0, 0))
        for zb in (12, 93, 187, 268):
            for t in (-52, 52):
                a.add(F("Part     1"), origin=at(P(phi, 272, t), hz + zb), **bank(phi))
        ex = P(phi, 250, 95)
        a.add(F("exhuast manifold" if phi > 0 else "exhaust manifold left"),
              origin=at(ex, 10 if phi > 0 else 34), **bank(phi))

    a.add(F("OIL PAN"), origin=(0, -70, 150))
    a.add(F("INTAKE MANIFOLD"), origin=(0, 195, 15))
    for sg in (1, -1):
        dz = (sg * math.sin(math.radians(45)), 0, -math.cos(math.radians(45)))
        o = (sg * 22 + 55 * dz[0], 215, -25 + 55 * dz[2])
        y = (0, 1, 0)
        x = (y[1] * dz[2] - y[2] * dz[1], y[2] * dz[0] - y[0] * dz[2], y[0] * dz[1] - y[1] * dz[0])
        a.add(F("engine air filter"), origin=o, x=x, y=y)
    a.add(F("Part    3"), origin=(0, 0, -46))
    a.add(F("engine belt 1"), origin=(0, 0, -44))
    a.add(F("engine belt 3"), origin=(0, 0, -20))
    a.add(F("SIDE COVER"), origin=(0, 0, 338), x=(-1, 0, 0), y=(0, 1, 0))
    rex = P(30, 250, 95)
    a.add(F("air turbo"), origin=(rex[0], rex[1] + 97, 350 + 85), x=(1, 0, 0), y=(0, 0, 1))
    return a.save("engine complete.SLDASM")


ISLER = {"piston": piston_assembly, "rocker": rocker_assembly, "asm1": assembly1, "complete": engine_complete}


def main():
    sec = sys.argv[1:] or list(ISLER)
    sw = connect()
    sw.CloseAllDocuments(True)
    for k in sec:
        yol = ISLER[k](sw)
        m = T(sw.ActiveDoc, "IModelDoc2")
        n = len(T(m, "IAssemblyDoc").GetComponents(True) or [])
        if k in ("complete", "asm1"):
            # motorun on yuzu -Z'de: onden-ustten bakis
            m.ShowNamedView2("*Back", 2)
            v = T(m.ActiveView, "IModelView")
            v.RotateAboutCenter(0, -0.6)
            v.RotateAboutCenter(0.45, 0)
            m.ViewZoomtofit2()
            m.Save3(1, 0, 0)
        m.SaveBMP(os.path.join(HEDEF, "_onizlemeler", f"montaj_{k}.bmp"), 1400, 900)
        print(f"{k:9s} OK  bilesen={n}  -> {os.path.basename(yol)}", flush=True)
        sw.CloseAllDocuments(True)


if __name__ == "__main__":
    main()
