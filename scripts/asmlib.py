"""SolidWorks montaj yardimcilari: parca ekle, eksenlerle yerlestir, sabitle."""
import os
from swlib import T, darr, MM

ASM_TEMPLATE = r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Montaj.ASMDOT"


def unit(v):
    n = sum(c * c for c in v) ** 0.5
    return tuple(c / n for c in v)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


class Asm:
    def __init__(self, sw, folder):
        self.sw = sw
        self.folder = folder
        self.loaded = set()
        self.mu = T(sw.GetMathUtility(), "IMathUtility")
        self.m = T(sw.NewDocument(ASM_TEMPLATE, 0, 0, 0), "IModelDoc2")
        self.a = T(self.m, "IAssemblyDoc")
        self.comps = []

    def _load(self, path):
        if path in self.loaded:
            return
        self.sw.DocumentVisible(False, 1)
        self.sw.DocumentVisible(False, 2)
        r = self.sw.OpenDoc6(path, 2 if path.upper().endswith(".SLDASM") else 1, 1, "", 0, 0)
        self.sw.DocumentVisible(True, 1)
        self.sw.DocumentVisible(True, 2)
        if isinstance(r, tuple):
            r = r[0]
        if r is None:
            raise RuntimeError("Acilamadi: " + path)
        self.loaded.add(path)

    def add(self, name, origin=(0, 0, 0), x=(1, 0, 0), y=(0, 1, 0)):
        """name: klasordeki dosya adi (uzantili). origin mm; x,y: parcanin yerel X ve Y
        eksenlerinin montajdaki yonu (Z otomatik = X x Y)."""
        path = os.path.join(self.folder, name)
        self._load(path)
        c = T(self.a.AddComponent5(path, 0, "", False, "", 0, 0, 0), "IComponent2")
        if c is None:
            raise RuntimeError("Eklenemedi: " + name)
        x = unit(x)
        y = unit(y)
        z = cross(x, y)
        vals = list(x) + list(y) + list(z) + [v * MM for v in origin] + [1.0, 0, 0, 0]
        c.Transform2 = T(self.mu.CreateTransform(darr(vals)), "IMathTransform")
        self.comps.append(c)
        return c

    def fix_all(self):
        self.m.ClearSelection2(True)
        for c in self.comps:
            c.Select4(True, None, False)
        self.a.FixComponent()
        self.m.ClearSelection2(True)

    def save(self, name):
        self.fix_all()
        self.m.ForceRebuild3(False)
        self.m.ShowNamedView2("*Isometric", 7)
        self.m.ViewZoomtofit2()
        path = os.path.join(self.folder, name)
        self.m.SaveAs3(path, 0, 1)
        return path


def box(c):
    b = c.GetBox(False, False)
    return [round(v / MM, 1) for v in b]
