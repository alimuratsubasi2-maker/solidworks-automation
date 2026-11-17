"""26 parcanin olcu listeleri. Her fonksiyon Resim nesnesine (R) olculer ekler.
Koordinatlar parcanin MODEL koordinatidir (v6_yeni_parcalar.py'deki cizimle ayni).
Gorunus esleme: on=(x,y)  ust=(x,-z)  yan=(z,y).  kat = gorunus kenarindan olcu sirasi."""
import math

PITCH = 146.05
ZC = [107.95, 254.0, 400.05]      # kapak/egzoz silindir merkezleri (yerel z)


def Pt(x, y, z):
    return (x, y, z)


# ---------------------------------------------------------------- ana blok / kapak / karter
def engine_block(R):
    b = R.bb
    # on gorunus: krank deligi + hazne capi (z=0 yuzunden bakilir, kesikli)
    R.cap("on", (0, 0, b[2]), 40.1, "x", yon=-1)
    R.cap("on", (0, 0, b[2]), 118.0, "y", yon=1)
    R.h("on", (-255.9, 255.9, b[2]), (0, 255.9, b[2]), "ust", 1) if False else None
    R.v("on", (-150, -25.4, b[2]), (-150, 120, b[2]), "sol", 1)         # taban blok yuksekligi 145.4
    R.h("on", (-150, -25.4, b[2]), (150, -25.4, b[2]), "alt", 1)        # taban genisligi 300
    R.genel(2, 2, 1)
    # ust gorunus: silindir merkezleri ve blok boyu
    for z in (73.935, 219.895, 365.855):
        pass
    R.v("ust", (255.9, 255.9, 73.935), (255.9, 255.9, 219.895), "sag", 1)   # silindir araligi 145.96
    R.v("ust", (255.9, 255.9, 219.895), (255.9, 255.9, 365.855), "sag", 1)
    R.v("ust", (255.9, 255.9, b[2]), (255.9, 255.9, 73.935), "sag", 2)      # on yuzden ilk silindire 95.3
    # kesit (x=0): krank boslugu (z, y duzlemi)
    R.h("kesit", (0, 60, -21.4), (0, 60, -9.4), "ust", 1)                   # on duvar 12
    R.h("kesit", (0, 60, 474.6), (0, 60, 486.6), "ust", 1)                  # arka duvar 12
    R.v("kesit", (0, -25.4, 200), (0, 118, 200), "sag", 1)                  # bosluk yuksekligi 143.4
    R.v("kesit", (0, -40.1, -21.4), (0, 40.1, -21.4), "sol", 1)             # krank deligi O80.2
    R.v("ust", (255.9, 255.9, 73.935), (255.9, 255.9, 99.335), "sag", 3) if False else None
    return ["6 adet O127.6 silindir deligi (piston O127 + 0.3 pay): eksenler dikeyden +-45 derece (90 derece V), derinlik: ust yuzden 169.4 mm",
            "Sira kaydirmasi: sag sira z=+25.4 mm geride. Krank boslugu O236, krank deligi O80.2, uc duvar kalinligi 12 mm"]


def cylinder_head(R):
    b = R.bb
    zc = ZC
    # ust (x,-z): deliklerin konumlari
    R.h("ust", (-28, 0, zc[0]), (28, 0, zc[0]), "alt", 1)                # 56 supap deligi araligi
    R.h("ust", (-70, 0, 25), (70, 0, 25), "alt", 2)                      # 140 civata araligi
    R.v("ust", (82.55, 0, zc[0]), (82.55, 0, zc[1]), "sag", 1)           # 146.05
    R.v("ust", (82.55, 0, zc[1]), (82.55, 0, zc[2]), "sag", 1)
    R.v("ust", (82.55, 0, 0), (82.55, 0, zc[0]), "sag", 2)               # uctan ilk silindire 107.95
    R.cap("ust", (28, 0, zc[0]), 11, "x", yon=1, mesafe=8)               # O22
    R.cap("ust", (0, 0, zc[0] - 40), 7, "x", yon=-1, mesafe=8)           # O14 buji
    R.cap("ust", (70, 0, 25), 6, "x", yon=1, mesafe=8)                   # O12 civata
    R.genel(2, 1, 3)
    # yan (z,y): yan portlar 31.8 x 38.1 (yukseklik y=25 .. 63.1)
    R.v("yan", (zc[0] - 28 + 15.9, 25, 0), (zc[0] - 28 + 15.9, 63.1, 0), "sol", 1) if False else None
    R.v("yan", (zc[0] + 28 + 15.9, 25, 0), (zc[0] + 28 + 15.9, 63.1, 0), "sag", 1)   # 38.1
    R.h("yan", (zc[0] - 28 - 15.9, 63.1, 0), (zc[0] - 28 + 15.9, 63.1, 0), "ust", 1)   # 31.8
    # kesit (x=0): kanal ve oda olculeri (z, y duzlemi)
    R.h("kesit", (0, 44, 64.05), (0, 44, 95.85), "ust", 1)                  # kanal genisligi 31.8
    R.v("kesit", (0, 25, 64.05), (0, 63.1, 64.05), "sol", 1)                # kanal yuksekligi 38.1
    R.v("kesit", (0, 0, 40), (0, 25, 40), "sol", 1)                         # tabandan kanala 25
    R.v("kesit", (0, 63.1, 480), (0, 85.7, 480), "sag", 1)                  # ust kalinlik 22.6
    R.v("kesit", (0, 0, 254), (0, 10, 254), "sag", 1)                       # yanma odasi derinligi 10
    return ["Supap delikleri O22 (6 adet), buji delikleri O14 (3 adet), civata delikleri O12 (8 adet) - hepsi gecirmeli",
            "Yan portlar: 31.8 x 38.1, y=25 ile y=63.1 arasi, her silindir icin 2 adet"]


