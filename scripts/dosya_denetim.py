"""V6 MOTOR YENI altindaki tum SolidWorks dosyalarini acip hata/uyari/eksik referans kontrolu yapar."""
import glob
import os
from swlib import connect, T, MM
from v6_yeni_parcalar import HEDEF

sw = connect()
sw.CloseAllDocuments(True)
sorun = []
tur = {".SLDPRT": 1, ".SLDASM": 2, ".SLDDRW": 3}
dosyalar = sorted(glob.glob(os.path.join(HEDEF, "**", "*.SLD*"), recursive=True))
for f in dosyalar:
    ext = os.path.splitext(f)[1].upper()
    if ext not in tur or os.path.basename(f).startswith("~"):
        continue
    ad = os.path.relpath(f, HEDEF)
    boyut = os.path.getsize(f)
    try:
        r = sw.OpenDoc6(f, tur[ext], 1, "", 0, 0)
    except Exception as e:
        sorun.append((ad, f"acilamadi: {e}"))
        continue
    model, hata, uyari = (r + (0, 0))[:3] if isinstance(r, tuple) else (r, 0, 0)
    m = T(model, "IModelDoc2")
    notlar = []
    if m is None:
        sorun.append((ad, f"acilamadi (hata kodu {hata})"))
        continue
    if hata:
        notlar.append(f"hata={hata}")
    if uyari:
        notlar.append(f"uyari={uyari}")
    if boyut < 20000:
        notlar.append(f"cok kucuk dosya ({boyut} B)")
    if ext == ".SLDPRT":
        b = T(m, "IPartDoc").GetBodies2(0, False)
        if not b:
            notlar.append("govde yok")
        elif len(b) > 1 and "Spring" not in ad and "Air" not in ad:
            notlar.append(f"{len(b)} govde")
    if ext == ".SLDASM":
        comps = T(m, "IAssemblyDoc").GetComponents(True) or []
        cozulmemis = [T(c, "IComponent2").Name2 for c in comps if T(c, "IComponent2").IsSuppressed()
                      or T(c, "IComponent2").GetModelDoc2() is None]
        notlar.append(f"{len(comps)} bilesen")
        if cozulmemis:
            notlar.append(f"EKSIK/BASTIRILMIS: {cozulmemis[:5]}")
            sorun.append((ad, f"eksik bilesen: {cozulmemis[:5]}"))
    if ext == ".SLDDRW":
        d = T(m, "IDrawingDoc")
        n = 0
        v = T(d.GetFirstView(), "IView")
        v = T(v.GetNextView(), "IView") if v else None
        while v is not None:
            n += 1
            v = T(v.GetNextView(), "IView")
        notlar.append(f"{n} gorunus")
        if n < 3:
            sorun.append((ad, f"az gorunus ({n})"))
    print(f"{ad:62s} {' | '.join(notlar) or 'tamam'}", flush=True)
    if hata or uyari:
        sorun.append((ad, " | ".join(notlar)))
    sw.CloseAllDocuments(True)

print("\nSORUN:", len(sorun))
for a, s in sorun:
    print(" -", a, s)
