from swlib import connect, Part, bbox

sw = connect()
p = Part(sw)

# 1) on duzlem: x=50,y=20 r=10 daire, 30 derinlik -> z yonu?
p.sketch("front"); p.circle(50, 20, 10); p.end_sketch()
b1 = p.extrude(30)
print("front extrude:", bbox(b1))

# 2) ofset duzlem z=100
p.plane("z100", "front", 100)
p.sketch("z100"); p.circle(0, 0, 5); p.end_sketch()
b2 = p.extrude(10, reverse=True)
print("z100 reverse:", bbox(b2))

# 3) ust duzlem: x=30,y=-40 daire
p.sketch("top"); p.circle(30, -40, 8); p.end_sketch()
b3 = p.extrude(20)
print("top:", bbox(b3))

# 4) sag duzlem: x=30,y=-40 daire
p.sketch("right"); p.circle(30, -40, 8); p.end_sketch()
b4 = p.extrude(20)
print("right:", bbox(b4))

# 5) revolve: front duzlemde dikdortgen, y eksenine paralel centerline x=0
p.sketch("front"); p.centerline(-100, 0, -100, 50); p.rect(-100, 0, -80, 30); p.end_sketch()
b5 = p.revolve()
print("revolve:", bbox(b5))

p.style(b1, "Test-Altin", (0.85, 0.65, 0.1))
p.style(b5, "Test-Seffaf", (0.6, 0.6, 0.6), transp=0.6)
print("isimler:", [b.Name for b in p._bodies()])
p.view()
