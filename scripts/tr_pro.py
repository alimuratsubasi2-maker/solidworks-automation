"""Profesyonel parca teknik resmi motoru (A3, 1. aci izdusum).
Gorunusler: on / ust / sol-yan (+ izometrik). Ic detaylar kesikli cizgiyle gosterilir.
Olculer parcanin MODEL koordinatlarindan hesaplanir (mm) ve gercek deger olarak yazilir.
Bir olcu = sayfa eskizinde iki nokta + SolidWorks olcusu (isaretleme noktalari sonra gizlenir)."""
import os
from swlib import connect, T, MM, darr

DRW_TEMPLATE = r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Teknik Resim.DRWDOT"
SAYFA = r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\lang\turkish\sheetformat\a3 - iso.slddrt"
W, H = 0.420, 0.297
OLCEKLER = [(10, 1), (5, 1), (2, 1), (1, 1), (1, 2), (1, 5), (1, 10)]


def proj(view, p):
    """Model noktasi (x,y,z mm) -> gorunus duzlemi (u,v) mm."""
    x, y, z = p
    if view == "on":
        return x, y
    if view == "ust":
        return x, -z
    return z, y          # yan (soldan bakis, 1. aci: on gorunusun sagina)


class Resim:
    def __init__(self, sw, yol, ad, malzeme="Celik", gorunumler=("on", "ust", "yan"), olcek=None, iso=True, kesit=None,
                 sade=True):
        self.kesit = kesit            # ("on", x_mm) veya ("ust", z_mm): kesit duzlemi
        self._sade_arg = sade
        self.sw, self.yol, self.ad = sw, yol, ad
        self.malzeme = malzeme
        r = sw.OpenDoc6(yol, 1, 1, "", 0, 0)
        pm = T(r[0] if isinstance(r, tuple) else r, "IModelDoc2")
        b = list(T(pm, "IPartDoc").GetPartBox(True))
        self.bb = [v / MM for v in b]
        sw.CloseAllDocuments(True)
        bx, by, bz = (self.bb[i + 3] - self.bb[i] for i in range(3))
        self.size = (bx, by, bz)
        a, bb_ = olcek or self.olcek_sec(bx, by, bz, gorunumler)
        self.a, self.b = a, bb_
        m = T(sw.NewDocument(DRW_TEMPLATE, 8, W, H), "IModelDoc2")
        self.m = m
        self.drw = T(m, "IDrawingDoc")
        sh = T(self.drw.GetCurrentSheet(), "ISheet")
        self.drw.SetupSheet5(sh.GetName(), 8, 12, a, bb_, True, SAYFA, W, H, "Default", True)
        self.sh = T(self.drw.GetCurrentSheet(), "ISheet")
        self.sh.SetScale(a, bb_, True, False)
        self.views = {}
        self.gor = gorunumler
        self.iso = iso
        self.yerlestir()

    def olcek_sec(self, bx, by, bz, gor):
        for a, b in OLCEKLER:
            s = a / b
            gen = bx * s + (bz * s if "yan" in gor else 0)
            yuk = by * s + (bz * s if "ust" in gor else 0)
            if gen <= 160 and yuk <= 138:
                return a, b
        return 1, 20

    def _view(self, adlar, x, y):
        for n in adlar:
            v = self.drw.CreateDrawViewFromModelView3(self.yol, n, x * MM, y * MM, 0)
            if v is not None:
                return T(v, "IView")
        raise RuntimeError("gorunus yok")

    def yerlestir(self):
        d = self.drw
        bx, by, bz = self.size
        on = self._view(["*Ön", "*Front"], 100, 200)
        # SolidWorks ilk gorunumde kendi olcegini secer; istedigimiz olcegi sonradan uygula
        self.sh.SetScale(self.a, self.b, True, False)
        on.UseSheetScale = False
        on.ScaleDecimal = self.a / self.b
        s = self.s = on.ScaleDecimal
        sol = 56 + bx * s / 2
        ust = 297 - 56 - by * s / 2
        on.Position = darr([sol * MM, ust * MM])
        self.views["on"] = on
        self._sec(on)
        if "yan" in self.gor:
            y = T(d.CreateUnfoldedViewAt3((sol + bx * s / 2 + 60 + bz * s / 2) * MM, ust * MM, 0, False), "IView")
            self.views["yan"] = y
            self._sec(on)
        if "ust" in self.gor:
            u = T(d.CreateUnfoldedViewAt3(sol * MM, (ust - by * s / 2 - 55 - bz * s / 2) * MM, 0, False), "IView")
            self.views["ust"] = u
        for k in ("yan", "ust"):
            if k in self.views:
                self.views[k].UseSheetScale = False
                self.views[k].ScaleDecimal = s
        if self.iso:
            iv = self._view(["*İzometrik", "*Isometric"], *((355, 215) if self.kesit else (345, 150)))
            iv.UseSheetScale = False
            iv.ScaleDecimal = min(s, (85 if self.kesit else 95) / (max(bx, by, bz) * 1.6))
            iv.SetDisplayMode4(False, 7, False, True, False)
            self.views["iso"] = iv
        self.sade = self._sade_arg
        for k in ("on", "ust", "yan"):
            if k in self.views:
                self.views[k].SetDisplayMode4(False, 2, False, True, False)   # sade: gizli cizgiler yok
        # outline ve bbox merkezi (olculer eklenmeden once alinir)
        self.out = {k: list(v.GetOutline()) for k, v in self.views.items()}
        if self.kesit:
            self._kesit_yap()

    def _kesit_yap(self):
        """Parcanin ortasindan kesit gorunus: on gorunusten dikey cizgi (x) veya ust gorunusten yatay cizgi (z)."""
        src, pos = self.kesit
        sv_ = self.views[src]
        self.drw.ActivateView(sv_.Name)
        o = self.out[src]
        sm = T(self.m.SketchManager, "ISketchManager")
        sm.AddToDB = True
        self._katman("KESITCIZGI")
        # aktif gorunumde eskiz koordinati = MODEL koordinati (metre), sayfa degil
        # (origin = gorunusun MERKEZI, birim = model metresi)
        b = self.bb
        xc, yc, zc = (b[0] + b[3]) / 2, (b[1] + b[4]) / 2, (b[2] + b[5]) / 2
        if src == "on":
            xr = (pos - xc) * MM
            h = (b[4] - b[1]) / 2 * MM + 0.015
            seg = sm.CreateLine(xr, -h, 0, xr, h, 0)
        else:
            yr = (zc - pos) * MM
            w = (b[3] - b[0]) / 2 * MM + 0.015
            seg = sm.CreateLine(-w, yr, 0, w, yr, 0)
        seg = T(seg, "ISketchSegment")
        self.m.ClearSelection2(True)
        seg.Select4(False, None)
        on_o = self.out["on"]
        if "ust" in self.out and "yan" not in self.out:      # ornek stil: kesit, on gorunusun hemen yaninda
            bx_, by_, bz_ = self.size
            gen = (bz_ if src == "on" else bx_) * self.s * MM
            px = on_o[2] + 0.075 + gen / 2
            py = (on_o[1] + on_o[3]) / 2
        elif "ust" in self.out:
            bx_, by_, bz_ = self.size
            w = (bz_ if src == "on" else bx_) * self.s * MM
            # ust gorunusun sag olculerinin (146.05, 508 ...) uzerine binmesin
            px = max((self.out["yan"][0] + self.out["yan"][2]) / 2, self.out["ust"][2] + 0.095 + w / 2)
            px = min(px, 0.405 - w / 2)
            py = (self.out["ust"][1] + self.out["ust"][3]) / 2
        else:           # ust gorunus yok: kesiti on gorunusun altina koy (antetle cakismasin)
            px = (on_o[0] + on_o[2]) / 2
            py = on_o[1] - (on_o[3] - on_o[1]) / 2 - 0.05
        sv = T(self.drw.CreateSectionViewAt5(px, py, 0, "A", 1, None, 0), "IView")
        sv.UseSheetScale = False
        sv.ScaleDecimal = self.s
        sv.SetDisplayMode4(False, 1, False, True, False)      # ic boslugun cizgileri de gorunsun
        self.views["kesit"] = sv
        self.out["kesit"] = list(sv.GetOutline())
        self._vx_kesit = T(sv.ModelToViewTransform, "IMathTransform")
        self._katman("OLCU")
        self.m.ClearSelection2(True)

    def _sec(self, v):
        self.m.ClearSelection2(True)
        T(self.m.Extension, "IModelDocExtension").SelectByID2(v.Name, "DRAWINGVIEW", 0, 0, 0, False, 0, None, 0)

    # ---- koordinat esleme: model mm -> sayfa metre ----
    def sayfa(self, view, p):
        if view == "kesit":
            mu = T(self.sw.GetMathUtility(), "IMathUtility")
            pt = T(mu.CreatePoint(darr([p[0] * MM, p[1] * MM, p[2] * MM])), "IMathPoint")
            q = T(pt.MultiplyTransform(self._vx_kesit), "IMathPoint").ArrayData
            return q[0], q[1]
        u, v = proj(view, p)
        uc = (proj(view, (self.bb[0], self.bb[1], self.bb[2]))[0] + proj(view, (self.bb[3], self.bb[4], self.bb[5]))[0]) / 2
        vc = (proj(view, (self.bb[0], self.bb[1], self.bb[2]))[1] + proj(view, (self.bb[3], self.bb[4], self.bb[5]))[1]) / 2
        o = self.out[view]
        cx, cy = (o[0] + o[2]) / 2, (o[1] + o[3]) / 2
        return cx + (u - uc) * self.s * MM, cy + (v - vc) * self.s * MM

    # ---- olculer ----
    def _noktalar(self):
        self.drw.EditSheet()
        sm = T(self.m.SketchManager, "ISketchManager")
        sm.AddToDB = True
        return sm

    def _katman(self, ad, renk=0, gorunur=True):
        lm = T(self.m.GetLayerManager(), "ILayerMgr")
        if not hasattr(self, "_kat"):
            self._kat = {}
        if ad not in self._kat:
            lm.AddLayer(ad, ad, renk, 0, 0)
            self._kat[ad] = True
        lm.SetCurrentLayer(ad)
        return lm

    def _dim(self, p1, p2, tip, tx, ty, onek=None):
        sm = self._noktalar()
        k = 1 / self.s
        self._katman("NOKTA")
        a = sm.CreatePoint(p1[0] * k, p1[1] * k, 0)
        b = sm.CreatePoint(p2[0] * k, p2[1] * k, 0)
        self._katman("OLCU")
        self.m.ClearSelection2(True)
        T(a, "ISketchPoint").Select4(False, None)
        T(b, "ISketchPoint").Select4(True, None)
        if tip == "h":
            dd = self.m.AddHorizontalDimension2(tx, ty, 0)
        elif tip == "v":
            dd = self.m.AddVerticalDimension2(tx, ty, 0)
        else:
            dd = self.m.AddDimension2(tx, ty, 0)
        self.m.ClearSelection2(True)
        if dd is None:
            print("   ! olcu eklenemedi:", tip, [round(v / MM) for v in (p1[0], p1[1], p2[0], p2[1])], flush=True)
        if dd is not None and onek:
            T(dd, "IDisplayDimension").SetText(1, onek)
        return dd

    def _yeni_olcu(self, tip, view, c1, c2):
        """Ayni gorunusta ayni iki cizgi arasina ikinci kez olcu konmasini engeller."""
        if not hasattr(self, "_gorulen"):
            self._gorulen = set()
        key = (tip, view, round(min(c1, c2) * 1e5), round(max(c1, c2) * 1e5))
        if key in self._gorulen:
            return False
        self._gorulen.add(key)
        return True

    def _yer(self, view, taraf, lo, hi, kat, metin=0.016):
        """Ayni tarafta cakisan olculeri farkli katlara kaydir. lo/hi: sayfa metre."""
        if not hasattr(self, "_dolu"):
            self._dolu = {}
        mid, w = (lo + hi) / 2, max(hi - lo, metin)
        a0, a1 = mid - w / 2, mid + w / 2
        while True:
            liste = self._dolu.setdefault((view, taraf, kat), [])
            if all(a1 < b0 - 0.001 or a0 > b1 + 0.001 for b0, b1 in liste) or kat >= 5:
                liste.append((a0, a1))
                return kat
            kat += 1

    def _k(self, view, p):
        """Yan gorunuste spec noktalari (z, y, 0) yazilir -> model (0, y, z)."""
        if view == "yan" and not getattr(self, "_uc_boyut", False):
            return (0, p[1], p[0])
        return p

    def h(self, view, p1, p2, taraf="ust", kat=1, onek=None):
        """Yatay olcu. taraf: 'ust'/'alt'; kat: gorunus kenarindan uzaklik (kat x 9 mm)."""
        if view not in self.views:
            return None
        if getattr(self, "sade", False) and not getattr(self, "_genel_cagri", False) and view != "kesit":
            return None            # sade mod: sadece genel boyutlar + cap olculeri (kesitte ic olculer serbest)
        if view == "ust" and taraf == "ust":
            taraf = "alt"          # ust gorunusun ustu, on gorunusun alt olculeriyle cakisir
        p1, p2 = self._k(view, p1), self._k(view, p2)
        a, b = self.sayfa(view, p1), self.sayfa(view, p2)
        o = self.out[view]
        if not self._yeni_olcu("h", view, a[0], b[0]):
            return None            # ayni aralik zaten olculendirilmis
        kat = self._yer(view, taraf, min(a[0], b[0]), max(a[0], b[0]), kat)
        ty = o[3] + (6 + 9 * kat) * MM if taraf == "ust" else o[1] - (6 + 9 * kat) * MM
        return self._dim(a, b, "h", (a[0] + b[0]) / 2, ty, onek)

    def v(self, view, p1, p2, taraf="sol", kat=1, onek=None):
        if view not in self.views:
            return None
        if getattr(self, "sade", False) and not getattr(self, "_genel_cagri", False) and view != "kesit":
            return None
        if view == "yan" and taraf == "sol":
            taraf = "sag"          # yan gorunumun solu, on gorunusun sag olculeriyle cakisir
        p1, p2 = self._k(view, p1), self._k(view, p2)
        a, b = self.sayfa(view, p1), self.sayfa(view, p2)
        o = self.out[view]
        if not self._yeni_olcu("v", view, a[1], b[1]):
            return None
        kat = self._yer(view, taraf, min(a[1], b[1]), max(a[1], b[1]), kat)
        tx = o[0] - (6 + 9 * kat) * MM if taraf == "sol" else o[2] + (6 + 9 * kat) * MM
        return self._dim(a, b, "v", tx, (a[1] + b[1]) / 2, onek)

    def cap(self, view, merkez, r, eksen="x", yon=1, mesafe=9, onek="Ø"):
        """Daire/silindir capi: dairenin merkezinden gecen cizgi, yazi dairenin disinda.
        eksen: x -> yatay olcu, y -> dikey olcu. yon: +1 sag/ust, -1 sol/alt tarafa yazar."""
        if view not in self.views:
            return None
        c = self.sayfa(view, self._k(view, merkez))
        rr = r * self.s * MM
        if eksen == "x":
            a, b = (c[0] - rr, c[1]), (c[0] + rr, c[1])
        else:
            a, b = (c[0], c[1] - rr), (c[0], c[1] + rr)
        tip = "h" if eksen == "x" else "v"
        d = mesafe * MM * yon
        if tip == "h":
            tx, ty = (b[0] if yon > 0 else a[0]) + d, a[1]
        else:
            tx, ty = a[0], (b[1] if yon > 0 else a[1]) + d
        return self._dim(a, b, tip, tx, ty, onek)

    def pt(self, view, p, onek=None):
        return self.sayfa(view, p)

    def genel(self, hk=1, vk=1, lk=1, yan=True):
        """Genel boy / en / yukseklik olculeri (en dis katta)."""
        b = self.bb
        self._genel_cagri = True
        try:
            self._genel_ic(b, hk, vk, lk, yan)
        finally:
            self._genel_cagri = False

    def _genel_ic(self, b, hk, vk, lk, yan):
        if "on" in self.views:
            self.h("on", (b[0], b[4], b[2]), (b[3], b[4], b[2]), "ust", hk)
            self.v("on", (b[0], b[1], b[2]), (b[0], b[4], b[2]), "sol", vk)
        if "ust" in self.views:
            self.v("ust", (b[3], b[4], b[2]), (b[3], b[4], b[5]), "sag", lk)
        elif "yan" in self.views and yan:
            self.h("yan", (b[2], b[4], 0), (b[5], b[4], 0), "ust", lk)

    def not_(self, metin, x, y, pt=10):
        n = self.m.InsertNote(metin)
        if n is None:
            return
        n = T(n, "INote")
        n.SetHeightInPoints(pt)
        T(n.GetAnnotation(), "IAnnotation").SetPosition2(x * MM, y * MM, 0)

    def bitir(self, cikti, notlar=()):
        # isaretleme noktalarini gizle
        self.m.ClearSelection2(True)
        lm = T(self.m.GetLayerManager(), "ILayerMgr")
        try:
            ly = T(lm.GetLayer("NOKTA"), "ILayer")
            ly.Visible = False
        except Exception:
            pass
        lm.SetCurrentLayer("0") if False else None
        self.drw.ActivateSheet(self.sh.GetName())
        sc = f"{self.a}:{self.b}"
        self.not_(f"{self.ad}   |   V6 MOTOR   |   Malzeme: {self.malzeme}   |   Olculer: mm   |   Olcek {sc}", 20, 16, 11)
        # sadece olculendirilemeyen bilgiler icin kisa notlar (en cok 3 satir)
        import re
        y = 22
        for n in list(notlar)[:3]:
            self.not_(re.sub(r"\bO(?=\d)", "Ø", n), 20, y, 9)
            y += 6
        self.m.ForceRebuild3(False)
        self.m.SaveAs3(cikti + ".SLDDRW", 0, 1)
        # kullanici PDF/PNG istemiyor: sadece .SLDDRW (on_izleme: sadece kontrol icin, scratchpad'e)
        if getattr(self, "on_izleme", None):
            self.m.SaveAs3(self.on_izleme, 0, 1)
        self.sw.CloseAllDocuments(True)

