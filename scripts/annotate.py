#!/usr/bin/env python3
"""캡처에 보라 강조 상자와 말풍선을 얹는다.

릴리즈노트 이미지는 한국어 말풍선을 달고 나갔다. 영어판으로 바꾸려면 같은 표시를
영어로 다시 그려야 한다. 원본 스타일을 그대로 맞췄다.
보라 테두리 #6D28D9, 검정 말풍선에 흰 글씨, 상자 쪽을 가리키는 꼬리.

    from annotate import annotate
    annotate("shot.png", "out.png",
             box=[652,1136,2092,1216],
             text="Search finds a property fast.",
             side="right")

좌표는 이미지 픽셀이다. CSS 픽셀이 아니다. dpr 3 으로 찍었으면 CSS 값의 3배다.
"""
import os

from PIL import Image, ImageDraw, ImageFont

PURPLE = (109, 40, 217)
BUBBLE = (23, 23, 23)
TEXT = (255, 255, 255)
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def _font(size):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()


def annotate(src, dst, box=None, text=None, side="auto", scale=None,
             pad=28, gap=34, radius=18, width=None, font_size=None,
             inset=-8, showbox=True):
    """box 에 보라 상자를, 그 옆에 text 말풍선을 그린다.

    side 는 말풍선이 붙는 쪽이다. right·left 는 좌우, below·above 는 위아래다.
    scale 을 주면 상자 두께와 글자 크기가 이미지 크기에 맞춰 따라간다.
    """
    im = Image.open(src).convert("RGB")
    if scale is None:
        scale = im.width / 1440.0          # 1440 CSS 폭 기준
    width = width or max(3, round(5 * scale))
    font_size = font_size or max(12, round(19 * scale))
    d = ImageDraw.Draw(im)

    if box:
        # 글씨에 딱 붙으면 테두리가 글자를 먹는다. 조금 벌려 그린다.
        m = inset * scale
        box = [box[0] + m, box[1] + m, box[2] - m, box[3] - m]
        if showbox:
            d.rounded_rectangle(box, radius=round(radius * scale),
                                outline=PURPLE, width=width)
    if not text:
        im.save(dst)
        return dst

    f = _font(font_size)
    tw = d.textlength(text, font=f)
    th = font_size
    bw, bh = tw + pad * scale * 2, th + pad * scale * 1.4
    cy = (box[1] + box[3]) / 2 if box else im.height / 2
    bw_probe = tw + pad * scale * 2
    if side == "auto":
        # 오른쪽에 안 들어가면 왼쪽으로 넘긴다. 잘린 말풍선이 여러 번 나왔다.
        room = im.width - (box[2] if box else 0) - gap * scale
        side = "right" if room >= bw_probe else "left"
    if side in ("below", "above"):
        # 한국어 원본은 상자 아래에 말풍선을 두고 꼬리를 위로 세운 게 많다.
        cx = (box[0] + box[2]) / 2 if box else im.width / 2
        bx = cx - bw / 2
        if side == "below":
            by = (box[3] if box else 0) + gap * scale
            ty = by
            tail = [(cx - 12 * scale, ty), (cx + 12 * scale, ty),
                    (cx, ty - 16 * scale)]
        else:
            by = (box[1] if box else im.height) - gap * scale - bh
            ty = by + bh
            tail = [(cx - 12 * scale, ty), (cx + 12 * scale, ty),
                    (cx, ty + 16 * scale)]
        edge = 12 * scale
        bx = min(max(bx, edge), im.width - bw - edge)
        by = min(max(by, edge), im.height - bh - edge)
        d.rounded_rectangle([bx, by, bx + bw, by + bh],
                            radius=round(10 * scale), fill=BUBBLE)
        d.polygon(tail, fill=BUBBLE)
        d.text((bx + pad * scale, by + bh / 2), text, font=f, fill=TEXT,
               anchor="lm")
        im.save(dst)
        return dst
    if side == "right":
        bx = (box[2] if box else 0) + gap * scale
        tail = [(bx, cy - 12 * scale), (bx, cy + 12 * scale),
                (bx - 16 * scale, cy)]
    else:
        bx = (box[0] if box else im.width) - gap * scale - bw
        tail = [(bx + bw, cy - 12 * scale), (bx + bw, cy + 12 * scale),
                (bx + bw + 16 * scale, cy)]
    by = cy - bh / 2
    # 화면 밖으로 나가면 글씨가 잘린다. 안으로 붙인다. 꼬리는 원래 자리에 둔다.
    edge = 12 * scale
    bx = min(max(bx, edge), im.width - bw - edge)
    by = min(max(by, edge), im.height - bh - edge)
    d.rounded_rectangle([bx, by, bx + bw, by + bh],
                        radius=round(10 * scale), fill=BUBBLE)
    d.polygon(tail, fill=BUBBLE)
    d.text((bx + pad * scale, by + bh / 2), text, font=f, fill=TEXT,
           anchor="lm")
    im.save(dst)
    return dst
