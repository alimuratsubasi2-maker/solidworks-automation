"""SolidWorks API yardimcilari (pywin32). Tum olculer mm olarak verilir, API'ye metre gider."""
import math
import time
import pythoncom
import win32com.client
from win32com.client import VARIANT

MM = 0.001
TEMPLATE = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\templates\Parça.prtdot"


MOD = win32com.client.gencache.EnsureModule("{83A33D31-27C5-11CE-BFD4-00400513BB57}", 0, 34, 0)


def T(obj, iface):
    """COM nesnesini SolidWorks tip kutuphanesindeki arayuzle sar."""
    if obj is None:
        return None
    return getattr(MOD, iface)(getattr(obj, "_oleobj_", obj))


def connect():
    sw = T(win32com.client.Dispatch("SldWorks.Application"), "ISldWorks")
    sw.Visible = True
    return sw


def darr(vals):
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(v) for v in vals])


class Part:
    def __init__(self, sw, model=None):
        self.sw = sw
        self.m = T(model or sw.NewDocument(TEMPLATE, 0, 0, 0), "IModelDoc2")
        self.sm = T(self.m.SketchManager, "ISketchManager")
        self.fm = T(self.m.FeatureManager, "IFeatureManager")
        self.sm.AddToDB = True
        self.planes = {}
        std = []
        f = T(self.m.FirstFeature(), "IFeature")
        while f is not None:
            if f.GetTypeName2() == "RefPlane":
                std.append(f)
            f = T(f.GetNextFeature(), "IFeature")
        self.planes["front"], self.planes["top"], self.planes["right"] = std[:3]

    # ---------- referans duzlem ----------
    def plane(self, name, base, dist_mm, flip=False):
        """base duzlemine paralel, dist_mm uzakta duzlem (flip=True: normalin ters tarafinda)."""
        if name in self.planes:
            return self.planes[name]
        self.m.ClearSelection2(True)
        self.planes[base].Select2(False, 0)
        self.fm.InsertRefPlane(8 | (256 if flip else 0), dist_mm * MM, 0, 0, 0, 0)
        f = T(self.m.FeatureByPositionReverse(0), "IFeature")
        f.Name = name
        self.planes[name] = f
        return f

    # ---------- eskiz ----------
    def sketch(self, plane):
        self.m.ClearSelection2(True)
        self.planes[plane].Select2(False, 0)
        self.sm.InsertSketch(True)

    def end_sketch(self):
        self.sm.InsertSketch(True)
        self.m.ClearSelection2(True)
        sk = T(self.m.FeatureByPositionReverse(0), "IFeature")
        sk.Select2(False, 0)
        return sk

    def circle(self, x, y, r):
        self.sm.CreateCircleByRadius(x * MM, y * MM, 0, r * MM)

    def poly(self, pts):
        n = len(pts)
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            self.sm.CreateLine(x1 * MM, y1 * MM, 0, x2 * MM, y2 * MM, 0)

    def rect(self, x1, y1, x2, y2):
        self.poly([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])

    def centerline(self, x1, y1, x2, y2):
        self.sm.CreateCenterLine(x1 * MM, y1 * MM, 0, x2 * MM, y2 * MM, 0)

    # ---------- ozellikler ----------
    def _bodies(self):
        b = T(self.m, "IPartDoc").GetBodies2(0, False)
        return [T(x, "IBody2") for x in b] if b else []

    def extrude(self, depth, mid=False, reverse=False, merge=False, depth2=None, draft=0.0, draft_out=False):
        before = self._bodies()
        self.fm.FeatureExtrusion3(
            depth2 is None, False, reverse, 6 if mid else 0, 0, depth * MM, (depth2 or 0) * MM,
            draft != 0, False, draft_out, False, math.radians(draft), 0, False, False, False, False,
            merge, True, True, 0, 0, False)
        return self._new_body(before)

    def cut(self, depth=0, mid=False, reverse=False, through=False, both=False):
        if both:
            self.fm.FeatureCut4(
                False, False, False, 1, 1, 0.01, 0.01,
                False, False, False, False, 0, 0, False, False, False, False,
                False, True, True, True, True, False, 0, 0, False, False)
            return
        # FeatureCut4'te varsayilan yon eskiz normalinin TERSI; ekstruzyonla ayni anlam icin cevir.
        # Yanlis yonde kesme sessizce None doner (malzemeye degmez) -> otomatik ters yonle yeniden dene.
        def _kes(yon):
            return self.fm.FeatureCut4(
                True, False, yon, 1 if through else (6 if mid else 0), 0, depth * MM, 0,
                False, False, False, False, 0, 0, False, False, False, False,
                False, True, True, True, True, False, 0, 0, False, False)
        f = _kes(not reverse)
        if f is None and not mid:
            f = _kes(reverse)
            if f is not None:
                print("   (kesme yonu otomatik cevrildi)", flush=True)
        if f is None:
            print("   ! kesme malzemeye degmedi", flush=True)

    def revolve(self, angle_deg=360, cut=False, merge=False):
        before = self._bodies()
        self.fm.FeatureRevolve2(
            True, True, False, cut, False, False, 0, 0,
            math.radians(angle_deg), 0, False, False, 0, 0, 0, 0, 0,
            merge or cut, True, True)       # revolve KESME merge=True olmadan sessizce hicbir sey yapmaz
        return None if cut else self._new_body(before)

    def _new_body(self, before):
        after = self._bodies()
        ids = [b.Name for b in before]
        new = [b for b in after if b.Name not in ids]
        return new[-1] if new else None

    def style(self, body, name, rgb, transp=0.0, shine=0.4):
        if body is None:
            return
        try:
            body.Name = name
        except Exception:
            pass
        r, g, b = rgb
        body.MaterialPropertyValues2 = darr([r, g, b, 0.6, 0.85, shine, 0.4, transp, 0.0])

    def arc(self, cx, cy, x1, y1, x2, y2, ccw=True):
        self.sm.CreateArc(cx * MM, cy * MM, 0, x1 * MM, y1 * MM, 0, x2 * MM, y2 * MM, 0, 1 if ccw else -1)

    def hide_planes(self):
        self.m.ClearSelection2(True)
        for f in self.planes.values():
            f.Select2(True, 0)
        self.m.BlankRefGeom()
        self.m.ClearSelection2(True)

    def hide_sketches(self):
        self.m.ClearSelection2(True)
        f = T(self.m.FirstFeature(), "IFeature")
        while f is not None:
            if f.GetTypeName2() == "ProfileFeature":
                f.Select2(False, 0)
                self.m.BlankSketch()
            sub = T(f.GetFirstSubFeature(), "IFeature")
            while sub is not None:
                if sub.GetTypeName2() == "ProfileFeature":
                    sub.Select2(False, 0)
                    self.m.BlankSketch()
                sub = T(sub.GetNextSubFeature(), "IFeature")
            f = T(f.GetNextFeature(), "IFeature")
        self.m.ClearSelection2(True)

    def iso(self):
        self.m.ShowNamedView2("*Isometric", 7)
        self.m.ViewZoomtofit2()
        self.m.GraphicsRedraw2()

    def style_all(self, rgb, transp=0.0, shine=0.5):
        for b in self._bodies():
            if not b.MaterialPropertyValues2:
                self.style(b, b.Name, rgb, transp, shine)

    def view(self):
        """Motorun on yuzu -Z'de: arkadan bakis + saga cevir + yukaridan egim."""
        self.m.ShowNamedView2("*Back", 2)
        v = T(self.m.ActiveView, "IModelView")
        v.RotateAboutCenter(0, -0.6)
        v.RotateAboutCenter(0.45, 0)
        self.m.ViewZoomtofit2()
        self.m.GraphicsRedraw2()


def bbox(body):
    b = body.GetBodyBox()
    return [round(v / MM, 1) for v in b]
