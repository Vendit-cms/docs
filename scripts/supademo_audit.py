#!/usr/bin/env python3
"""문서에 임베드된 Supademo 데모를 스냅샷으로 떠서 git 에 남긴다.

왜 필요한가. 워크스페이스가 공용 계정 하나(VENDIT)로 돌아가는데 demo versioning 은
Growth 플랜부터라 못 켠다. 즉 슈파데모 안에는 되돌리기도 변경 이력도 없다.
누가 데모를 덮어써도 흔적이 안 남는다. 그래서 우리가 밖에서 기록한다.
이 스냅샷의 diff 가 사실상의 변경 이력이다. (Dean, 2026-09-15)

자격증명이 없어도 된다. 공개된 임베드 HTML 을 그대로 파싱한다.
MCP 도 API 키도 안 쓰니 크론이나 CI 에 그대로 걸 수 있다.

    python3 scripts/supademo_audit.py            # 스냅샷 갱신
    python3 scripts/supademo_audit.py --check    # 비교만. 달라졌으면 exit 1

출력이 결정적이다. 바뀐 게 없으면 파일 바이트가 그대로라 `git status` 가 깨끗하다.
그래서 수집 시각을 파일에 안 적는다. 수집 시각은 커밋 날짜가 말해준다.
"""
import hashlib, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "audit", "supademo")
EMBED = "https://preview.vendit.co.kr/embed/{}?embed_v=2"

ULID = re.compile(r"\b[0-7][0-9A-HJKMNP-TV-Z]{25}\b")
EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")


def short(s: str, n: int = 8) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:n]


def scrub(s):
    """레포가 public 이다. 업장 식별자와 메일 주소는 해시로 바꾼다.

    지우지 않고 해시로 바꾸는 이유: 값이 실제로 달라지면 diff 에 그대로 드러나야 한다.
    """
    if not isinstance(s, str):
        return s
    s = ULID.sub(lambda m: "ULID:" + short(m.group(0)), s)
    s = EMAIL.sub(lambda m: "EMAIL:" + short(m.group(0)), s)
    return s


def embedded_ids():
    """en/ ko/ mdx 가 실제로 쓰는 데모 id 와 그걸 쓰는 파일 목록."""
    used = {}
    pat = re.compile(r"preview\.vendit\.co\.kr/(?:embed|demo)/([a-z0-9]+)")
    for top in ("en", "ko"):
        base = os.path.join(ROOT, top)
        for r, _, fs in os.walk(base):
            for f in fs:
                if not f.endswith(".mdx"):
                    continue
                p = os.path.join(r, f)
                rel = os.path.relpath(p, ROOT)
                for d in pat.findall(open(p, encoding="utf-8").read()):
                    used.setdefault(d, set()).add(rel)
    return {k: sorted(v) for k, v in used.items()}


def block(raw, start, open_ch, close_ch):
    """start 위치의 여는 괄호부터 짝이 맞는 닫는 괄호까지 잘라낸다. 문자열 안의 괄호는 센다."""
    depth, j, instr, esc = 0, start, False, False
    while j < len(raw):
        c = raw[j]
        if instr:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                instr = False
        elif c == '"':
            instr = True
        elif c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return raw[start:j + 1]
        j += 1
    return None


def fetch(demo_id):
    r = subprocess.run(["curl", "-sS", "-f", "--max-time", "45", EMBED.format(demo_id)],
                       capture_output=True, text=True)
    if r.returncode != 0 or len(r.stdout) < 500:
        raise RuntimeError(f"임베드를 못 받았다 (rc={r.returncode}, {len(r.stdout)} bytes): {r.stderr.strip()[:200]}")
    # Next.js 페이로드는 한 번 더 이스케이프돼 있다. 문자열 리터럴로 되돌린 뒤 파싱한다.
    return r.stdout.replace('\\"', '"').replace("\\\\", "\\")


