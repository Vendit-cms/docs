#!/usr/bin/env python3
"""이미지 여러 장을 한 장으로 붙인다. 원본이 뭘 담고 있는지 싸게 확인할 때 쓴다.

    python3 scripts/contact_sheet.py out.png 3 img1.png img2.png ...
"""
import sys, os
from PIL import Image, ImageDraw

out, cols = sys.argv[1], int(sys.argv[2])
paths = sys.argv[3:]
CW, CH, LABEL = 620, 420, 22
rows = (len(paths) + cols - 1) // cols
sheet = Image.new("RGB", (cols * CW, rows * (CH + LABEL)), "white")
d = ImageDraw.Draw(sheet)
for i, p in enumerate(paths):
    x, y = (i % cols) * CW, (i // cols) * (CH + LABEL)
    try:
        im = Image.open(p).convert("RGB")
        im.thumbnail((CW - 8, CH - 8))
        sheet.paste(im, (x + 4, y + LABEL + 4))
    except Exception as e:
        d.text((x + 6, y + LABEL + 20), f"ERR {e}", fill="red")
    d.text((x + 6, y + 6), os.path.basename(p)[:70], fill="black")
sheet.save(out)
print(out, sheet.size)