def valves_cover(R):
    b = R.bb
    t = 10.16
    R.h("on", (-82.55, 63.5, 0), (-82.55 + t, 63.5, 0), "ust", 1)                    # duvar 10.16
    R.v("on", (0, 53.34, 0), (0, 63.5, 0), "sag", 1)                                  # ust kalinlik 10.16
    R.cap("ust", (-82.55 + 5, 0, 12), 3.2, "x", yon=1, mesafe=8)                      # O6.4 civata
    R.v("ust", (82.55, 0, 12), (82.55, 0, 107.41), "sag", 1)                          # 95.41
    R.v("ust", (82.55, 0, 107.41), (82.55, 0, 254), "sag", 1)                         # 146.59
    for k in range(3):
        pass
    R.v("ust", (-82.55, 0, 120.65), (-82.55, 0, 266.7), "sol", 1)                     # kavis araligi 146.05
    R.v("ust", (-82.55, 0, 0), (-82.55, 0, 120.65), "sol", 2)                         # uctan 120.65
    R.genel(2, 1, 3)
    R.h("yan", (120.65 - 20.32, 63.5, 0), (120.65 + 20.32, 63.5, 0), "ust", 1)        # O40.64 oyuk
    # kesit (x=0): ic bosluk (z, y duzlemi)
    R.v("kesit", (0, 53.34, 250), (0, 63.5, 250), "sag", 1)                          # ust kalinlik 10.16
    R.h("kesit", (0, 30, 0), (0, 30, 10.16), "alt", 1)                               # uc duvar 10.16
    R.v("kesit", (0, 0, 20), (0, 53.34, 20), "sol", 1)                               # ic yukseklik 53.34
    return ["Ic oyuk: duvar kalinligi 10.16 mm (yan ve ust); alt yuzden bos",
            "Sol kenarda 40.64 capinda 6 adet yari daire oyuk (63.5 derinlik), aralik 146.05 / 60.64 / 146.05"]


def oil_pan(R):
    b = R.bb
    R.v("on", (-165.1, 25.4, 0), (-165.1, 0, 0), "sol", 1)           # flans kalinligi
    R.v("on", (-165.1, 25.4, 0), (-165.1, -101.6, 0), "sol", 2)       # toplam yukseklik 127
    R.h("on", (-110, -101.6, 0), (110, -101.6, 0), "alt", 1)          # taban genisligi 220
    R.h("on", (-150, 0, 0), (150, 0, 0), "alt", 2)                    # govde genisligi 300
    R.h("on", (-165.1, 25.4, 0), (165.1, 25.4, 0), "ust", 1)          # flans genisligi
    R.h("on", (-150, -50, 0), (-140, -50, 0), "ust", 2) if False else None
    R.h("on", (140, 0, 0), (150, 0, 0), "ust", 2)                     # yan duvar 10 (ust)
    R.v("on", (110, -101.6, 0), (110, -91.4, 0), "sag", 1)            # taban kalinligi 10.2
    R.v("ust", (165.1, 0, 0), (165.1, 0, 508), "sag", 1)              # boy 508
    R.v("ust", (140, 0, 0), (140, 0, 22), "sag", 2) if False else None
    R.h("yan", (0, 25.4, 0), (22, 25.4, 0), "ust", 1)                 # uc duvar 22
    R.h("yan", (0, 25.4, 0), (12, 25.4, 0), "ust", 2) if False else None
    R.genel(2, 3, 2)
    # kesit (z=254): ic bosluk olculeri (x, y duzlemi)
    R.h("kesit", (-140, 26, 254), (140, 26, 254), "ust", 1)           # ic ust genislik 280
    R.h("kesit", (-100, -91.4, 254), (100, -91.4, 254), "alt", 1)     # ic taban genisligi 200
    R.v("kesit", (-140, 26, 254), (-140, -91.4, 254), "sol", 1)       # ic derinlik 117.4
    R.v("kesit", (0, -101.6, 254), (0, -91.4, 254), "sag", 1)         # taban kalinligi 10.2
    R.v("kesit", (165.1, 25.4, 254), (165.1, 0, 254), "sag", 1)       # flans kalinligi 25.4
    return ["Govde kenar duvari 10 mm, taban 10.2 mm, uc duvarlar 22 mm; flans kalinligi 25.4 mm",
            "Ic boslugun ust acikligi: 280 mm (x), 464 mm (z)"]