def parse(demo_id, raw):
    steps, best = None, None
    for m in re.finditer(r'"steps":\s*\[', raw):
        b = block(raw, m.end() - 1, "[", "]")
        if not b:
            continue
        try:
            cand = json.loads(b)
        except Exception:
            continue
        if isinstance(cand, list) and cand and isinstance(cand[0], dict) and "number" in cand[0]:
            # Next.js 는 청크를 스트리밍해서 같은 배열이 여러 번, 순서도 다르게 나올 수 있다.
            # 길이가 같으면 내용으로 못박는다. 안 그러면 실행마다 스냅샷이 흔들린다.
            key = (len(cand), json.dumps(cand, sort_keys=True, ensure_ascii=False))
            if steps is None or key > best:
                steps, best = cand, key
    if steps is None:
        raise RuntimeError("steps 배열을 못 찾았다. 임베드 구조가 바뀌었을 수 있다")

    def field(key, pattern=r'"([^"]*)"'):
        m = re.search(r'"%s":\s*%s' % (re.escape(key), pattern), raw)
        return m.group(1) if m else None

    out = {
        "id": demo_id,
        "title": field("title"),
        "published": '"published":true' in raw,
        "domainURL": scrub(field("domainURL") or ""),
        "stepCount": len(steps),
        "steps": [],
    }
    for s in sorted(steps, key=lambda x: x.get("number", 0)):
        media = s.get("image") or s.get("video") or ""
        rec = {
            "n": s.get("number"),
            # 전체 URL 은 계정 id 를 물고 다닌다. 파일명만 남겨도 교체 여부는 그대로 보인다.
            "media": os.path.basename(media.split("?")[0]) if media else None,
            "hotspots": [],
        }
        for h in s.get("hotspots") or []:
            rec["hotspots"].append({
                # 사람이 읽는 문구. 이게 바뀌면 diff 에 그대로 보여야 한다.
                "text": scrub((h.get("text") or "").strip()),
                # 캡처된 DOM 조각. 통째로 넣으면 diff 가 읽을 수 없게 된다. 지문만 남긴다.
                "html": short(h.get("htmlValue") or "", 12),
                "style": h.get("style"),
            })
        out["steps"].append(rec)
    return out


def write(demo, used):
    demo = dict(demo)
    demo["embeddedIn"] = used.get(demo["id"], [])
    p = os.path.join(OUT, "demos", demo["id"] + ".json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(demo, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    return p


def index(demos, used):
    lines = [
        "# Supademo 스냅샷",
        "",
        "슈파데모는 공용 계정 하나로 돌아가고 버전 관리가 꺼져 있다(Growth 플랜 전용).",
        "제품 안에 변경 이력이 없어서 여기에 남긴다. **이 디렉터리의 git diff 가 변경 이력이다.**",
        "갱신은 `python3 scripts/supademo_audit.py`, 확인만 하려면 `--check`.",
        "",
        "| 데모 | 제목 | 스텝 | 공개 | 쓰는 문서 |",
        "|---|---|---:|---|---|",
    ]
    for d in sorted(demos, key=lambda x: (x["title"] or "").lower()):
        docs = used.get(d["id"], [])
        lines.append("| `%s` | %s | %d | %s | %s |" % (
            d["id"], (d["title"] or "?").replace("|", "\\|"), d["stepCount"],
            "예" if d["published"] else "아니오",
            " ".join("`%s`" % x for x in docs) or "-"))
    lines += ["", "합계 %d편." % len(demos), ""]
    p = os.path.join(OUT, "index.md")
    os.makedirs(OUT, exist_ok=True)
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    return p


def main():
    check = "--check" in sys.argv
    used = embedded_ids()
    if not used:
        print("임베드된 데모가 하나도 없다. mdx 를 못 읽었거나 임베드 주소가 바뀐 것이다.", file=sys.stderr)
        return 2

    demos, failed = [], []
    for i, d in enumerate(sorted(used), 1):
        try:
            demos.append(parse(d, fetch(d)))
            print("  [%2d/%d] %s ok" % (i, len(used), d))
        except Exception as e:
            failed.append((d, str(e)))
            print("  [%2d/%d] %s 실패: %s" % (i, len(used), d, e), file=sys.stderr)

    if failed:
        # 한 편이라도 못 받으면 아무것도 안 쓴다. 반쪽 스냅샷을 커밋하면
        # 멀쩡한 데모가 사라진 것처럼 보인다.
        print("\n%d편을 못 받았다. 스냅샷을 쓰지 않는다." % len(failed), file=sys.stderr)
        return 1

    for d in demos:
        write(d, used)
    index(demos, used)
    print("\n%d편 기록. %s" % (len(demos), os.path.relpath(OUT, ROOT)))

    drift = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--", "audit/supademo"],
                           capture_output=True, text=True).stdout.strip()
    if not drift:
        print("직전 커밋과 동일하다. 바뀐 데모 없음.")
        return 0
    print("\n바뀐 것:")
    print(drift)
    if check:
        print("\n--check 라 되돌린다.")
        subprocess.run(["git", "-C", ROOT, "checkout", "--", "audit/supademo"])
        subprocess.run(["git", "-C", ROOT, "clean", "-qfd", "--", "audit/supademo"])
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
