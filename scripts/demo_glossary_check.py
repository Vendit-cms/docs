#!/usr/bin/env python3
"""임베드된 Supademo 데모의 영어 번역 문자열을 실제 배포본에서 긁어 용어 검사한다.

전사하지 않는다. `?lang=English` 로 받은 임베드 HTML 안의 translatedTexts 를 그대로 판다.
번역본이 없는 영어 원본 데모는 핫스팟 문구를 본다. 메타 설명(metadesc)도 같이 본다.

    python3 scripts/demo_glossary_check.py [en 디렉터리]
"""
import json, re, sys, os, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("g", os.path.join(HERE, "glossary_check.py"))
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)

# 임베드 파싱은 스냅샷 도구 것을 쓴다. 따옴표를 통째로 치환하던 사본은 문자열 경계를 깨뜨렸다.
spec = importlib.util.spec_from_file_location("a", os.path.join(HERE, "supademo_audit.py"))
A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)


def demo_ids(root):
    ids = set()
    for r, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(".mdx"):
                t = open(os.path.join(r, f), encoding="utf-8").read()
                ids |= set(re.findall(r"preview\.vendit\.co\.kr/(?:embed|demo)/([a-z0-9]+)", t))
    return sorted(ids)


def texts(demo_id):
    raw = A.fetch(demo_id, "English")
    out = []
    for m in re.finditer(r'"translatedTexts":\s*\[', raw):
        b = A.block(raw, m.end() - 1, "[", "]")
        try:
            arr = json.loads(b) if b else []
        except ValueError:
            continue
        for e in arr:
            t = (e.get("text") or "").strip()
            if t:
                out.append((e.get("entityType", "?"), t))
    demo = A.parse(demo_id, raw)
    if not out:
        # 영어로 찍은 데모는 번역본이 없어서 translatedTexts 가 비어 있다. 원문 핫스팟이 곧 영어다.
        # 이걸 안 보면 영어 데모 7편이 문자열 0개로 검사를 통과했다(2026-09-19).
        out = [("hotspot", h["text"]) for st in demo["steps"] for h in st["hotspots"] if h["text"]]
    if demo.get("metadesc"):
        # 링크 미리보기에 뜨는 설명. 한국어 데모라도 슈파데모 AI 가 영어로 붙인다.
        out.append(("metadesc", demo["metadesc"]))
    return out


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "en"
    rules = G.canon()
    ids = demo_ids(root)
    total, bad = 0, []
    for d in ids:
        ts = texts(d)
        total += len(ts)
        for et, t in ts:
            low = t.lower()
            if any(re.search(a, low) for a in G.ALLOW):
                continue
            for term, variants in G.BAD.items():
                if term not in rules:
                    continue
                if term in G.BILLING_RULES and G.BILLING_CTX.search(t):
                    continue
                if term == "상품" and G.PRODUCT_ALLOW.search(t):
                    continue
                for v in variants:
                    if re.search(r"\b" + re.escape(v), low):
                        bad.append((d, et, v, rules[term]["en"], rules[term]["key"], t[:80]))
        print(f"  {d}  영어 문자열 {len(ts):3}개")
    print()
    for d, et, v, en, key, t in bad:
        print(f"{d} [{et}]  '{v}' -> '{en}'  [{key}]\n    {t}")
    print(f"\n데모 {len(ids)}개 | 영어 문자열 {total}개 | 위반 {len(bad)}건")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
