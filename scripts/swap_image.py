#!/usr/bin/env python3
"""en 페이지의 이미지 참조를 새 영어 캡처로 갈아끼운다.

이 레포는 파일명을 NFD 로 저장한다. 셸에서 친 한글은 NFC 라서 `sed` 가 조용히 아무것도
못 바꾸고 성공한 척한다. 그래서 치환은 항상 이 스크립트로 한다.

    python3 scripts/swap_image.py <en페이지.mdx> 옛파일.png=새파일.png [...]
    python3 scripts/swap_image.py --map map.tsv          # 탭 구분: 페이지<TAB>옛<TAB>새

ko/ 는 글이 동결이다(2026-09-10). 이미지 참조 교체만 --ko-images 로 허용한다(2026-09-11 Dean).
이 스크립트는 /images/ 경로만 바꾸므로 문장은 건드리지 않는다.
"""
import os
import sys
KO_IMAGES = "--ko-images" in sys.argv
if KO_IMAGES:
    sys.argv.remove("--ko-images")
import unicodedata as ud


def swap(page, pairs):
    if (page.startswith("ko/") or "/ko/" in page) and not KO_IMAGES:
        raise SystemExit(f"거부: ko/ 는 글이 동결이다. 이미지 참조만 바꾸려면 --ko-images ({page})")
    src = open(page, encoding="utf-8").read()
    out, hits, misses = src, [], []
    for old, new in pairs:
        # MDX 는 괄호를 이스케이프해서 쓴다: image\(67\).png. 그 형태도 찾는다.
        esc = old.replace("(", "\\(").replace(")", "\\)")
        for form, name in (("NFD", old), ("NFC", old), ("NFD", esc), ("NFC", esc)):
            token = "/images/" + ud.normalize(form, name)
            if token in out:
                out = out.replace(token, "/images/" + new)
                hits.append((old, new))
                break
        else:
            misses.append(old)
    if out != src:
        open(page, "w", encoding="utf-8").write(out)
    return hits, misses


def main():
    if sys.argv[1] == "--map":
        rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[2], encoding="utf-8")
                if l.strip() and not l.startswith("#")]
        by = {}
        for page, old, new in rows:
            by.setdefault(page, []).append((old, new))
    else:
        page = sys.argv[1]
        by = {page: [tuple(a.split("=", 1)) for a in sys.argv[2:]]}

    ok = bad = 0
    for page, pairs in by.items():
        hits, misses = swap(page, pairs)
        ok += len(hits)
        bad += len(misses)
        for old, new in hits:
            print(f"  ok   {page}  {old} -> {new}")
        for old in misses:
            print(f"  MISS {page}  {old}  (참조가 없다)")
    print(f"\n치환 {ok} / 실패 {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
