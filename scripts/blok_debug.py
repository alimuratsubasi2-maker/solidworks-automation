import traceback
import swlib
from swlib import connect, Part
import v6_yeni_parcalar as V

orig = swlib.Part.cut


def cut(self, *a, **k):
    n0 = sum(b.GetFaceCount() for b in self._bodies())
    orig(self, *a, **k)
    n1 = sum(b.GetFaceCount() for b in self._bodies())
    fr = [f for f in traceback.extract_stack() if "v6_yeni_parcalar" in f.filename][-1]
    print(f"cut satir {fr.lineno}: yuz {n0}->{n1}  args={a} {k}", flush=True)


swlib.Part.cut = cut
sw = connect()
sw.CloseAllDocuments(True)
p = Part(sw)
p.iso()
V.engine_block(p)
sw.CloseAllDocuments(True)
