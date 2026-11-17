import math
from swlib import connect, Part, MM

sw = connect()
sw.CloseAllDocuments(True)


def kutu():
    p = Part(sw)
    p.sketch("top"); p.rect(-50, -50, 50, 50); p.end_sketch(); p.extrude(60)      # y 0..60
    return p


def sonuc(ad, p):
    print(ad, "yuz:", p._bodies()[0].GetFaceCount(), flush=True)


# 1) profil eksene degen (mevcut yontem)
p = kutu()
p.sketch("front"); p.centerline(0, -10, 0, 80); p.poly([(0, 10), (10, 10), (10, 50), (0, 50)]); p.end_sketch()
p.revolve(cut=True); sonuc("A eksene degen profil", p); sw.CloseAllDocuments(True)

# 2) FeatureRevolve2 dogrudan, farkli bayraklar
for tek in (True, False):
    for merge in (True, False):
        p = kutu()
        p.sketch("front"); p.centerline(0, -10, 0, 80); p.poly([(0, 10), (10, 10), (10, 50), (0, 50)]); p.end_sketch()
        f = p.fm.FeatureRevolve2(tek, True, False, True, False, False, 0, 0, 2 * math.pi, 0, False, False, 0, 0, 0, 0, 0,
                                 merge, True, True)
        print(f"B tek={tek} merge={merge} feature={f is not None}", end=" ")
        sonuc("", p); sw.CloseAllDocuments(True)

# 3) merkez cizgisi secili degil, profil eksenden uzakta (halka)
p = kutu()
p.sketch("front"); p.centerline(0, -10, 0, 80); p.poly([(5, 10), (10, 10), (10, 50), (5, 50)]); p.end_sketch()
p.revolve(cut=True); sonuc("C eksenden uzak profil", p); sw.CloseAllDocuments(True)
