"""Aktif modeli onden-ustten, hafif yandan goster ve gorsel kaydet.
Kullanim: python kamera.py <cikti.bmp> [xaci] [yaci]"""
import sys
from swlib import connect, T

sw = connect()
m = T(sw.ActiveDoc, "IModelDoc2")
xa = float(sys.argv[2]) if len(sys.argv) > 2 else 0.45
ya = float(sys.argv[3]) if len(sys.argv) > 3 else -0.6
m.ShowNamedView2("*Back", 2)
v = T(m.ActiveView, "IModelView")
v.RotateAboutCenter(0, ya)
v.RotateAboutCenter(xa, 0)
m.ViewZoomtofit2()
m.GraphicsRedraw2()
m.SaveBMP(sys.argv[1], 1600, 1000)
