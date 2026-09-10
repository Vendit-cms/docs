#!/usr/bin/env python3
"""한국어 스크린샷 위에 영어 텍스트만 덮어쓴다. UI 는 원본 픽셀 그대로 둔다.

제품에서 사라진 화면이라 다시 찍을 수 없는 이미지에만 쓴다. 지금은 판매관리
이해하기의 범례 두 장(요금 조절 / 판매 완료·재고)뿐이다. 찍을 수 있으면 찍어라.

동작
    1. 지정한 영역에서 잉크(어두운 픽셀)의 실제 경계를 찾는다.
    2. 그 영역 바로 위 배경색을 떠서 글자만 지운다. 칸·테두리·칩 색은 건드리지 않는다.
    3. 같은 베이스라인, 같은 왼쪽 좌표에 Pretendard 로 영어를 그린다.
       크기는 원문 글자 높이에 맞춘다(한글 글자 높이 ~= 라틴 캡 높이).

    python3 scripts/overlay_text.py spec.json
"""
import json
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONTS = {
    "regular": "/Users/vendit/Library/Fonts/Pretendard-Regular.otf",
    "medium": "/Users/vendit/Library/Fonts/Pretendard-Medium.otf",
    "semibold": "/Users/vendit/Library/Fonts/Pretendard-SemiBold.otf",
    "bold": "/Users/vendit/Library/Fonts/Pretendard-Bold.otf",
}


def ink_box(gray, box, thresh=150):
    """box=(x1,y1,x2,y2) 안에서 실제 글자가 차지한 경계를 돌려준다."""
    x1, y1, x2, y2 = box
    sub = gray[y1:y2, x1:x2] < thresh
    if not sub.any():
        return None
    ys = np.where(sub.any(axis=1))[0]
    xs = np.where(sub.any(axis=0))[0]
    return (x1 + xs[0], y1 + ys[0], x1 + xs[-1] + 1, y1 + ys[-1] + 1)


def run(spec):
    src = spec["src"]
    im = Image.open(src).convert("RGB")
    gray = np.array(im.convert("L"))
    d = ImageDraw.Draw(im)

    for item in spec["items"]:
        box = tuple(item["box"])
        ink = ink_box(gray, box)
        if ink is None:
            print(f"  건너뜀(잉크 없음) {item['text'][:24]}")
            continue
        ix1, iy1, ix2, iy2 = ink
        # 배경색은 잉크 바로 위 6px 띠의 최빈값에서 뜬다.
        strip = np.array(im)[max(0, iy1 - 14):max(1, iy1 - 4), ix1:ix2].reshape(-1, 3)
        bg = tuple(int(v) for v in np.median(strip, axis=0))
        pad = item.get("pad", 6)
        d.rectangle([ix1 - pad, iy1 - pad, ix2 + pad, iy2 + pad], fill=bg)

        target_h = iy2 - iy1
        size = int(target_h / 0.72)
        font = ImageFont.truetype(FONTS[item.get("weight", "regular")], size)
        # 라틴 캡 높이를 원문 글자 높이에 맞춰 한 번 보정한다.
        probe = font.getbbox("Hxdp")
        cap = probe[3] - probe[1]
        if cap:
            size = max(8, int(size * target_h / cap))
            font = ImageFont.truetype(FONTS[item.get("weight", "regular")], size)
        # segments 가 있으면 한 줄 안에서 굵기가 바뀌는 문장으로 이어 그린다.
        # 용어와 설명을 따로 그리면 영어가 한국어보다 길어져 서로 겹친다.
        segs = item.get("segments") or [{"text": item["text"],
                                         "weight": item.get("weight", "regular"),
                                         "color": item.get("color", [10, 12, 19])}]
        gap = item.get("gap", int(size * 0.5))
        if item.get("align") == "center":
            total = 0
            for sg in segs:
                f = ImageFont.truetype(FONTS[sg.get("weight", "regular")], size)
                total += d.textlength(sg["text"], font=f)
            total += gap * (len(segs) - 1)
            x = (ix1 + ix2) / 2 - total / 2
        else:
            x = ix1
        for k, sg in enumerate(segs):
            f = ImageFont.truetype(FONTS[sg.get("weight", "regular")], size)
            col = tuple(sg.get("color", [10, 12, 19]))
            d.text((x, iy2), sg["text"], font=f, fill=col, anchor="ls")
            w = d.textlength(sg["text"], font=f)
            if sg.get("underline"):
                off = max(2, size // 12)
                d.rectangle([x, iy2 + off, x + w, iy2 + off + max(2, size // 22)], fill=col)
            x += w + (gap if k < len(segs) - 1 else 0)
        label = " ".join(sg["text"] for sg in segs)
        print(f"  ok  {label[:44]:46} size={size} box={ink}")

    im.save(spec["dst"])
    print(f"저장 {spec['dst']}  {im.size}")


def main():
    for spec in json.load(open(sys.argv[1], encoding="utf-8")):
        print(spec["dst"])
        run(spec)


if __name__ == "__main__":
    main()
