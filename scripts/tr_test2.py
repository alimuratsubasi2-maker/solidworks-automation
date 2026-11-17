import os
from swlib import connect
from tr_pro import Resim
from v6_yeni_parcalar import HEDEF

sw = connect()
sw.SetUserPreferenceToggle(10, False)
sw.CloseAllDocuments(True)
R = Resim(sw, os.path.join(HEDEF, "OilPan.SLDPRT"), "OilPan", "Dokum celik")
print("olcek", R.a, R.b, "s", R.s, "outlines", {k: [round(x * 1000) for x in v] for k, v in R.out.items()})
bb = R.bb
# on gorunus (x,y):
R.h("on", (-165.1, 25.4, 0), (165.1, 25.4, 0), "ust", 1)
R.h("on", (-110, -101.6, 0), (110, -101.6, 0), "alt", 1)
R.v("on", (-165.1, 25.4, 0), (-165.1, 0, 0), "sol", 1)
R.v("on", (-165.1, 25.4, 0), (-165.1, -101.6, 0), "sol", 2)
# ust gorunus (x,-z)
R.h("ust", (-165.1, 0, 0), (165.1, 0, 0), "alt", 1)
R.v("ust", (165.1, 0, 0), (165.1, 0, 508), "sag", 1)
R.bitir(os.path.join(HEDEF, "Teknik Resimler", "_t2"))