# ---------------------------------------------------------------- krank / piston grubu
def crank_shaft(R):
    b = R.bb
    # yan gorunus (z,y): z boyunca ana muylular, pimler, yanaklar
    for i in range(4):
        z0 = i * 145.96
        R.h("yan", (z0, 38.1, 0), (z0 + 27.31, 38.1, 0), "ust", 1)                 # 27.31 muylu uzunlugu
    R.h("yan", (0, 38.1, 0), (145.96, 38.1, 0), "ust", 2)                           # muylu adimi 145.96
    R.h("yan", (-45, 25, 0), (0, 25, 0), "alt", 1)                                   # on mil 45
    R.h("yan", (27.31, -38.1, 0), (47.31, -38.1, 0), "alt", 1)                       # yanak kalinligi 20
    R.h("yan", (47.31, -38.1, 0), (125.96, -38.1, 0), "alt", 2)                      # pim uzunlugu 78.65
    R.cap("on", (0, 0, 0), 38.1, "x", yon=-1, mesafe=14)                              # O76.2 muylu
    R.cap("on", (0, 63.5, 100), 31.75, "x", yon=1, mesafe=8)                          # O63.5 pim
    R.cap("on", (0, 0, -45), 25, "y", yon=1, mesafe=10)                               # O50 on mil
    R.v("on", (0, 0, 0), (0, 63.5, 0), "sag", 1)                                      # kol yaricapi 63.5
    R.genel(2, 2, 3)
    return ["Pim acilari (on gorunusten): 0, 120, 240 derece; kol (cark) yaricapi 63.5 mm, yanak kalinligi 20 mm",
            "Ana muylu O76.2 x 27.31 (4 adet), pim O63.5 x 78.65 (3 adet), on mil O50 x 45"]


def piston_head(R):
    r = 63.5
    R.v("on", (r, -6.35, 0), (r, -15.88, 0), "sag", 1)                          # segman adimi 9.53
    R.v("on", (r, 0, 0), (r, -6.35, 0), "sag", 2)                               # ust bant 6.35
    R.v("on", (-r, 0, 0), (-r, -15, 0), "sol", 2)                               # tepe kalinligi 15 (ic oyuk tabani)
    R.cap("ust", (0, 0, 0), 56, "x", yon=1, mesafe=10)                          # ic oyuk O112
    R.h("yan", (-38.1, -66, 0), (38.1, -66, 0), "alt", 1)                       # pencere 76.2
    R.v("yan", (38.1, -81.28, 0), (38.1, -27.9, 0), "sag", 1)                   # pencere yuksekligi 53.4
    R.genel(1, 1, 1)
    # kesit (x=0): ic bosluk olculeri
    R.v("kesit", (0, 0, -63.5), (0, -15, -63.5), "sol", 1)                      # ust plaka 15
    R.h("kesit", (0, -50, -63.5), (0, -50, -56), "alt", 1)                      # cidar 7.5
    R.v("kesit", (0, -15, 56), (0, -81.28, 56), "sag", 1)                       # ic oyuk derinligi 66.28
    R.h("kesit", (0, -81.28, -56), (0, -81.28, 56), "alt", 1)                   # ic cap 112
    R.h("kesit", (0, -81.28, -38.1), (0, -81.28, 38.1), "alt", 2)               # pim penceresi 76.2
    R.v("kesit", (0, -81.28, 38.1), (0, -27.9, 38.1), "sag", 2)                 # pencere yuksekligi 53.38
    R.h("kesit", (0, -8, 60.68), (0, -8, 63.5), "ust", 1)                       # segman yuvasi derinligi 2.82
    R.v("kesit", (0, -6.35, 63.5), (0, -9.53, 63.5), "sag", 3)                  # yuva genisligi 3.18
    return ["Ust yuzde 3 segman yuvasi: genislik 3.18, derinlik 2.82, adim 9.53; ust bant 6.35",
            "Ic oyuk O112 (et kalinligi 7.5), taban 15 mm kalin; pim yuvasi O25.4 (tepeden 50.8)"]


def piston_rod(R):
    b = R.bb
    R.v("on", (0, 0, 0), (0, 152.4, 0), "sol", 1)                               # merkez mesafesi 152.4
    R.cap("on", (0, 0, 0), 31.75, "x", yon=-1, mesafe=14)                       # O63.5 buyuk uc
    R.cap("on", (0, 152.4, 0), 12.7, "x", yon=1, mesafe=14)                     # O25.4 kucuk uc
    R.cap("on", (0, 152.4, 0), 19.05, "x", yon=-1, mesafe=14)                   # O38.1 dis
    R.h("on", (-55, 12.7, 0), (-38, 12.7, 0), "ust", 1)                         # kulak 17
    R.h("on", (-46.5, 0, 0), (46.5, 0, 0), "alt", 1)                            # civata araligi 93
    R.v("on", (55, 0, 0), (55, 12.7, 0), "sag", 1)                              # kulak yuksekligi 12.7
    R.h("on", (-19.05, 38, 0), (19.05, 38, 0), "alt", 2)                        # govde genisligi 38.1 (alt)
    R.h("on", (-10, 134.4, 0), (10, 134.4, 0), "ust", 1)                        # govde genisligi 20 (ust)
    R.genel(2, 2, 1)
    R.h("yan", (-12.065, 0, 0), (12.065, 0, 0), "alt", 1) if False else None
    return ["Buyuk uc yariccapi 43.29 (O86.58); kulaklarda 2 adet O8 civata deligi (x=+-46.5)",
            "Kalinlik: uclar 24.13 mm, govde (I-kesit) 15 mm"]


