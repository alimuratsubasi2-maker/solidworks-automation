"""26 parcanin her kesme / dondurme-kesme / birlestirmeli uzatma komutunun GERCEKTEN etki edip etmedigini olcer.
Etkisiz komut = sessiz hata (parca eksik oyuk/delik/govde ile cikar)."""
import traceback
import swlib
from swlib import connect, Part
import v6_yeni_parcalar as V

P = swlib.Part
o_cut, o_rev, o_ext = P.cut, P.revolve, P.extrude
bulgu = []
mevcut = {"ad": ""}


def yuz(p):
    return sum(b.GetFaceCount() for b in p._bodies())


def hacim(p):
    try:
        t = p.m.Extension.CreateMassProperty()
        return t.Volume
    except Exception:
        return None


def satir():
    fr = [f for f in traceback.extract_stack() if "v6_yeni_parcalar" in f.filename or "parcalar_ciz" in f.filename
          or "v6_duzeltme" in f.filename]
    return fr[-1].lineno if fr else "?"


def kayit(tur, p, n0, n1, v0, v1):
    degisti = (n1 != n0) or (v0 is not None and v1 is not None and abs(v1 - v0) > 1e-12)
    if not degisti:
        bulgu.append((mevcut["ad"], tur, satir()))
        print(f"   ! ETKISIZ {tur} (satir {satir()})", flush=True)


def cut(self, *a, **k):
    n0, v0 = yuz(self), hacim(self)
    o_cut(self, *a, **k)
    kayit("cut", self, n0, yuz(self), v0, hacim(self))


def revolve(self, *a, **k):
    n0, v0 = yuz(self), hacim(self)
    r = o_rev(self, *a, **k)
    if k.get("cut") or (a and False):
        kayit("revolve-cut", self, n0, yuz(self), v0, hacim(self))
    return r


def extrude(self, *a, **k):
    n0, v0 = yuz(self), hacim(self)
    r = o_ext(self, *a, **k)
    if k.get("merge"):
        n1, v1 = yuz(self), hacim(self)
        if v0 is not None and v1 is not None and abs(v1 - v0) < 1e-12 and n0 == n1:
            kayit("extrude(merge)", self, n0, n1, v0, v1)
    return r


P.cut, P.revolve, P.extrude = cut, revolve, extrude
sw = connect()
sw.CloseAllDocuments(True)
for i, (ad, fn) in enumerate(V.PARCALAR, 1):
    mevcut["ad"] = ad
    print(f"{i:2d}. {ad}", flush=True)
    try:
        p = Part(sw)
        p.iso()
        fn(p)
        if not p._bodies():
            bulgu.append((ad, "GOVDE YOK", 0))
    except Exception as e:
        bulgu.append((ad, f"HATA {e}", 0))
        print("   HATA", e)
    try:
        sw.CloseAllDocuments(True)
    except Exception:
        sw = connect()
print("\nBULGU SAYISI:", len(bulgu))
for b in bulgu:
    print(" -", b)
