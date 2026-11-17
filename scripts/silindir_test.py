import swlib
from swlib import connect, Part
import v6_yeni_parcalar as V

orig = swlib.Part.revolve


def rev(self, *a, **k):
    n0 = sum(b.GetFaceCount() for b in self._bodies())
    r = orig(self, *a, **k)
    n1 = sum(b.GetFaceCount() for b in self._bodies())
    print(f"revolve cut={k.get('cut')}: yuz {n0}->{n1}", flush=True)
    return r


swlib.Part.revolve = rev
sw = connect()
sw.CloseAllDocuments(True)
p = Part(sw)
p.iso()
V.engine_block(p)
print("toplam yuz:", sum(b.GetFaceCount() for b in p._bodies()))
sw.CloseAllDocuments(True)