def piston_rod_cap(R):
    R.cap("on", (0, 0, 0), 31.75, "x", yon=-1, mesafe=14)                       # O63.5
    R.cap("on", (0, 0, 0), 43.29, "y", yon=-1, mesafe=12) if False else None
    R.h("on", (-46.5, 0, 0), (46.5, 0, 0), "ust", 1)                            # civata araligi 93
    R.h("on", (-55, -12.7, 0), (-38, -12.7, 0), "alt", 1)                       # kulak 17
    R.v("on", (55, 0, 0), (55, -12.7, 0), "sag", 1)                             # kulak 12.7
    R.v("on", (-43.29 + 0, -0.0, 0), (-43.29 + 0, -43.29, 0), "sol", 1) if False else None
    R.v("on", (0, 0, 0), (0, -43.29, 0), "sol", 1)                              # yukseklik 43.29
    R.genel(2, 2, 1)
    return ["Kulaklarda 2 adet O8 civata deligi (x=+-46.5); dis yaricap 43.29, ic yaricap 31.75 (O63.5)",
            "Kalinlik 24.13 mm"]


def piston_pin(R):
    R.h("on", (-34.9, 12.7, 0), (34.9, 12.7, 0), "ust", 1)                      # boy 69.8
    R.v("on", (-34.9, -12.7, 0), (-34.9, 12.7, 0), "sol", 1)                    # O25.4
    R.v("on", (34.9, -6.35, 0), (34.9, 6.35, 0), "sag", 1)                      # O12.7 ic
    R.cap("yan", (0, 0, 0), 12.7, "x", yon=1, mesafe=10)                        # O25.4
    R.cap("yan", (0, 0, 0), 6.35, "y", yon=1, mesafe=10)                        # O12.7
    R.v("kesit", (0, 6.35, 0), (0, 12.7, 0), "sag", 1)                          # cidar 6.35
    return ["Ici bos pim: dis O25.4, ic O12.7, boy 69.8 mm"]


# ---------------------------------------------------------------- mil / yatak / burclar
def cam_shaft(R):
    # mil O19.05 x 466; 12 kam (6 cift): kam genisligi 14, cift ici aralik 56, cift adimi 146.05, ilk cift uctan 62.55
    R.v("on", (-24, 0, 0), (-24, 62.55, 0), "sol", 1)                           # uctan ilk kama 62.55
    R.v("on", (-24, 62.55, 0), (-24, 76.55, 0), "sol", 1)                       # kam genisligi 14
    R.v("on", (-24, 62.55, 0), (-24, 118.55, 0), "sol", 2)                      # cift ici aralik 56
    R.v("on", (-24, 62.55, 0), (-24, 208.6, 0), "sol", 3)                       # cift adimi 146.05
    R.v("on", (24, 0, 0), (24, 466, 0), "sag", 1)                               # toplam boy 466
    R.h("on", (-9.525, 466, 0), (9.525, 466, 0), "ust", 1)                      # mil O19.05
    R.cap("ust", (0, 0, 0), 9.525, "x", yon=1, mesafe=14)                       # O19.05 mil
    R.cap("ust", (0, 0, 0), 17.3, "y", yon=-1, mesafe=14)                       # O34.6 kam tabani
    return ["12 adet kam: taban yaricapi 17.3 (O34.6), burun +9 mm; kam genisligi 14; ciftler 56 aralikli",
            "Kam aciklari: her silindir icin 90 derece fark, silindirler arasi 120 derece. Mil O19.05 x 466"]

def cam_retainer(R):
    R.h("yan", (-28.6, 0, 0), (28.6, 0, 0), "alt", 1)                           # tum genislik
    R.h("yan", (-14, 22.2, 0), (14, 22.2, 0), "ust", 1)                         # ust bolum 28
    R.v("yan", (28.6, 0, 0), (28.6, 12.7, 0), "sag", 1)                         # kanat yuksekligi 12.7
    R.v("yan", (28.6, 12.7, 0), (28.6, 22.2, 0), "sag", 1)                      # 9.5 ust bolum
    R.cap("yan", (0, 0, 0), 9.525, "x", yon=1, mesafe=10)                       # O19.05 yuva
    R.h("on", (-9.525, 0, 0), (9.525, 22.2, 0), "ust", 1) if False else None
    R.h("on", (-9.525, 22.2, 0), (9.525, 22.2, 0), "ust", 1)                    # kalinlik 19.05
    R.cap("ust", (0, 0, 19.05), 3.2, "x", yon=1, mesafe=8)                      # O6.4 civata
    R.v("ust", (9.525, 0, -19.05), (9.525, 0, 19.05), "sag", 1) if False else None
    R.v("ust", (-9.525, 0, 19.05), (-9.525, 0, -19.05), "sol", 1)               # civata araligi 38.1
    R.genel(2, 2, 2, yan=False)
    return ["Alt yuva O19.05; 2 adet O6.4 civata deligi z=+-19.05 (aralik 38.1)"]


