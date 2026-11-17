from swlib import connect, Part
import math

sw = connect()
sw.CloseAllDocuments(True)
for rev in (False, True):
    p = Part(sw)
    p.sketch("top"); p.rect(-20, -20, 20, 20); p.end_sketch(); p.extrude(10)
    p.sketch("top"); p.circle(0, 0, 5); p.end_sketch()
    f = p.fm.FeatureCut4(True, False, not rev, 0, 0, 0.005, 0, False, False, False, False, 0, 0, False, False, False, False,
                         False, True, True, True, True, False, 0, 0, False, False)
    print("reverse" if rev else "default", "-> feature:", f is not None, " yuz:", p._bodies()[0].GetFaceCount())
    sw.CloseAllDocuments(True)
