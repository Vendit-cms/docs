#!/usr/bin/env python3
"""배포된 영어 문서가 선언한 이미지 치수와 레포의 실제 파일 치수를 대조한다.

    python3 scripts/check_image_dims.py            # en 전체
    python3 scripts/check_image_dims.py ko         # ko 전체

왜 필요한가: **이미지를 같은 경로에 덮으면 Mintlify 가 옛 치수를 계속 쓴다.**
새 바이트는 내려주면서 `width`/`height` 와 `style="aspect-ratio:..."` 는 캐시된 값이라
`class="object-contain"` 이 그 박스 안에 레터박싱한다. 2026-09-13 에 `en-legend-*` 4장이
7680x3520(가로 2.18:1) 인데 900x974(세로 0.92:1) 박스에 들어가 화면 절반이 빈칸이었다.
배포를 두 번 더 해도 안 풀린다. 고치는 법은 파일명을 바꾸는 것뿐이다.

종료코드: 불일치가 하나라도 있으면 1.
"""
import concurrent.futures as cf
import os
import pathlib
import re
import sys
import unicodedata as ud
import urllib.parse
import urllib.request

from PIL import Image

SITE = "https://docs.vcms.io"
IMG_TAG = re.compile(r'<img[^>]*data-path="(images/[^"]+)"[^>]*>')
W = re.compile(r'\swidth="(\d+)"')
H = re.compile(r'\sheight="(\d+)"')


def fetch(slug):
    req = urllib.request.Request(f"{SITE}/{slug}", headers={"User-Agent": "vcms-docs-dimcheck"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return slug, r.read().decode("utf-8", "replace")


def main():
    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    root = pathlib.Path(__file__).resolve().parent.parent
    os.chdir(root)
    slugs = sorted(str(p)[:-4] for p in pathlib.Path(lang).rglob("*.mdx"))
    if not slugs:
        sys.exit(f"{lang}/ 에 mdx 가 없다")

    pages = {}
    with cf.ThreadPoolExecutor(8) as ex:
        for slug, html in ex.map(fetch, slugs):
            pages[slug] = html

    size_of = {}
    checked = 0
    bad = []
    for slug, html in sorted(pages.items()):
        for m in IMG_TAG.finditer(html):
            tag = m.group(0)
            path = urllib.parse.unquote(m.group(1))
            w, h = W.search(tag), H.search(tag)
            if not (w and h):
                continue
            checked += 1
            # 레포 파일명은 NFD 다. NFC 로 열면 못 찾는다.
            local = ud.normalize("NFD", path)
            if not os.path.exists(local):
                bad.append((slug, path, f"{w.group(1)}x{h.group(1)}", "파일 없음"))
                continue
            if local not in size_of:
                size_of[local] = Image.open(local).size
            aw, ah = size_of[local]
            if (int(w.group(1)), int(h.group(1))) != (aw, ah):
                bad.append((slug, path, f"{w.group(1)}x{h.group(1)}", f"{aw}x{ah}"))

    print(f"{lang}: {len(slugs)}쪽, img {checked}개 검사 · 일치 {checked - len(bad)} · 불일치 {len(bad)}")
    for slug, path, declared, actual in bad:
        print(f"  /{slug}")
        print(f"      {ud.normalize('NFC', path)}  선언 {declared} vs 실제 {actual}")
    if bad:
        print()
        print("고치는 법: 파일을 새 이름으로 옮기고(`git mv`) mdx 참조를 바꿔라. 덮어쓰기로는 안 풀린다.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