def cam_bushing(R):
    R.h("on", (0, 12.7, 0), (19.05, 12.7, 0), "ust", 1)                         # boy 19.05
    R.v("on", (0, -12.7, 0), (0, 12.7, 0), "sol", 1)                            # O25.4
    R.v("on", (19.05, -9.525, 0), (19.05, 9.525, 0), "sag", 1)                  # O19.05
    R.cap("yan", (0, 0, 0), 12.7, "x", yon=1, mesafe=10)
    R.cap("yan", (0, 0, 0), 9.525, "y", yon=1, mesafe=10)
    R.v("kesit", (9.5, 9.525, 0), (9.5, 12.7, 0), "sag", 1)                  # cidar 3.175
    return ["Burc: dis O25.4, ic O19.05, boy 19.05 mm"]


def crank_bushing(R):
    R.h("on", (0, 42.1, 0), (19.05, 42.1, 0), "ust", 1)                         # boy 19.05
    R.v("on", (0, -42.1, 0), (0, 42.1, 0), "sol", 1)                            # O84.2
    R.v("on", (19.05, -38.1, 0), (19.05, 38.1, 0), "sag", 1)                    # O76.2
    R.cap("yan", (0, 0, 0), 42.1, "x", yon=1, mesafe=10)
    R.cap("yan", (0, 0, 0), 38.1, "y", yon=1, mesafe=10)
    R.v("kesit", (9.5, 38.1, 0), (9.5, 42.1, 0), "sag", 1)                   # cidar 4
    return ["Burc: dis O84.2, ic O76.2, boy 19.05 mm"]


# ---------------------------------------------------------------- supap grubu
def valve(R):
    R.v("on", (30, 0, 0), (30, 115, 0), "sag", 2)                               # toplam 115
    R.v("on", (30, 0, 0), (30, 2.5, 0), "sag", 1) if False else None
    R.v("on", (26.7, 0, 0), (26.7, 2.5, 0), "sag", 1)                           # kafa kalinligi 2.5
    R.v("on", (8, 2.5, 0), (8, 14, 0), "sag", 1) if False else None
    R.v("on", (-26.7, 0, 0), (-26.7, 22, 0), "sol", 1)                          # kafa + koni 22
    R.v("on", (-4.76, 108, 0), (-4.76, 111, 0), "sol", 1)                       # oluk 3
    R.v("on", (-4.76, 111, 0), (-4.76, 115, 0), "sol", 2)                       # uc 4
    R.h("on", (-26.7, 0, 0), (26.7, 0, 0), "alt", 1)                            # O53.4 kafa
    R.h("on", (-4.76, 60, 0), (4.76, 60, 0), "alt", 2) if False else None
    R.cap("on", (0, 60, 0), 4.76, "x", yon=1, mesafe=14)                        # O9.52 sap
    R.cap("on", (0, 109.5, 0), 3.8, "x", yon=-1, mesafe=14)                     # O7.6 oluk
    return ["Supap: kafa O53.4 x 2.5, sap O9.52, koni 2.5 - 22 mm arasi, oluk O7.6 (y=108..111), toplam boy 115 mm"]


def rocker_spring(R):
    R.v("on", (30, 0, 0), (30, 30.3, 0), "sag", 1)                              # toplam 30.3
    R.h("on", (-13.35, 0, 0), (13.35, 0, 0), "alt", 1)                          # O26.7 uc disk
    R.h("on", (-12.4, 6.725, 0), (12.4, 6.725, 0), "alt", 2)                    # ortalama cap 24.8
    R.v("on", (-13.35, 2.725, 0), (-13.35, 7.725, 0), "sol", 1)                 # adim 5.0
    R.v("on", (-13.35, 0, 0), (-13.35, 1.5, 0), "sol", 2)                       # disk kalinligi 1.5
    R.cap("on", (12.4, 6.725, 0), 1.225, "y", yon=1, mesafe=10) if False else None
    return ["Yay: tel O2.45, ortalama sarim capi 24.8, adim 5.0, 6 sarim, uclarda O26.7 x 1.5 disk, toplam boy 30.3"]


def rocker_arm(R):
    R.h("yan", (-22.23, 11.9, 0), (28.58, 11.9, 0), "ust", 2) if False else None
    R.h("yan", (0, 11.9, 0), (28.58, 11.9, 0), "ust", 1)                        # 28.58 sol kol
    R.h("yan", (0, 11.9, 0), (-22.23, 11.9, 0), "ust", 1)                       # 22.23 sag kol
    R.v("yan", (-22.23, -2, 0), (-22.23, 5, 0), "sag", 1) if False else None
    R.v("yan", (28.58, 0, 0), (28.58, 5, 0), "sag", 1)                          # uc yuksekligi 5
    R.v("yan", (-22.23, -11.9, 0), (-22.23, 11.9, 0), "sol", 1)                 # toplam yukseklik 23.8
    R.cap("yan", (0, 0, 0), 4.765, "x", yon=-1, mesafe=12) if False else None
    R.cap("yan", (0, 0, 0), 4.765, "y", yon=1, mesafe=10)                       # O9.53 pivot
    R.cap("yan", (24, 2.5, 0), 1.59, "y", yon=1, mesafe=10)                     # O3.18
    R.h("on", (-5, 11.9, 0), (5, 11.9, 0), "ust", 1)                            # kalinlik 10
    R.genel(2, 2, 2, yan=False) if False else None
    return ["Kol: pivot deligi O9.53, sol kol ucunda O3.18 delik (pivot'a 24 mm), kalinlik 10 mm"]


