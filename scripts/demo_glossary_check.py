#!/usr/bin/env python3
"""임베드된 Supademo 데모의 영어 번역 문자열을 실제 배포본에서 긁어 용어 검사한다.

전사하지 않는다. `?lang=English` 로 받은 임베드 HTML 안의 translatedTexts 를 그대로 판다.

    python3 scripts/demo_glossary_check.py [en 디렉터리]
"""
import json, re, subprocess, sys, os, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("g", os.path.join(HERE, "glossary_check.py"))
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)

EMBED = "https://preview.vendit.co.kr/embed/{}?embed_v=2&lang=English"


def demo_ids(root):
    ids = set()
    for r, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(".mdx"):
                t = open(os.path.join(r, f), encoding="utf-8").read()
                ids |= set(re.findall(r"preview\.vendit\.co\.kr/(?:embed|demo)/([a-z0-9]+)", t))
    return sorted(ids)


def texts(demo_id):
    html = subprocess.run(["curl", "-s", EMBED.format(demo_id)],
                          capture_output=True, text=True).stdout
    # Next.js 페이로드는 한 번 더 이스케이프돼 있다. 문자열 리터럴로 되돌린 뒤 파싱한다.
    raw = html.replace('\\"', '"').replace("\\\\", "\\")
    out = []
    for m in re.finditer(r'"translatedTexts":\s*\[', raw):
        i = m.end() - 1
        depth, j = 0, i
        while j < len(raw):
            if raw[j] == "[":
                depth += 1
            elif raw[j] == "]":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        try:
            arr = json.loads(raw[i:j + 1])
        except Exception:
            continue
        for e in arr:
            t = (e.get("text") or "").strip()
            if t:
                out.append((e.get("entityType", "?"), t))
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
