"""Pilot: ornek-stilde (taranmis kesit + tam olculer + golgeli izometrik) tek parca. python tr_pilot.py "Piston Head" """
import os
import sys
from swlib import connect
from tr_pro import Resim
from tr_specler import SPEC, KESIT
from v6_yeni_parcalar import HEDEF

sw = connect()
sw.SetUserPreferenceToggle(10, False)
sw.CloseAllDocuments(True)
istenen = sys.argv[1].lower()
for rel, (fn, gor, malz) in SPEC.items():
    if istenen in rel.lower():
        ad = os.path.basename(rel)
        R = Resim(sw, os.path.join(HEDEF, rel + ".SLDPRT"), ad, malz, gorunumler=tuple(g for g in gor if g != "yan"),
                  kesit=KESIT.get(rel), sade=False)
        fn(R)
        sp = os.environ.get("TR_PREVIEW")
        if sp:
            R.on_izleme = sp          # kontrol amacli gecici PDF (bitir icinde, belge kapanmadan once)
        R.bitir(os.path.join(HEDEF, "Teknik Resimler", ad))
        print("tamam:", ad)
        break
sw.SetUserPreferenceToggle(10, True)