def rocker_roll(R):
    R.h("on", (-3, 7.14, 0), (3, 7.14, 0), "ust", 1)                            # genislik 6
    R.v("on", (-3, -7.14, 0), (-3, 7.14, 0), "sol", 1)                          # O14.28
    R.v("on", (3, -1.59, 0), (3, 1.59, 0), "sag", 1)                            # O3.18 ic
    R.cap("yan", (0, 0, 0), 7.14, "x", yon=1, mesafe=10)
    R.cap("yan", (0, 0, 0), 1.59, "y", yon=1, mesafe=10)
    R.v("kesit", (0, 1.59, 0), (0, 7.14, 0), "sag", 1)                          # cidar 5.55
    return ["Makara: dis O14.28 x 10, ic O3.18, kenar pahlari 0.76 x 45 derece"]


def rocker_pin(R):
    R.h("on", (-9.5, 4.765, 0), (9.5, 4.765, 0), "ust", 1)                      # boy 19
    R.v("on", (-9.5, -4.765, 0), (-9.5, 4.765, 0), "sol", 1)                    # O9.53
    R.cap("yan", (0, 0, 0), 4.765, "x", yon=1, mesafe=10)
    return ["Pim: O9.53 x 19, uc pahlari 0.7 x 45 derece"]


# ---------------------------------------------------------------- manifold / filtre / turbo
def intake_manifold(R):
    b = R.bb
    R.h("on", (-45, 371.5, 0), (45, 371.5, 0), "ust", 1) if False else None
    R.v("yan", (40, 300, 0), (40, 371.5, 0), "sag", 1) if False else None
    R.v("on", (45, 300, 0), (45, 371.5, 0), "sag", 1)                           # plenum yuksekligi 71.5
    R.h("on", (-45, 300, 0), (45, 300, 0), "alt", 1)                            # plenum genisligi 90
    R.cap("on", (-22, 336, 0), 18, "x", yon=-1, mesafe=12)                      # O36 giris
    R.h("on", (-22, 372, 0), (22, 372, 0), "ust", 1) if False else None
    R.h("ust", (-22, 0, 0), (22, 0, 0), "alt", 1) if False else None
    R.v("ust", (45, 0, 40), (45, 0, 468), "sag", 1)                             # plenum boyu 428
    R.v("ust", (45, 0, 0), (45, 0, 40), "sag", 2)                               # giris boyu 40
    R.genel(2, 2, 3, yan=False)
    return ["Plenum 90 x 71.5 x 428, iki giris O36 (merkez araligi 44, uzunluk 40)",
            "Her silindir icin 38.1 genisliginde kanal (toplam 6 adet), kanallar sira ekseni +-45 derece"]


def exhaust(R, sg):
    X = lambda v: sg * v
    zc = ZC
    R.v("on", (X(9.52), -31.75, 0), (X(9.52), 31.75, 0), "sag" if sg > 0 else "sol", 1)   # flans 63.5
    R.h("on", (0, 31.75, 0), (X(9.52), 31.75, 0), "ust", 1)                      # flans kalinligi 9.52
    R.cap("on", (X(75), -60, 0), 23.8, "x", yon=sg, mesafe=12)                   # O47.6 boru
    R.cap("on", (X(75), -60, 0), 19, "y", yon=-1, mesafe=12)                     # O38 ic
    R.v("ust", (X(0), 0, 60.3), (X(0), 0, 447.65), "sol" if sg > 0 else "sag", 1)   # flans boyu 387.35
    R.v("ust", (X(0), 0, 20), (X(0), 0, 508), "sol" if sg > 0 else "sag", 2)         # boru boyu 488
    for i in range(2):
        R.v("ust", (X(9.52), 0, zc[i]), (X(9.52), 0, zc[i + 1]), "sag" if sg > 0 else "sol", 1)   # 146.05
    R.genel(2, 2, 3, yan=False)
    return ["Flansta 3 adet 31.8 x 31.8 kare port (aralik 146.05); boru ucu: dis O47.6, ic O38",
            "Kanallar: 38.1 genislik, flans yuzeyinden boruya acili"]


def air_filter(R):
    R.cap("on", (0, 0, 0), 50, "x", yon=1, mesafe=12)                            # O100
    R.cap("on", (0, 0, 0), 41, "y", yon=-1, mesafe=12)                           # ic O82 (pili)
    R.cap("on", (0, 0, 101.5), 33, "x", yon=-1, mesafe=12) if False else None
    R.h("yan", (0, 50, 0), (101.5, 50, 0), "ust", 1)                             # pili boyu 101.5
    R.h("yan", (-10, 50, 0), (0, 50, 0), "ust", 1)                               # kapak 10
    R.h("yan", (101.5, 33, 0), (131.5, 33, 0), "ust", 2)                         # boyun 30
    R.v("yan", (131.5, -33, 0), (131.5, 33, 0), "sag", 1)                        # boyun O66
    R.v("yan", (131.5, -26.7, 0), (131.5, 26.7, 0), "sag", 2) if False else None
    R.genel(2, 2, 3, yan=False) if False else None
    return ["Pileli govde: 20 pili, ucgen kesit, 6 derece konik (dis O100, ic O82), et kalinligi 1 mm",
            "Kapak O100 x 10; boyun O66 / O53.4 x 30"]


