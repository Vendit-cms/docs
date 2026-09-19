#!/usr/bin/env python3
"""녹화가 끝난 Supademo 데모를 에디터 화면 없이 고친다. 슈파데모 내부 API 를 그대로 부른다.

녹화 자체는 헤드리스로 못 한다. 확장이 activeTab 권한을 진짜 툴바 클릭으로만 받고,
VCMS 그리드는 탭이 보여야 렌더된다. 그 뒤 편집은 여기서 다 된다(2026-09-19).
예전엔 에디터를 CDP 로 몰았는데 메모리를 많이 먹고 좌표가 계속 밀렸다.

    python3 scripts/supademo_edit.py show    <demo>
    python3 scripts/supademo_edit.py tidy    <demo>             # 인트로 챕터와 영상 스텝 삭제
    python3 scripts/supademo_edit.py texts   <demo> <json>      # {"1": "문구", ...} 스텝 번호 기준
    python3 scripts/supademo_edit.py meta    <demo> --title T --desc D
    python3 scripts/supademo_edit.py archive <demo> [<demo> ...]

쓰기마다 공개 임베드를 다시 읽어서 실제로 바뀌었는지 본다. 안 바뀌었으면 exit 1.
`update-demo` 처럼 success 라고 답하고 필드를 무시하는 경로가 있어서다(metadesc 가 그랬다).

인증은 떠 있는 크롬(CDP_PORT, 기본 9222)의 쿠키를 메모리로만 읽는다. 파일로 안 쓰고 출력도 안 한다.
워크스페이스가 공용 계정이라 이 쿠키로 VENDIT 워크스페이스 전체를 쓸 수 있다. 데모 id 를 잘 보고 써라.

엔드포인트는 에디터 JS 청크에서 읽었다(demoEditEndpoints, hotspotEndpoints, demoEndpoints).
    POST /api/edit/delete-steps     {deleteStepsArray:[stepId], steps:[{id, number}] 남는 스텝 새 번호}
    POST /api/hotspot/<hotspotId>   {demoId, text}
    POST /api/edit/update-metadata  {id, title, metadesc, displayDescription, displayAuthor, indexable, customMetadataImage}
    POST /api/demo/archive          {demoIds:[id]}
"""
import asyncio, json, os, re, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import supademo_audit as A  # noqa: E402

API = "https://app.supademo.com"
PORT = int(os.environ.get("CDP_PORT", "9222"))
META_KEEP = ("displayDescription", "displayAuthor", "indexable", "customMetadataImage")


