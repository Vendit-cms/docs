#!/usr/bin/env python3
"""문서에 임베드된 Supademo 데모를 스냅샷으로 떠서 git 에 남긴다.

왜 필요한가. 워크스페이스가 공용 계정 하나(VENDIT)로 돌아가는데 demo versioning 은
Growth 플랜부터라 못 켠다. 즉 슈파데모 안에는 되돌리기도 변경 이력도 없다.
누가 데모를 덮어써도 흔적이 안 남는다. 그래서 우리가 밖에서 기록한다.
이 스냅샷의 diff 가 사실상의 변경 이력이다. (Dean, 2026-09-15)

자격증명이 없어도 된다. 공개된 임베드 HTML 을 그대로 파싱한다.
MCP 도 API 키도 안 쓰니 크론이나 CI 에 그대로 걸 수 있다.

    python3 scripts/supademo_audit.py            # 스냅샷 갱신
    python3 scripts/supademo_audit.py --check    # 비교만. 달라졌으면 exit 1. 트리는 안 건드린다

출력이 결정적이다. 바뀐 게 없으면 파일 바이트가 그대로라 `git status` 가 깨끗하다.
그래서 수집 시각을 파일에 안 적는다. 수집 시각은 커밋 날짜가 말해준다.
"""
import filecmp, hashlib, json, os, re, shutil, subprocess, sys, tempfile

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


PUSH = "self.__next_f.push([1,"
FLIGHT_REF = re.compile(r"^\$[0-9a-f]{1,6}$")


def json_string_at(raw, i):
    """raw[i] 가 여는 따옴표. 닫는 따옴표까지의 JSON 문자열 리터럴을 그대로 잘라 준다."""
    j, esc = i + 1, False
    while j < len(raw):
        c = raw[j]
        if esc:
            esc = False
        elif c == "\\":
            esc = True
        elif c == '"':
            return raw[i:j + 1]
        j += 1
    return None


def fetch(demo_id, lang=None):
    url = EMBED.format(demo_id) + ("&lang=" + lang if lang else "")
    r = subprocess.run(["curl", "-sS", "-f", "--max-time", "45", url],
                       capture_output=True, text=True)
    if r.returncode != 0 or len(r.stdout) < 500:
        raise RuntimeError(f"임베드를 못 받았다 (rc={r.returncode}, {len(r.stdout)} bytes): {r.stderr.strip()[:200]}")
    # Next.js 는 페이로드를 self.__next_f.push([1,"..."]) 조각으로 흘려보낸다.
    # 조각마다 json.loads 로 풀어서 이어 붙인다. 통째로 치환하면 이스케이프된 따옴표까지
    # 같이 풀려서 문자열 경계가 깨진다.
    parts, i = [], r.stdout.find(PUSH)
    while i != -1:
        q = r.stdout.find('"', i + len(PUSH))
        lit = json_string_at(r.stdout, q) if q != -1 else None
        if lit:
            try:
                parts.append(json.loads(lit))
            except ValueError:
                pass
        i = r.stdout.find(PUSH, i + len(PUSH))
    if not parts:
        raise RuntimeError("페이로드 조각을 하나도 못 읽었다. 임베드 구조가 바뀐 것이다")
    return "".join(parts)