def air_turbo(R):
    R.h("yan", (0, 70, 0), (55, 70, 0), "ust", 1)                                # govde 55
    R.h("yan", (55, 25, 0), (90, 25, 0), "ust", 1)                               # mil 35
    R.h("yan", (90, 60, 0), (135, 60, 0), "ust", 1)                              # kafa 45
    R.h("yan", (135, 33, 0), (165, 33, 0), "ust", 2)                             # cikis 30
    R.h("yan", (-20, 19, 0), (0, 19, 0), "ust", 1)                               # on uzanti 20
    R.v("yan", (0, -70, 0), (0, 70, 0), "sol", 1)                                # O140
    R.v("yan", (90, -60, 0), (90, 60, 0), "sag", 1)                              # O120
    R.v("yan", (60, -25, 0), (60, 25, 0), "sag", 1) if False else None
    R.cap("on", (0, 0, 0), 70, "x", yon=1, mesafe=14)
    R.cap("on", (0, 0, 135), 33, "y", yon=1, mesafe=12) if False else None
    R.h("on", (40, 43.27, 0), (103.5, 43.27, 0), "ust", 1)                       # cikis kutusu 63.5
    R.v("on", (103.5, 10, 0), (103.5, 43.27, 0), "sag", 1)                       # cikis yuksekligi 33.27
    # kesit (x=0): z, y duzlemi
    R.v("kesit", (0, 26, -12), (0, 32, -12), "sol", 1)                           # on halka cidari 6
    R.h("kesit", (0, -36, -30), (0, -36, 0), "alt", 1)                           # delik derinligi 30
    return ["Turbo: govde O140 x 55, mil O50 x 35, kafa O120 x 45, cikis halkasi O66/O53.4 x 30, on uzanti O38 x 20",
            "Cikis kutusu 63.5 x 33.27 x 55 (x=40..103.5, y=10..43.27)"]


def pulley_small(R):
    R.h("yan", (-40, 30.1, 0), (0.6, 30.1, 0), "ust", 1)                         # toplam 40.6
    R.h("yan", (-27, 24.6, 0), (0, 24.6, 0), "ust", 2) if False else None
    R.h("yan", (-40, -19, 0), (-27, -19, 0), "alt", 1)                           # gobek 13
    R.h("yan", (-27, -30.1, 0), (-25.4, -30.1, 0), "alt", 2) if False else None
    R.v("yan", (0.6, -30.1, 0), (0.6, 30.1, 0), "sag", 1)                        # O60.2
    R.v("yan", (-33, -19, 0), (-33, 19, 0), "sol", 1)                            # gobek O38
    R.cap("on", (0, 0, 0), 6, "x", yon=1, mesafe=12)                             # O12 delik
    R.cap("on", (0, 0, 0), 27.2, "y", yon=1, mesafe=12)                          # O54.4 disli tepe
    # kesit (x=0): z, y duzlemi
    R.v("kesit", (0, 6, -33), (0, 19, -33), "sol", 1)                            # gobek cidari 13
    R.h("kesit", (0, -25, -40), (0, -25, -27), "alt", 1)                         # gobek boyu 13
    R.h("kesit", (0, -35, -27), (0, -35, 0.6), "alt", 2)                         # disli genisligi 27.6
    return ["Disli kasnak: 20 dis, tepe O54.4, dip O49.2, flans O60.2, gobek O38 x 13, ic delik O12, toplam genislik 40.6"]


def pulley_big(R):
    R.h("yan", (-45, 83, 0), (0.6, 83, 0), "ust", 1)                             # toplam 45.6
    R.h("yan", (-15, 62, 0), (0, 62, 0), "alt", 1) if False else None
    R.h("yan", (-45, -62, 0), (-15, -62, 0), "alt", 1)                           # gobek 30
    R.v("yan", (0.6, -83, 0), (0.6, 83, 0), "sag", 1)                            # O166
    R.v("yan", (-30, -62, 0), (-30, 62, 0), "sol", 1)                            # gobek O124
    R.cap("on", (0, 0, 0), 50, "x", yon=1, mesafe=14)                            # O100 delik
    R.cap("on", (0, 0, 0), 81, "y", yon=1, mesafe=12)                            # O162 disli dip
    # kesit (x=0): z, y duzlemi
    R.v("kesit", (0, 50, -30), (0, 62, -30), "sol", 1)                           # gobek cidari 12
    R.v("kesit", (0, 50, -5), (0, 83, -5), "sag", 1)                             # disli halka yuksekligi 33
    R.h("kesit", (0, -70, -45), (0, -70, -15), "alt", 1)                         # gobek boyu 30
    R.h("kesit", (0, -90, -15), (0, -90, 0.6), "alt", 2)                         # disli kalinligi 15.6
    return ["Disli kasnak: 60 dis, dis O166, ic delik O100, gobek O124 x 30, toplam genislik 45.6"]


