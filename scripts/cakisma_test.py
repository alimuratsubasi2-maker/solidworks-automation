"""Engine Assembly'de bilesenler arasi cakisma (interference) kontrolu."""
import os
from swlib import connect, T, MM
from v6_yeni_parcalar import HEDEF

sw = connect()
sw.CloseAllDocuments(True)
r = sw.OpenDoc6(os.path.join(HEDEF, "Engine Assembly.SLDASM"), 2, 1, "", 0, 0)
m = T(r[0] if isinstance(r, tuple) else r, "IModelDoc2")
a = T(m, "IAssemblyDoc")
m.ForceRebuild3(False)
ext = T(m.Extension, "IModelDocExtension")
idm = T(a.InterferenceDetectionManager, "IInterferenceDetectionMgr")
idm.TreatCoincidenceAsInterference = False
idm.TreatSubAssembliesAsComponents = False
idm.IncludeMultibodyPartInterferences = False
idm.MakeInterferingPartsTransparent = False
idm.CreateFastenersFolder = False
idm.IgnoreHiddenBodies = True
ints = idm.GetInterferences()
print("cakisma sayisi:", 0 if not ints else len(ints))
from collections import Counter
sayac = Counter()
toplam = Counter()
for i in (ints or []):
    it = T(i, "IInterference")
    comps = it.Components
    ad = tuple(sorted(T(c, "IComponent2").Name2.rsplit("-", 1)[0].split("/")[-1] for c in comps))
    sayac[ad] += 1
    toplam[ad] += it.Volume * 1e6                # m3 -> cm3
print("\nozet (parca cifti: adet, toplam cakisma hacmi cm3), buyukten kucuge:")
for k, v in sorted(toplam.items(), key=lambda kv: -kv[1])[:22]:
    print(f"  {str(k):62s} adet={sayac[k]:3d}  {v:10.2f} cm3")
idm.Done()
sw.CloseAllDocuments(True)
