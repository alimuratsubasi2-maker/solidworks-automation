from swlib import connect
from asmlib import Asm, box
from parcalar_ciz import HEDEF

sw = connect()
a = Asm(sw, HEDEF)
c1 = a.add("engine valve.SLDPRT")                                   # yerinde: Y boyunca 0..62
c2 = a.add("engine valve.SLDPRT", origin=(100, 0, 0), x=(0, 1, 0), y=(1, 0, 0))  # Y -> +X
print("yerinde :", box(c1))
print("Y->X +100:", box(c2))