def front_cover(R):
    R.h("on", (-239.4, 305.2, 0), (239.4, 305.2, 0), "ust", 1)                   # 478.8
    R.v("on", (-239.4, -10.5, 0), (-239.4, 305.2, 0), "sol", 1)                  # 315.7
    R.h("on", (-165, -10.5, 0), (165, -10.5, 0), "alt", 1)                       # alt genislik 330
    R.v("on", (110, -10.5, 0), (110, 150, 0), "sag", 1)                          # delik yuksekligi 160.5
    R.h("on", (-110, 150, 0), (110, 150, 0), "alt", 2)                           # delik araligi 220
    R.cap("on", (110, 150, 0), 15, "x", yon=1, mesafe=14)                        # O30
    R.cap("on", (0, -10.5, 0), 105, "x", yon=-1, mesafe=12) if False else None
    R.v("on", (-30, -10.5, 0), (-30, 205, 0), "sol", 2) if False else None
    R.v("on", (0, -10.5, 0), (0, 205, 0), "sag", 2) if False else None
    R.h("yan", (0, 305.2, 0), (10, 305.2, 0), "ust", 1)                          # plaka 10
    R.h("yan", (0, 310, 0), (52.1, 310, 0), "ust", 2) if False else None
    R.h("yan", (0, -10.5, 0), (52.1, -10.5, 0), "alt", 1)                        # flans derinligi 52.1
    return ["Plaka kalinligi 10 mm; ust kenar flansi 6 mm kalin, 52.1 mm derin",
            "Delik gobekleri: dis O52, ic O30, yukseklik 20 mm; alt yuvanin yaricapi 105 (O210), merkezi alt kenarda"]


# 4. eleman: kesit duzlemi ("on", x_mm) veya ("ust", z_mm); sadece ici bos parcalarda
KESIT = {
    "EngineBlock": ("on", 0.0), "CylinderHead": ("on", 0.0), "Valves Cover": ("on", 0.0),
    "OilPan": ("ust", 254.0),
    "Piston parcalari\\Piston Head": ("on", 0.0), "Piston parcalari\\Piston Pin": ("ust", 0.0),
    "CamShaft Bushing": ("ust", 0.0), "CrankShaft Bushing": ("ust", 0.0),
    "rockerarm parcalari\\Rocker arm roll": ("ust", 0.0),
    "PartR3": ("on", 0.0), "PartR11": ("on", 0.0), "AirTurbo": ("on", 0.0),
}

SPEC = {
    "EngineBlock": (engine_block, ("on", "ust", "yan"), "Dokum demir"),
    "CylinderHead": (cylinder_head, ("on", "ust", "yan"), "Aluminyum"),
    "Valves Cover": (valves_cover, ("on", "ust", "yan"), "Aluminyum"),
    "OilPan": (oil_pan, ("on", "ust", "yan"), "Sac / aluminyum"),
    "Crankshaft": (crank_shaft, ("on", "yan"), "Dovme celik"),
    "Piston parcalari\\Piston Head": (piston_head, ("on", "ust", "yan"), "Aluminyum alasim"),
    "Piston parcalari\\Piston Rod": (piston_rod, ("on", "yan"), "Dovme celik"),
    "Piston parcalari\\Piston Rod Cap": (piston_rod_cap, ("on", "yan"), "Dovme celik"),
    "Piston parcalari\\Piston Pin": (piston_pin, ("on", "ust", "yan"), "Sertlestirilmis celik"),
    "CamShaft": (cam_shaft, ("on", "ust"), "Dovme celik"),
    "CamShaft Retainer": (cam_retainer, ("yan", "on", "ust"), "Celik"),
    "CamShaft Bushing": (cam_bushing, ("on", "ust", "yan"), "Bronz"),
    "CrankShaft Bushing": (crank_bushing, ("on", "ust", "yan"), "Bronz"),
    "valve": (valve, ("on",), "Paslanmaz celik"),
    "rockerarm parcalari\\Rocker arm": (rocker_arm, ("yan", "on"), "Celik"),
    "rockerarm parcalari\\Rocker arm roll": (rocker_roll, ("on", "ust", "yan"), "Celik"),
    "rockerarm parcalari\\rocker arm pin1": (rocker_pin, ("on", "yan"), "Celik"),
    "RockerArm spring": (rocker_spring, ("on",), "Yay celigi"),
    "IntakeManifold2": (intake_manifold, ("on", "ust"), "Aluminyum"),
    "vvexhaust1": (lambda R: exhaust(R, 1), ("on", "ust"), "Celik"),
    "exhaust manifold2": (lambda R: exhaust(R, -1), ("on", "ust"), "Celik"),
    "AirFilter": (air_filter, ("on", "yan"), "Kagit / metal"),
    "AirTurbo": (air_turbo, ("on", "yan"), "Aluminyum"),
    "PartR11": (pulley_small, ("on", "yan"), "Celik"),
    "PartR3": (pulley_big, ("on", "ust", "yan"), "Celik"),
    "FrontCover": (front_cover, ("on", "yan"), "Sac"),
}




