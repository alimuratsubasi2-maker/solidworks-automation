from swlib import connect, Part

sw = connect()
sw.CloseAllDocuments(True)


def deneme(ad, fn):
    p = Part(sw)
    p.sketch("top"); p.rect(-20, -20, 20, 20); p.end_sketch(); p.extrude(10)
    p.sketch("top"); p.circle(0, 0, 5); p.end_sketch()
    fn(p)
    b = p._bodies()[0]
    print(f"{ad:28s} yuz sayisi={b.GetFaceCount()}  (6=kesilmedi, 7=delik var)")
    sw.CloseAllDocuments(True)


deneme("through (tek yon)", lambda p: p.cut(through=True))
deneme("both (iki yon)", lambda p: p.cut(both=True))
deneme("blind 5", lambda p: p.cut(5))
deneme("blind 5 reverse", lambda p: p.cut(5, reverse=True))
