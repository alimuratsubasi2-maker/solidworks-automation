"""SLDDRW'leri acip kontrol icin PDF'e cevirir (scratchpad'e; proje klasorune PDF yazmaz) ve 4'lu sayfalar yapar."""
import glob
import os
import sys
import fitz
from PIL import Image
from swlib import connect, T
from v6_yeni_parcalar import HEDEF

SP = sys.argv[1]
os.makedirs(SP, exist_ok=True)
sw = connect()
sw.CloseAllDocuments(True)
adlar = []
for f in sorted(glob.glob(os.path.join(HEDEF, "Teknik Resimler", "*.SLDDRW"))):
    ad = os.path.basename(f)[:-7]
    r = sw.OpenDoc6(f, 3, 1, "", 0, 0)
    m = T(r[0] if isinstance(r, tuple) else r, "IModelDoc2")
    m.SaveAs3(os.path.join(SP, ad + ".pdf"), 0, 1)
    sw.CloseAllDocuments(True)
    fitz.open(os.path.join(SP, ad + ".pdf"))[0].get_pixmap(dpi=105).save(os.path.join(SP, ad + ".png"))
    adlar.append(ad)
# tek tek kontrol: her resim kendi dosyasinda (ad.png); ayrica 28'i icin liste
print(len(adlar), adlar)
sys.exit(0)
print(len(adlar), adlar)