def flight_rows(payload):
    """RSC 행 표. 번호 -> 텍스트.

    같은 문자열을 두 번 보내지 않으려고 Next.js 는 `$1b` 같은 행 참조를 쓴다.
    행 번호는 페이로드 안의 위치라서 위쪽이 조금만 바뀌어도 통째로 밀린다.
    그 번호를 그대로 해시하면 데모는 그대로인데 스냅샷만 바뀐다.
    2026-09-19 에 이것 때문에 13편이 한꺼번에 바뀐 것처럼 보였다.

    행은 앞에서부터 차례로 읽어야 한다. 텍스트 행(`1b:T266b,`)은 머리에 적힌 바이트 수만큼이
    내용이고, 끝나면 줄바꿈 없이 바로 다음 행 머리가 붙는다. 처음엔 줄 맨 앞의 머리만 찾아서
    텍스트 행 뒤에 붙은 행을 다 놓쳤다. 참조 44개 중 30개가 안 풀린 채 번호로 해시됐고,
    번호가 가끔 밀릴 때만 스냅샷이 흔들려서 한참 몰랐다(2026-09-19).
    행 번호가 빈 힌트 행(`:HL[...]`)도 있다.
    """
    data = payload.encode("utf-8")
    rows, i, n = {}, 0, len(data)
    head = re.compile(rb"([0-9a-f]*):")
    text = re.compile(rb"T([0-9a-f]+),")
    while i < n:
        m = head.match(data, i)
        if not m:
            # 행 머리가 아닌 자리. 다음 줄에서 다시 맞춘다
            j = data.find(b"\n", i)
            if j == -1:
                break
            i = j + 1
            continue
        rid, j = m.group(1).decode(), m.end()
        t = text.match(data, j)
        if t:
            size = int(t.group(1), 16)
            body = data[t.end():t.end() + size]
            i = t.end() + size
        else:
            k = data.find(b"\n", j)
            k = n if k == -1 else k
            body = data[j:k]
            i = k + 1
        if rid:
            rows[rid] = body.decode("utf-8", "ignore")
    return rows


def deref(v, rows):
    """`$1b` 꼴이면 행 내용으로 바꾼다. 못 찾으면 그대로 둔다."""
    if isinstance(v, str) and FLIGHT_REF.match(v):
        return rows.get(v[1:], v)
    return v


def step_seconds(s):
    """영상 스텝의 재생 길이(초). 이미지 스텝은 None.

    trimStart/trimEnd 는 초가 아니라 videoDuration 에 대한 퍼센트다. 두 번 속았다.
    """
    vd = s.get("videoDuration")
    if not vd:
        return None
    try:
        ts = float(s.get("trimStart") or 0)
        te = float(s.get("trimEnd") if s.get("trimEnd") is not None else 100)
        return round((te - ts) / 100.0 * float(vd), 2)
    except (TypeError, ValueError):
        return None


def parse(demo_id, raw):
    rows = flight_rows(raw)
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

    def field(key):
        m = re.search(r'"%s":\s*"' % re.escape(key), raw)
        lit = json_string_at(raw, m.end() - 1) if m else None
        return json.loads(lit) if lit else None

    out = {
        "id": demo_id,
        "title": field("title"),
        "published": '"published":true' in raw,
        "domainURL": scrub(field("domainURL") or ""),
        # 링크 미리보기, 공유 페이지, 검색에 뜨는 설명. 슈파데모 AI 가 영어로 지어 붙인다.
        # 한국어 데모에 "sales management" 가 박혀 있었는데 아무 검사기도 못 봤다(2026-09-19).
        # 키 이름은 metadesc 다. seoDescription 은 켜고 끄는 설정값(true/false)이라 헷갈리지 마라.
        "metadesc": scrub((field("metadesc") or "").strip()),
        "stepCount": len(steps),
        "steps": [],
    }
    for s in sorted(steps, key=lambda x: x.get("number", 0)):
        media = s.get("image") or s.get("video") or ""
        rec = {
            "n": s.get("number"),
            # 전체 URL 은 계정 id 를 물고 다닌다. 파일명만 남겨도 교체 여부는 그대로 보인다.
            "media": os.path.basename(media.split("?")[0]) if media else None,
            # 영상 스텝이 몇 초인지. trimStart/trimEnd 는 videoDuration 에 대한 퍼센트다.
            # 이걸 안 적으면 트림을 고쳐도 diff 가 조용해서 이력이 안 남는다(2026-09-18).
            "sec": step_seconds(s),
            "hotspots": [],
        }
        for h in s.get("hotspots") or []:
            rec["hotspots"].append({
                # 사람이 읽는 문구. 이게 바뀌면 diff 에 그대로 보여야 한다.
                "text": scrub((deref(h.get("text"), rows) or "").strip()),
                # 캡처된 DOM 조각. 통째로 넣으면 diff 가 읽을 수 없게 된다. 지문만 남긴다.
                "html": short(deref(h.get("htmlValue"), rows) or "", 12),
                "style": h.get("style"),
            })
        out["steps"].append(rec)
    return out


