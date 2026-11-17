from swlib import connect, Part, T, darr

sw = connect()
p = Part(sw, sw.ActiveDoc)
bodies = p._bodies()
vals = darr([0.86, 0.66, 0.12, 0.6, 0.85, 0.9, 0.4, 0.0, 0.0])

b = [x for x in bodies if x.Name == "Hava Filtresi Sol"][0]
print("once v1:", b.MaterialPropertyValues, " v2:", b.MaterialPropertyValues2)
b.MaterialPropertyValues2 = vals
print("sonra v2:", b.MaterialPropertyValues2)

# ikinci yontem: govdeyi olusturan ozellik uzerinden
b2 = [x for x in bodies if x.Name == "Hava Filtresi Sag"][0]
feats = b2.GetFeatures()
print("ozellikler:", [T(f, "IFeature").Name for f in feats])
f = T(feats[-1], "IFeature")
print("feat set:", f.SetMaterialPropertyValues2(vals, 2, None))
p.m.GraphicsRedraw2()
p.m.SaveBMP(r"C:\Users\MSI\AppData\Local\Temp\claude\c--Users-MSI-Desktop-ETSY-MAGAZASI----N--R-NLER\3969b6e5-a38c-498b-8d58-69190f22786a\scratchpad\renk.bmp", 1200, 800)
