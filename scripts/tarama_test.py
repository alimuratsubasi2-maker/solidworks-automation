import os
from swlib import connect, T
from tr_pro import Resim
from v6_yeni_parcalar import HEDEF

sw = connect()
sw.SetUserPreferenceToggle(10, False)
sw.CloseAllDocuments(True)
yol = os.path.join(HEDEF, "Piston parcalari", "Piston Head.SLDPRT")
r = sw.OpenDoc6(yol, 1, 1, "", 0, 0)
pm = T(r[0] if isinstance(r, tuple) else r, "IModelDoc2")
pd = T(pm, "IPartDoc")
db = r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\turkish\sldmaterials\SolidWorks Materials.sldmat"
print(os.path.exists(db))
for cand in (db, "SOLIDWORKS Materials"):
    try:
        print("material:", pd.SetMaterialPropertyName2("", cand, "Plain Carbon Steel"), cand)
        break
    except Exception as e:
        print("hata", e)
pm.Save3(1, 0, 0)
sw.CloseAllDocuments(True)
R = Resim(sw, yol, "x", "x", gorunumler=("on",), iso=False, kesit=("on", 0.0))
sv = R.views["kesit"]
print("solid hatch:", sv.GetSolidHatchCount(), " face hatch:", sv.GetFaceHatchCount())
R.m.SaveAs3(os.path.join(HEDEF, "Teknik Resimler", "_h.pdf"), 0, 1)
sw.CloseAllDocuments(True)