def write(demo, used, out=OUT):
    demo = dict(demo)
    demo["embeddedIn"] = used.get(demo["id"], [])
    p = os.path.join(out, "demos", demo["id"] + ".json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(demo, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    return p


def index(demos, used, out=OUT):
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
    p = os.path.join(out, "index.md")
    os.makedirs(out, exist_ok=True)
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    return p


def prune(demos, out=OUT):
    """문서에서 빠진 데모의 스냅샷을 지운다. 지운 id 목록을 돌려준다.

    안 지우면 교체된 데모가 옛 embeddedIn 을 단 채 남아서 아직 쓰이는 것처럼 보인다.
    2026-09-19 에 cmtyc75ri0hrxqme9293l1cf5 가 그랬다. 26개 파일에 index 는 25편.
    기록은 git 에 남는다.
    """
    keep = {d["id"] + ".json" for d in demos}
    base = os.path.join(out, "demos")
    gone = []
    for f in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        if f.endswith(".json") and f not in keep:
            os.remove(os.path.join(base, f))
            gone.append(f[:-5])
    return gone


def tree_diff(a, b):
    """두 디렉터리를 파일 단위로 비교한다. 바뀐 것, a 에만, b 에만 있는 상대 경로."""
    changed, only_a, only_b = [], [], []

    def walk(c, rel):
        changed.extend(os.path.join(rel, f) for f in c.diff_files)
        only_a.extend(os.path.join(rel, f) for f in c.left_only)
        only_b.extend(os.path.join(rel, f) for f in c.right_only)
        for name, sub in c.subdirs.items():
            walk(sub, os.path.join(rel, name))

    # 방금 쓴 파일이라 mtime 이 늘 달라서 dircmp 가 바이트까지 내려가 비교한다.
    walk(filecmp.dircmp(a, b), "")
    return sorted(changed), sorted(only_a), sorted(only_b)


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

    if check:
        # 트리에 쓰고 git 으로 되돌리던 때가 있었다. 그러면 커밋 전의 새 스냅샷까지
        # git clean 이 지운다. 임시 디렉터리에 쓰고 비교만 한다.
        tmp = tempfile.mkdtemp(prefix="supademo-check-")
        try:
            for d in demos:
                write(d, used, tmp)
            index(demos, used, tmp)
            changed, fresh, stale = tree_diff(tmp, OUT)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        if not (changed or fresh or stale):
            print("\n디스크의 스냅샷과 동일하다. 바뀐 데모 없음.")
            return 0
        for label, xs in (("바뀜", changed), ("새로 생김", fresh), ("문서에서 빠짐", stale)):
            for x in xs:
                print("  %s  %s" % (label, x))
        print("\n--check 라 아무것도 안 썼다. 반영하려면 --check 없이 돌려라.")
        return 1

    for d in demos:
        write(d, used)
    gone = prune(demos)
    index(demos, used)
    print("\n%d편 기록. %s" % (len(demos), os.path.relpath(OUT, ROOT)))
    for g in gone:
        print("  문서에서 빠져서 지움: %s" % g)

    drift = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--", "audit/supademo"],
                           capture_output=True, text=True).stdout.strip()
    if not drift:
        print("직전 커밋과 동일하다. 바뀐 데모 없음.")
        return 0
    print("\n바뀐 것:")
    print(drift)
    return 0


if __name__ == "__main__":
    sys.exit(main())
