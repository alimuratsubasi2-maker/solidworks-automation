"""V6 MOTOR YENI montajlari (#203 videosundaki yapi): Piston, rockerarm assembly, Engine Assembly.
Kullanim: python v6_yeni_montaj.py [piston] [rocker] [complete]"""
import math
import os
import sys

from swlib import connect, T
from asmlib import Asm
from v6_yeni_parcalar import (HEDEF, ONIZ, P, U, Z0, CYL_Z, PIN_ANG, THROW, ROD, DECK, HEAD_H,
                              BLOCK_L, PITCH, CRANK_STEP, PIS, ROC)

F = lambda n: n + ".SLDPRT"
PIN_DROP = 50.8     # piston tepesinden pim eksenine
PISTON_ASM = "Piston Assembly.SLDASM"          # ana klasorde (kullanici gorsun diye)
ROCKER_ASM = "Rocker Arm Assembly.SLDASM"


def piston_assembly(sw):
    a = Asm(sw, HEDEF)
    a.add(F(PIS + "Piston Head"))
    a.add(F(PIS + "Piston Pin"), origin=(0, -PIN_DROP, 0))
    o = (0, -PIN_DROP - ROD, 0)
    a.add(F(PIS + "Piston Rod"), origin=o, x=(0, 0, -1), y=(0, 1, 0))
    a.add(F(PIS + "Piston Rod Cap"), origin=o, x=(0, 0, -1), y=(0, 1, 0))
    return a.save(PISTON_ASM)


def rocker_assembly(sw):
    # video #199: kol + pim + makara (supap ve yay motor montajinda ayri)
    a = Asm(sw, HEDEF)
    a.add(F(ROC + "Rocker arm"))
    a.add(F(ROC + "rocker arm pin1"))
    a.add(F(ROC + "Rocker arm roll"), origin=(0, 2.5, 24))
    return a.save(ROCKER_ASM)


def bank_frame(phi):
    u = U(phi)
    sg = 1 if phi > 0 else -1
    a = math.radians(phi)
    o = (sg * math.cos(a), -sg * math.sin(a), 0)
    x = o if phi > 0 else (-o[0], -o[1], 0)
    return x, (u[0], u[1], 0), o


def local_to_world(origin, x, y, pt):
    z = (x[1] * y[2] - x[2] * y[1], x[2] * y[0] - x[0] * y[2], x[0] * y[1] - x[1] * y[0])
    return tuple(origin[i] + pt[0] * x[i] + pt[1] * y[i] + pt[2] * z[i] for i in range(3))


