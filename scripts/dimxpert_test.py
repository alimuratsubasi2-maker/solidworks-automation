import pythoncom
import win32com.client
from swlib import connect, T, MM

la = pythoncom.LoadTypeLib(r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\swdimxpert.tlb").GetLibAttr()
DX = win32com.client.gencache.EnsureModule(str(la[0]), la[1], la[3], la[4])
print("opsiyonlar:", [a for a in dir(DX.IDimXpertAutoDimSchemeOption) if not a.startswith("_") and a not in ("CLSID", "coclass_clsid")])

sw = connect()
sw.CloseAllDocuments(True)
r = sw.OpenDoc6(r"C:\Users\MSI\Desktop\V6 MOTOR YENI\Piston parcalari\Piston Head.SLDPRT", 1, 1, "", 0, 0)
m = T(r[0] if isinstance(r, tuple) else r, "IModelDoc2")
mgr = T(m.Extension, "IModelDocExtension").DimXpertManager("", True)
part = DX.IDimXpertPart(mgr.DimXpertPart._oleobj_)
opt = part.GetAutoDimSchemeOption()
opt.PartType = 1          # 1 = donel (turned), 0 = prizmatik
ok = part.AutoDimensionScheme(opt)
print("sema olustu:", ok, " ozellik:", part.GetFeatureCount(), " ek:", part.GetAnnotationCount())
m.ForceRebuild3(False)
m.Save3(1, 0, 0)
