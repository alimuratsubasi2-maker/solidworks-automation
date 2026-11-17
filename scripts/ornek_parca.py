"""Gorseldeki SolidWorks alistirma parcasi (olculer gorselden).
Y yukari, silindir ekseni Y. Taban +X yonunde, sol blok -X yonunde."""
import os
from swlib import connect, Part, bbox

HEDEF = os.path.join(os.path.expanduser("~"), "Desktop", "solıd yapay zeka model tasarlama", "ornek parca")
RENK = (0.62, 0.52, 0.42)     # gorseldeki bronz/kahve ton


def main():
    os.makedirs(HEDEF, exist_ok=True)
    sw = connect()
    sw.CloseAllDocuments(True)
    p = Part(sw)
    p.iso()

    # 1) silindir: R30, yukseklik 60
    p.sketch("top"); p.circle(0, 0, 30); p.end_sketch()
    p.extrude(60)

    # 2) taban: kalinlik 15, ucu R23, delik merkezi 75
    p.sketch("top"); p.rect(0, -23, 75, 23); p.end_sketch()
    p.extrude(15, merge=True)
    p.sketch("top"); p.circle(75, 0, 23); p.end_sketch()
    p.extrude(15, merge=True)

    # 3) destek kanadi (kalinlik 10): silindir ustunden tabana, delikten 25 once biter
    p.sketch("front"); p.poly([(25, 15), (50, 15), (25, 60)]); p.end_sketch()
    p.extrude(10, mid=True, merge=True)

    # 4) baglanti kolu: 10 kalin, 15 genis, ust yuzey silindirle ayni (y 50..60)
    p.plane("Y50", "top", 50)
    p.sketch("Y50"); p.rect(-48, -7.5, -25, 7.5); p.end_sketch()
    p.extrude(10, merge=True)

    # 5) sol blok: x -45..-60 (15 kalin), y 15..60 (45 yuksek), genislik 35, O16 delik (ustten 15)
    p.plane("X-45", "right", 45, flip=True)
    p.sketch("X-45"); p.rect(-17.5, 15, 17.5, 60); p.circle(0, 45, 8); p.end_sketch()
    p.extrude(15, reverse=True, merge=True)      # ters duzlemde ekstruzyon +X'e gider; -X icin cevir
    print("blok sonrasi kutu:", bbox(p._bodies()[0]))

    # 6) delikler: silindir O40, taban O20
    p.sketch("top"); p.circle(0, 0, 20); p.circle(75, 0, 10); p.end_sketch()
    p.cut(through=True)

    p.style_all(RENK, shine=0.5)
    p.hide_planes(); p.hide_sketches(); p.iso()
    b = p._bodies()
    print("govde:", len(b), "sinir kutusu (mm):", bbox(b[0]))
    yol = os.path.join(HEDEF, "Alistirma_Parcasi.SLDPRT")
    p.m.SaveAs3(yol, 0, 1)
    p.m.SaveBMP(os.path.join(HEDEF, "onizleme.bmp"), 1400, 900)
    print("kaydedildi:", yol)


if __name__ == "__main__":
    main()