def engine_complete(sw):
    a = Asm(sw, HEDEF)
    a.add(F("EngineBlock"))
    a.add(F("Crankshaft"))
    for i in range(4):
        a.add(F("CrankShaft Bushing"), origin=(0, 0, i * CRANK_STEP + 4), x=(0, 0, 1), y=(0, 1, 0))
    # 6 piston (alt montaj); biyel krank pimine dogru egik
    for phi, zs in CYL_Z.items():
        u = U(phi)
        for k, z in enumerate(zs):
            ang = math.radians(PIN_ANG[k])
            c = (THROW * math.sin(ang), THROW * math.cos(ang))
            w = (u[1], -u[0])
            cu, cw = c[0] * u[0] + c[1] * u[1], c[0] * w[0] + c[1] * w[1]
            s = cu + math.sqrt(ROD ** 2 - cw ** 2)
            pp = P(phi, s, 0)
            fr = dict(x=(0, 0, 1), y=(u[0], u[1], 0))
            top = P(phi, s + PIN_DROP, 0)
            a.add(F(PIS + "Piston Head"), origin=(top[0], top[1], z), **fr)
            a.add(F(PIS + "Piston Pin"), origin=(pp[0], pp[1], z), **fr)
            d = (pp[0] - c[0], pp[1] - c[1])
            n = math.hypot(*d)
            d = (d[0] / n, d[1] / n)
            rf = dict(x=(d[1], -d[0], 0), y=(d[0], d[1], 0))
            a.add(F(PIS + "Piston Rod"), origin=(c[0], c[1], z), **rf)
            a.add(F(PIS + "Piston Rod Cap"), origin=(c[0], c[1], z), **rf)
    zc_local = [BLOCK_L / 2 - PITCH, BLOCK_L / 2, BLOCK_L / 2 + PITCH]
    for phi in (45, -45):
        x, y, o = bank_frame(phi)
        dz = -12.7 if phi > 0 else 12.7
        hp = P(phi, DECK, 0)
        head_o = (hp[0], hp[1], Z0 + dz)
        a.add(F("CylinderHead"), origin=head_o, x=x, y=y)
        cp = P(phi, DECK + HEAD_H, 0)
        a.add(F("Valves Cover"), origin=(cp[0], cp[1], Z0 + dz), x=x, y=y)
        for zl in zc_local:
            for vx in (-28, 28):
                a.add(F("valve"), origin=local_to_world(head_o, x, y, (vx, 0, zl)), x=x, y=y)
                a.add(F("RockerArm spring"), origin=local_to_world(head_o, x, y, (vx, HEAD_H, zl)), x=x, y=y)
                a.add(ROCKER_ASM, origin=local_to_world(head_o, x, y, (vx, 117, zl + 22.23)), x=x, y=y)
        a.add(F("CamShaft"), origin=local_to_world(head_o, x, y, (0, HEAD_H + 28, 21)), x=x, y=(0, 0, 1))
        for kb in range(4):
            zr = 21 + 8 + kb * 146.05 + 9.5
            a.add(F("CamShaft Retainer"), origin=local_to_world(head_o, x, y, (0, HEAD_H + 28, zr)),
                  x=(0, 0, 1), y=y)
        a.add(F("CamShaft Bushing"), origin=local_to_world(head_o, x, y, (0, HEAD_H + 28, 2)), x=(0, 0, 1), y=y)
        wp = local_to_world(head_o, x, y, (0, HEAD_H + 28, 0))
        a.add(F("PartR11"), origin=(wp[0], wp[1], Z0 - 14))
        ex_o = local_to_world(head_o, x, y, ((82.55 if phi > 0 else -82.55), 44, 0))
        a.add(F("vvexhaust1" if phi > 0 else "exhaust manifold2"), origin=ex_o, x=x, y=y)
        tube_end = local_to_world(ex_o, x, y, ((75 if phi > 0 else -75), -60, BLOCK_L))
        a.add(F("AirTurbo"), origin=tube_end)
        a.add(F("AirFilter"), origin=(tube_end[0], tube_end[1], tube_end[2] + 165 + 131.5),
              x=(-1, 0, 0), y=(0, 1, 0))
    a.add(F("IntakeManifold2"), origin=(0, 0, Z0))
    a.add(F("OilPan"), origin=(0, -50.8, Z0))
    a.add(F("PartR3"), origin=(0, 0, Z0 - 14))
    a.add(F("FrontCover"), origin=(0, 0, Z0 + BLOCK_L + 13))
    return a.save("Engine Assembly.SLDASM")


ISLER = {"piston": piston_assembly, "rocker": rocker_assembly, "complete": engine_complete}


def main():
    sec = sys.argv[1:] or list(ISLER)
    sw = connect()
    sw.CloseAllDocuments(True)
    for k in sec:
        yol = ISLER[k](sw)
        m = T(sw.ActiveDoc, "IModelDoc2")
        n = len(T(m, "IAssemblyDoc").GetComponents(True) or [])
        m.ShowNamedView2("*İzometrik", -1)
        m.ViewZoomtofit2()
        m.SaveBMP(os.path.join(ONIZ, f"montaj_{k}.bmp"), 1400, 900)
        m.Save3(1, 0, 0)
        print(f"{k:9s} OK  bilesen={n}  -> {os.path.relpath(yol, HEDEF)}", flush=True)
        sw.CloseAllDocuments(True)


if __name__ == "__main__":
    main()

