"""SolidWorks'te sifirdan 60 derece V6 motor modeli (cok govdeli tek parca).
Koordinatlar (mm): krank mili Z ekseninde, blok z=0..300, Y yukari.
Sag sira phi=+30, sol sira phi=-30 (dikeyden aci)."""
import math
import os
import time
from swlib import connect, Part

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "V6_Motor.SLDPRT")

# ---------------- geometri ----------------
CRANK_R, ROD_L = 40.0, 135.0
BORE, PISTON = 41.0, 40.0
DECK, HEAD_TOP, COVER_TOP = 230.0, 272.0, 298.0
BANK_W = 58.0
CYL = {+30: [43, 138, 233], -30: [67, 162, 257]}   # sira -> silindir z'leri
PAIRS = [(55, 0), (150, 120), (245, 240)]           # (krank pimi z merkezi, pim acisi)

COL = {
    "blok": (0.86, 0.86, 0.84), "kapak": (0.70, 0.71, 0.73), "kulbutor": (0.62, 0.07, 0.05),
    "karter": (0.33, 0.33, 0.35), "krank": (0.55, 0.57, 0.60), "biyel": (0.40, 0.42, 0.46),
    "piston": (0.83, 0.83, 0.86), "manifold": (0.78, 0.78, 0.80), "altin": (0.86, 0.66, 0.12),
    "krom": (0.86, 0.86, 0.89), "kasnak": (0.24, 0.24, 0.26), "kayis": (0.06, 0.06, 0.06),
    "egzoz": (0.72, 0.68, 0.62),
}


def U(phi):
    a = math.radians(phi)
    return (math.sin(a), math.cos(a))


def P(phi, s, t):
    """Sira ekseni boyunca s, disa dogru t (mm) -> model x,y."""
    a = math.radians(phi)
    u = (math.sin(a), math.cos(a))
    sg = 1 if phi > 0 else -1
    o = (sg * math.cos(a), -sg * math.sin(a))
    return (s * u[0] + t * o[0], s * u[1] + t * o[1])


def pin_pos(theta):
    a = math.radians(theta)
    return (CRANK_R * math.sin(a), CRANK_R * math.cos(a))


def piston_s(phi, c):
    u = U(phi)
    a = math.radians(phi)
    w = (math.cos(a), -math.sin(a))
    cu = c[0] * u[0] + c[1] * u[1]
    cw = c[0] * w[0] + c[1] * w[1]
    return cu + math.sqrt(ROD_L ** 2 - cw ** 2)


def hull_loop(p, circles):
    """Daireleri (CCW sirali) disaridan saran kapali kayis konturu."""
    n = len(circles)
    outs, ins = [None] * n, [None] * n
    for i in range(n):
        (c1, r1), (c2, r2) = circles[i], circles[(i + 1) % n]
        dx, dy = c2[0] - c1[0], c2[1] - c1[1]
        L = math.hypot(dx, dy)
        e = (dx / L, dy / L)
        pr = (e[1], -e[0])
        k = (r1 - r2) / L
        q = math.sqrt(1 - k * k)
        m = (k * e[0] + q * pr[0], k * e[1] + q * pr[1])
        a = (c1[0] + r1 * m[0], c1[1] + r1 * m[1])
        b = (c2[0] + r2 * m[0], c2[1] + r2 * m[1])
        outs[i] = a
        ins[(i + 1) % n] = b
        p.sm.CreateLine(a[0] / 1000, a[1] / 1000, 0, b[0] / 1000, b[1] / 1000, 0)
    for j in range(n):
        c, _ = circles[j]
        p.arc(c[0], c[1], ins[j][0], ins[j][1], outs[j][0], outs[j][1], ccw=True)


def adim(p, msg):
    print("  >", msg, flush=True)
    p.m.ViewZoomtofit2()
    p.m.GraphicsRedraw2()
    time.sleep(0.2)