def cookie():
    """크롬 브라우저 레벨 CDP 로 supademo.com 쿠키를 읽는다. 탭이 필요 없다."""
    import websockets
    v = json.load(urllib.request.urlopen("http://127.0.0.1:%d/json/version" % PORT, timeout=5))

    async def get():
        async with websockets.connect(v["webSocketDebuggerUrl"], max_size=None, ping_interval=None) as ws:
            await ws.send(json.dumps({"id": 1, "method": "Storage.getCookies"}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == 1:
                    return msg["result"]["cookies"]

    cs = [c for c in asyncio.run(get()) if "supademo.com" in c.get("domain", "")]
    if not any(c["name"].endswith("next-auth.session-token") for c in cs):
        sys.exit("크롬에 슈파데모 로그인 세션이 없다. app.supademo.com 에 로그인하고 다시 돌려라")
    return "; ".join("%s=%s" % (c["name"], c["value"]) for c in cs)


def post(path, body, ck):
    # 쿠키를 argv 로 넘기면 ps 에 보인다. stdin 설정 파일로 넘긴다.
    cfg = 'header = "Cookie: %s"\n' % ck.replace('"', '\\"')
    r = subprocess.run(["curl", "-sS", "-X", "POST", API + path, "-K", "-",
                        "-H", "Content-Type: application/json", "-H", "Origin: " + API,
                        "--data-binary", json.dumps(body, ensure_ascii=False), "--max-time", "40",
                        "-w", "\n%{http_code}"],
                       input=cfg, capture_output=True, text=True)
    out, _, code = r.stdout.rpartition("\n")
    if code != "200":
        sys.exit("%s -> HTTP %s %s" % (path, code, out[:300]))
    return out


def load(demo):
    raw = A.fetch(demo)
    steps = sorted(A.raw_steps(raw), key=lambda s: float(s.get("number") or 0))
    rows = A.flight_rows(raw)
    for s in steps:
        for h in s.get("hotspots") or []:
            h["text"] = A.deref(h.get("text"), rows)
    return raw, steps


def kind(s):
    if s.get("video"):
        return "video"
    if s.get("image"):
        return "image"
    return "chapter"


def show(demo):
    raw, steps = load(demo)
    d = A.parse(demo, raw)
    print("%s  %s" % (demo, d["title"]))
    print("  metadesc: %s" % d["metadesc"])
    for i, s in enumerate(steps, 1):
        sec = A.step_seconds(s)
        texts = [(h.get("text") or "").strip().replace("\n", " ") for h in s.get("hotspots") or []]
        print("  %d. %-7s %s %s" % (i, kind(s), ("%.2fs" % sec) if sec else "", texts))
    return steps


def tidy(demo, ck):
    _, steps = load(demo)
    drop = [s for s in steps if kind(s) in ("chapter", "video")]
    keep = [s for s in steps if s not in drop]
    if not drop:
        print("지울 스텝 없음"); return
    if not keep:
        sys.exit("다 지우면 빈 데모가 된다. 멈춘다")
    print("지움: %s" % ["%s(%s)" % (kind(s), s["id"]) for s in drop])
    post("/api/edit/delete-steps", {
        "deleteStepsArray": [s["id"] for s in drop],
        "steps": [{"id": s["id"], "number": i} for i, s in enumerate(keep, 1)],
    }, ck)
    _, after = load(demo)
    kinds = [kind(s) for s in after]
    if len(after) != len(keep) or set(kinds) != {"image"}:
        sys.exit("삭제 뒤 확인 실패: %s" % kinds)
    print("남은 스텝 %d개, 전부 이미지" % len(after))


def texts(demo, path, ck):
    want = {int(k): v for k, v in json.load(open(path, encoding="utf-8")).items()}
    _, steps = load(demo)
    for n, text in sorted(want.items()):
        hs = steps[n - 1].get("hotspots") or []
        if not hs:
            sys.exit("스텝 %d 에 핫스팟이 없다" % n)
        post("/api/hotspot/%s" % hs[0]["id"], {"demoId": demo, "text": text}, ck)
    _, after = load(demo)
    bad = [n for n, t in want.items() if ((after[n - 1]["hotspots"][0].get("text") or "").strip() != t.strip())]
    if bad:
        sys.exit("문구가 안 바뀐 스텝: %s" % bad)
    print("문구 %d개 반영 확인" % len(want))


def meta(demo, title, desc, ck):
    raw, _ = load(demo)
    cur = {}
    for k in META_KEEP:
        m = re.search(r'"%s":\s*(true|false|null|"(?:[^"\\]|\\.)*")' % k, raw)
        if not m:
            sys.exit("%s 현재 값을 못 읽었다. 덮어쓸 수 있어서 멈춘다" % k)
        cur[k] = json.loads(m.group(1))
    d = A.parse(demo, raw)
    body = {"id": demo, "title": title or d["title"], "metadesc": desc if desc is not None else d["metadesc"], **cur}
    post("/api/edit/update-metadata", body, ck)
    after = A.parse(demo, A.fetch(demo))
    if after["title"] != body["title"] or after["metadesc"] != body["metadesc"]:
        sys.exit("반영 안 됨: %r / %r" % (after["title"], after["metadesc"]))
    print("제목, 설명 반영 확인")


def archive(demos, ck):
    used = A.embedded_ids()
    live = [d for d in demos if d in used]
    if live:
        sys.exit("문서에 아직 붙어 있다. 보관하면 페이지가 깨진다: %s" % live)
    post("/api/demo/archive", {"demoIds": demos}, ck)
    print("보관함으로: %s" % demos)


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    cmd, demo = a[0], a[1]
    if cmd == "show":
        show(demo); return
    ck = cookie()
    if cmd == "tidy":
        tidy(demo, ck)
    elif cmd == "texts":
        texts(demo, a[2], ck)
    elif cmd == "meta":
        title = a[a.index("--title") + 1] if "--title" in a else None
        desc = a[a.index("--desc") + 1] if "--desc" in a else None
        meta(demo, title, desc, ck)
    elif cmd == "archive":
        archive(a[1:], ck)
    else:
        sys.exit(__doc__)
    show(demo) if cmd != "archive" else None


if __name__ == "__main__":
    main()
