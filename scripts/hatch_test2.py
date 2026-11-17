import os
from swlib import connect, T, MM
from tr_pro import Resim
from v6_yeni_parcalar import HEDEF

sw = connect()
sw.SetUserPreferenceToggle(10, False)
sw.CloseAllDocuments(True)
yol = os.path.join(HEDEF, "Piston parcalari", "Piston Head.SLDPRT")
R = Resim(sw, yol, "x", "x", gorunumler=("on",), iso=False, kesit=("on", 0.0))
sv = R.views["kesit"]
o = sv.GetOutline()
print("kesit outline mm:", [round(v / MM) for v in o])
sv.SetDisplayMode4(False, 2, False, True, False)
R.m.ForceRebuild3(False)
sp = r"C:\Users\MSI\AppData\Local\Temp\claude\fe524e2f6919b122\3969b6e5-a38c-498b-8d58-69190f22786a\scratchpad"
R.m.SaveAs3(sp + r"\_hh.pdf", 0, 1)
sw.CloseAllDocuments(True)
