"""Egitim videosundan kare cikarma.
  python video_kare.py tablo <video> <cikti_klasoru> [aralik_sn=8] [sutun=3]
      -> aralikli kareler, zaman damgali 3x3 tablolar (tablo_01.png ...)
  python video_kare.py kare <video> <saniye> <cikti.png> [x0 y0 x1 y1]
      -> tek kare tam cozunurluk (istege bagli kirpma)"""
import glob
import os
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont


def sure(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                          "default=nw=1:nk=1", video], capture_output=True, text=True).stdout
    return float(out.strip())


def tablo(video, klasor, aralik=8, sutun=3):
    os.makedirs(klasor, exist_ok=True)
    for f in glob.glob(os.path.join(klasor, "k_*.jpg")):
        os.remove(f)
    subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf", f"fps=1/{aralik}",
                    "-q:v", "3", os.path.join(klasor, "k_%04d.jpg")], check=True)
    kareler = sorted(glob.glob(os.path.join(klasor, "k_*.jpg")))
    font = ImageFont.truetype("arial.ttf", 22)
    W = 640
    per = sutun * sutun
    n = 0
    for s in range(0, len(kareler), per):
        grup = kareler[s:s + per]
        ims = []
        for k, f in enumerate(grup):
            im = Image.open(f).convert("RGB")
            im = im.resize((W, int(W * im.height / im.width)))
            ims.append((s + k, im))
        H = ims[0][1].height
        sh = Image.new("RGB", (sutun * W, ((len(ims) + sutun - 1) // sutun) * H), "white")
        d = ImageDraw.Draw(sh)
        for k, (idx, im) in enumerate(ims):
            x, y = (k % sutun) * W, (k // sutun) * H
            sh.paste(im, (x, y))
            t = idx * aralik + aralik / 2
            d.rectangle([x, y, x + 110, y + 28], fill="yellow")
            d.text((x + 5, y + 2), f"{int(t // 60)}:{int(t % 60):02d}", fill="black", font=font)
        n += 1
        sh.save(os.path.join(klasor, f"tablo_{n:02d}.png"))
    print(f"{len(kareler)} kare, {n} tablo, sure {sure(video):.0f}s -> {klasor}")


def kare(video, t, out, crop=None):
    tmp = out + ".tmp.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", video, "-frames:v", "1", tmp], check=True)
    im = Image.open(tmp)
    if crop:
        im = im.crop(crop)
        im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    im.save(out)
    os.remove(tmp)
    print(out, im.size)


if __name__ == "__main__":
    if sys.argv[1] == "tablo":
        tablo(sys.argv[2], sys.argv[3], float(sys.argv[4]) if len(sys.argv) > 4 else 8,
              int(sys.argv[5]) if len(sys.argv) > 5 else 3)
    else:
        crop = tuple(int(v) for v in sys.argv[5:9]) if len(sys.argv) > 8 else None
        kare(sys.argv[2], float(sys.argv[3]), sys.argv[4], crop)
