"""Profesyonel parca teknik resimlerini uretir: python tr_calistir.py [filtre ...]"""
import os
import sys
import traceback

from swlib import connect
from tr_pro import Resim
from tr_specler import SPEC, KESIT
from v6_yeni_parcalar import HEDEF

CIKTI = os.path.join(HEDEF, "Teknik Resimler")


def main():
    filt = [f.lower() for f in sys.argv[1:]]
    sw = connect()
    sw.SetUserPreferenceToggle(10, False)
    sw.CloseAllDocuments(True)
    os.makedirs(CIKTI, exist_ok=True)
    ok = 0
    try:
        for rel, (fn, gor, malz) in SPEC.items():
            if filt and not any(f in rel.lower() for f in filt):
                continue
            ad = os.path.basename(rel)
            try:
                if "Piston Head" in rel:
                    gor = tuple(g for g in gor if g != "yan")          # ornek stil yerlesimi
                R = Resim(sw, os.path.join(HEDEF, rel + ".SLDPRT"), ad, malz, gorunumler=gor, kesit=KESIT.get(rel),
                          sade=False)
                notlar = fn(R) or []
                R.bitir(os.path.join(CIKTI, ad), notlar)
                ok += 1
                print(f"OK   {ad:24s} olcek {R.a}:{R.b}", flush=True)
            except Exception:
                print(f"HATA {ad}")
                traceback.print_exc()
                try:
                    sw.CloseAllDocuments(True)
                except Exception:
                    import time
                    time.sleep(8)
                    sw = connect()                      # SolidWorks coktuyse yeniden baslat
                    sw.SetUserPreferenceToggle(10, False)
                    sw.CloseAllDocuments(True)
    finally:
        sw.SetUserPreferenceToggle(10, True)
    print("Basarili:", ok)


if __name__ == "__main__":
    main()