def main():
    sw = connect()
    sw.CloseAllDocuments(True)
    p = Part(sw)
    p.view()
    zp = lambda z: p.plane(f"Z{z}", "front", z)

    # 1) Motor blogu: karter govdesi + iki silindir sirasi
    p.sketch("front"); p.rect(-115, -70, 115, 50); p.end_sketch()
    blok = p.extrude(300)
    for phi in (30, -30):
        p.sketch("front")
        p.poly([P(phi, 30, -BANK_W), P(phi, DECK, -BANK_W), P(phi, DECK, BANK_W), P(phi, 30, BANK_W)])
        p.end_sketch()
        p.extrude(300, merge=True)
    p.style(blok, "Motor Blogu", COL["blok"], transp=0.55)
    adim(p, "Motor blogu")

    # 2) Silindir delikleri (6 adet, eksene gore dondurerek kesme)
    for phi, zs in CYL.items():
        for z in zs:
            zp(z)
            p.sketch(f"Z{z}")
            p.centerline(*P(phi, 0, 0), *P(phi, 260, 0))
            p.poly([P(phi, 70, 0), P(phi, DECK + 10, 0), P(phi, DECK + 10, BORE), P(phi, 70, BORE)])
            p.end_sketch()
            p.revolve(cut=True)
    adim(p, "6 silindir deligi")

    # 3) Krank boslugu
    zp(10)
    p.sketch("Z10"); p.circle(0, 0, 76); p.end_sketch()
    p.cut(280)
    adim(p, "Krank boslugu")

    # 4) Krank mili: ana mil + pimler + kollar
    p.sketch("front"); p.circle(0, 0, 24); p.end_sketch()
    p.style(p.extrude(315, depth2=45), "Krank Mili", COL["krank"], shine=0.7)
    for i, (zc, th) in enumerate(PAIRS, 1):
        c = pin_pos(th)
        zp(zc)
        p.sketch(f"Z{zc}"); p.circle(c[0], c[1], 19); p.end_sketch()
        p.style(p.extrude(44, mid=True), f"Krank Pimi {i}", COL["krank"], shine=0.7)
        a = math.radians(th)
        e = (math.sin(a), math.cos(a))
        q = (e[1], -e[0])
        loc = [(62, -23), (62, 23), (0, 30), (-30, 45), (-46, 20), (-46, -20), (-30, -45), (0, -30)]
        pts = [(x * e[0] + y * q[0], x * e[1] + y * q[1]) for x, y in loc]
        for dz in (-28, 28):
            zp(zc + dz)
            p.sketch(f"Z{zc + dz}"); p.poly(pts); p.end_sketch()
            p.style(p.extrude(12, mid=True), f"Krank Kolu {i}{'A' if dz < 0 else 'B'}", COL["krank"], shine=0.7)
    adim(p, "Krank mili")

    # 5) Biyeller + pistonlar
    n = 0
    for phi, zs in CYL.items():
        for k, z in enumerate(zs):
            n += 1
            c = pin_pos(PAIRS[k][1])
            s = piston_s(phi, c)
            pp = P(phi, s, 0)
            dx, dy = pp[0] - c[0], pp[1] - c[1]
            L = math.hypot(dx, dy)
            nx, ny = -dy / L, dx / L
            p.sketch(f"Z{z}")
            p.poly([(c[0] + 12 * nx, c[1] + 12 * ny), (pp[0] + 8 * nx, pp[1] + 8 * ny),
                    (pp[0] - 8 * nx, pp[1] - 8 * ny), (c[0] - 12 * nx, c[1] - 12 * ny)])
            p.end_sketch()
            p.style(p.extrude(16, mid=True), f"Biyel {n}", COL["biyel"], shine=0.5)

            s0, s1 = s - 30, s + 28
            prof = [(0, s0), (PISTON, s0), (PISTON, s1 - 18), (PISTON - 3, s1 - 18), (PISTON - 3, s1 - 15),
                    (PISTON, s1 - 15), (PISTON, s1 - 11), (PISTON - 3, s1 - 11), (PISTON - 3, s1 - 8),
                    (PISTON, s1 - 8), (PISTON, s1), (0, s1)]
            p.sketch(f"Z{z}")
            p.centerline(*P(phi, s0 - 20, 0), *P(phi, s1 + 20, 0))
            p.poly([P(phi, ss, tt) for tt, ss in prof])
            p.end_sketch()
            p.style(p.revolve(), f"Piston {n}", COL["piston"], shine=0.8)
    adim(p, "6 piston + 6 biyel")

    # 6) Silindir kapaklari + kulbutor kapaklari
    zp(150)
    for phi, ad in ((30, "Sag"), (-30, "Sol")):
        p.sketch("Z150")
        p.poly([P(phi, DECK, -60), P(phi, HEAD_TOP, -60), P(phi, HEAD_TOP, 60), P(phi, DECK, 60)])
        p.end_sketch()
        p.style(p.extrude(280, mid=True), f"Silindir Kapagi {ad}", COL["kapak"])

        # kapak profili ustteki 3 sogutma kanatcigiyla birlikte tek kontur
        top = [(COVER_TOP, 42)]
        for t in (27, 0, -27):
            top += [(COVER_TOP, t + 3), (COVER_TOP + 6, t + 3), (COVER_TOP + 6, t - 3), (COVER_TOP, t - 3)]
        top += [(COVER_TOP, -42)]
        prof = [(HEAD_TOP, -50), (HEAD_TOP, 50), (290, 50)] + top + [(290, -50)]
        p.sketch("Z150")
        p.poly([P(phi, s, t) for s, t in prof])
        p.end_sketch()
        p.style(p.extrude(260, mid=True), f"Kulbutor Kapagi {ad}", COL["kulbutor"], shine=0.8)
    adim(p, "Silindir kapaklari + kirmizi kulbutor kapaklari")

    # 7) Yag karteri
    p.sketch("Z150"); p.poly([(-108, -70), (108, -70), (96, -135), (-96, -135)]); p.end_sketch()
    p.style(p.extrude(270, mid=True), "Yag Karteri", COL["karter"])
    adim(p, "Yag karteri")

    # 8) Emme manifoldu (plenum + 6 runner)
    p.sketch("Z150"); p.poly([(-40, 195), (40, 195), (48, 240), (-48, 240)]); p.end_sketch()
    p.style(p.extrude(270, mid=True), "Emme Manifoldu", COL["manifold"], shine=0.6)
    for phi, zs in CYL.items():
        sg = 1 if phi > 0 else -1
        for z in zs:
            p.sketch(f"Z{z}")
            a, b = (40 * sg, 205), (46 * sg, 232)
            p.poly([a, P(phi, 238, -58), P(phi, 252, -58), b])
            p.end_sketch()
            p.style(p.extrude(30, mid=True), f"Emme Runner z{z}", COL["manifold"], shine=0.6)
    adim(p, "Emme manifoldu")

    # 9) Hava filtreleri (altin konik) + borular
    p.sketch("front"); p.circle(45, 215, 16); p.circle(-45, 215, 16); p.end_sketch()
    p.style(p.extrude(20, depth2=45), "Gaz Kelebegi Borulari", COL["krom"], shine=0.9)
    p.plane("Y215", "top", 215)
    for sg, ad in ((1, "Sag"), (-1, "Sol")):
        X = lambda r: (45 + r) * sg
        p.sketch("Y215")
        p.centerline(X(0), 30, X(0), 150)
        prof = [(0, -45), (30, -45)]
        for i in range(1, 17):
            r = 30 + 12 * i / 16 - (4 if i % 2 else 0)
            prof.append((r, -45 - 5 * i))
        prof.append((0, -125))
        p.poly([(X(r), -z) for r, z in prof])
        p.end_sketch()
        p.style(p.revolve(), f"Hava Filtresi {ad}", COL["altin"], shine=0.9)
        p.sketch("Y215")
        p.centerline(X(0), 30, X(0), 150)
        p.poly([(X(0), 125), (X(44), 125), (X(44), 133), (X(0), 133)])
        p.end_sketch()
        p.style(p.revolve(), f"Filtre Kapagi {ad}", COL["krom"], shine=0.9)
    adim(p, "Altin hava filtreleri")

    # 10) Kasnaklar + triger kayisi (on yuz)
    cams = [P(30, 250, 0), P(-30, 250, 0)]
    p.sketch("front"); p.circle(0, 0, 55); p.end_sketch()
    p.style(p.extrude(28, reverse=True), "Krank Kasnagi", COL["kasnak"])
    p.sketch("front"); p.circle(0, 0, 16); p.end_sketch()
    p.style(p.extrude(42, reverse=True), "Kasnak Gobegi", COL["krom"], shine=0.9)
    for c, ad in zip(cams, ("Sag", "Sol")):
        p.sketch("front"); p.circle(c[0], c[1], 38); p.end_sketch()
        p.style(p.extrude(28, reverse=True), f"Eksantrik Kasnagi {ad}", COL["kasnak"])
    p.sketch("front")
    hull_loop(p, [((0, 0), 61), (cams[0], 44), (cams[1], 44)])
    hull_loop(p, [((0, 0), 55.5), (cams[0], 38.5), (cams[1], 38.5)])
    p.end_sketch()
    p.style(p.extrude(22, reverse=True), "Triger Kayisi", COL["kayis"], shine=0.1)
    adim(p, "Kasnaklar + kayis")

    # 11) Egzoz manifoldlari
    for phi, zs in CYL.items():
        ad = "Sag" if phi > 0 else "Sol"
        tc = P(phi, 250, 95)
        p.sketch("Z10"); p.circle(tc[0], tc[1], 17); p.end_sketch()
        p.style(p.extrude(330), f"Egzoz Borusu {ad}", COL["egzoz"], shine=0.8)
        for z in zs:
            p.sketch(f"Z{z}")
            p.poly([P(phi, 238, 55), P(phi, 262, 55), P(phi, 262, 85), P(phi, 238, 85)])
            p.end_sketch()
            p.style(p.extrude(26, mid=True), f"Egzoz Kolu z{z}", COL["egzoz"], shine=0.8)
    adim(p, "Egzoz manifoldlari")

    # 12) Volan
    zp(302)
    p.sketch("Z302"); p.circle(0, 0, 112); p.end_sketch()
    p.style(p.extrude(16), "Volan", COL["kasnak"], shine=0.6)
    adim(p, "Volan")

    p.hide_planes()
    p.hide_sketches()
    p.view()
    bodies = p._bodies()
    print("Toplam govde:", len(bodies))
    p.m.SaveAs3(OUT, 0, 1)
    p.m.SaveBMP(OUT.replace(".SLDPRT", "_onizleme.bmp"), 1600, 1000)
    print("Kaydedildi:", OUT)


if __name__ == "__main__":
    main()
