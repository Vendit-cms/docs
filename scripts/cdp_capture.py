#!/usr/bin/env python3
"""VCMS 화면을 원본급 해상도로 캡처한다.

헤드리스 크롬을 CDP 로 붙잡고 돌린다. --screenshot 플래그와 달리 JS 를 실행할 수 있어서,
모달이나 드롭다운처럼 클릭해야 나오는 화면도 잡을 수 있다.

사전 준비(1회): ~/.vcms-capture-profile 에 로그인 + UI 언어 English + 사이드바 펼침.
    scripts/capture-login.sh

사용법:
    python3 scripts/cdp_capture.py jobs.json [출력디렉터리]

jobs.json 형식:
    [{"name": "en-users-list.png",
      "url": "https://www.vcms.io/.../setting/users",
      "js": "document.querySelector('button').click()",   # 선택
      "wait": 1.5,                                        # js 실행 후 대기(초)
      "blur": [[425,362,540,700]],                        # 선택, CSS 픽셀 기준
      "box": [1252,209,1392,254]}]                        # 선택, 보라 강조 사각형
"""
import base64, json, os, shutil, signal, subprocess, sys, time, asyncio
import websockets  # type: ignore

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE = os.path.expanduser(os.environ.get("VCMS_CAPTURE_PROFILE", "~/.vcms-capture-profile"))
PORT = int(os.environ.get("CDP_PORT", "9333"))
WIDTH, HEIGHT = 1440, 900
SCALE = int(os.environ.get("SCALE", "3"))

# 우하단 채팅 위젯을 숨긴다. 크기로 거르면 놓치는 래퍼가 있어서 위치로 잡는다.
PREP_JS = """
(() => {
  let n = 0;
  for (const e of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(e);
    if (cs.position !== 'fixed') continue;
    const r = e.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    const bottomRight = r.right > innerWidth - 200 && r.bottom > innerHeight - 200;
    const smallish = r.width < 260 && r.height < 260;
    if (bottomRight && smallish) { e.style.setProperty('display', 'none', 'important'); n++; }
  }
  for (const sel of ['#ch-plugin', '#ch-plugin-core', '.ch-desk-messenger', '[id*="channel-plugin"]']) {
    document.querySelectorAll(sel).forEach(e => {
      e.style.setProperty('display', 'none', 'important'); n++;
    });
  }
  return n;
})()
"""


def launch():
    if os.path.exists(os.path.join(PROFILE, "SingletonLock")):
        os.remove(os.path.join(PROFILE, "SingletonLock"))
    args = [CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
            "--no-default-browser-check", "--hide-scrollbars",
            f"--user-data-dir={PROFILE}", f"--remote-debugging-port={PORT}",
            f"--window-size={WIDTH},{HEIGHT}", f"--force-device-scale-factor={SCALE}",
            "about:blank"]
    p = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            import urllib.request
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1):
                return p
        except Exception:
            time.sleep(0.5)
    raise SystemExit("크롬이 디버깅 포트를 열지 못했다")


def page_ws():
    import urllib.request
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list") as r:
        targets = json.load(r)
    for t in targets:
        if t.get("type") == "page":
            return t["webSocketDebuggerUrl"]
    raise SystemExit("page 타깃을 못 찾았다")


class CDP:
    def __init__(self, ws):
        self.ws = ws
        self.i = 0

    async def send(self, method, **params):
        self.i += 1
        mid = self.i
        await self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        while True:
            msg = json.loads(await self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})

    async def js(self, expr):
        r = await self.send("Runtime.evaluate", expression=expr,
                            awaitPromise=True, returnByValue=True)
        return r.get("result", {}).get("value")

    async def click_text(self, pattern, nth=0):
        """텍스트로 요소를 찾아 실제 마우스 이벤트를 쏜다.

        React 는 합성 click() 을 무시하는 경우가 있다. 탭이나 라디오가 그렇다.
        """
        box = await self.js(f"""
        (() => {{
          const rx = {pattern};
          const els = [...document.querySelectorAll('button,a,[role],label,li,div,span,p')]
            .filter(e => e.children.length < 4 && rx.test((e.innerText || e.textContent || '').trim()))
            .filter(e => {{ const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; }})
            .sort((a, b) => {{
              const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
              return ra.width * ra.height - rb.width * rb.height;
            }});
          const el = els[{nth}];
          if (!el) return null;
          el.scrollIntoView({{block: 'center'}});
          const r = el.getBoundingClientRect();
          return {{x: r.left + r.width / 2, y: r.top + r.height / 2, text: (el.innerText||'').trim().slice(0, 40)}};
        }})()""")
        if not box:
            raise RuntimeError(f"클릭 대상 없음: {pattern}")
        for t in ("mousePressed", "mouseReleased"):
            await self.send("Input.dispatchMouseEvent", type=t, x=box["x"], y=box["y"],
                            button="left", clickCount=1)
        return box["text"]


async def run(jobs, outdir):
    ws_url = page_ws()
    done, failed = [], []
    async with websockets.connect(ws_url, max_size=200 * 1024 * 1024) as ws:
        cdp = CDP(ws)
        await cdp.send("Page.enable")
        await cdp.send("Runtime.enable")
        last_url = None
        for job in jobs:
            name = job["name"]
            try:
                if job["url"] != last_url or job.get("reload", True):
                    await cdp.send("Page.navigate", url=job["url"])
                    await asyncio.sleep(job.get("load", 4.0))
                    last_url = job["url"]
                await cdp.js(PREP_JS)
                for step in job.get("click", []):
                    pat, nth = (step, 0) if isinstance(step, str) else (step[0], step[1])
                    await cdp.click_text(pat, nth)
                    await asyncio.sleep(job.get("step_wait", 1.5))
                # click_at: 좌표를 돌려주는 JS. 아이콘 버튼처럼 텍스트가 없는 것에 쓴다.
                for expr in job.get("click_at", []):
                    box = await cdp.js(expr)
                    if not box:
                        raise RuntimeError(f"좌표 못 구함: {expr[:60]}")
                    for t in ("mousePressed", "mouseReleased"):
                        await cdp.send("Input.dispatchMouseEvent", type=t,
                                       x=box["x"], y=box["y"], button="left", clickCount=1)
                    await asyncio.sleep(job.get("step_wait", 1.5))
                if job.get("js"):
                    await cdp.js(job["js"])
                await cdp.js(PREP_JS)
                if job.get("click") or job.get("js") or job.get("click_at"):
                    await asyncio.sleep(job.get("wait", 1.5))
                shot = await cdp.send("Page.captureScreenshot", format="png",
                                      captureBeyondViewport=False)
                path = os.path.join(outdir, name)
                with open(path, "wb") as f:
                    f.write(base64.b64decode(shot["data"]))
                done.append((name, os.path.getsize(path)))
                print(f"  ok   {name}  {os.path.getsize(path)//1024}KB")
            except Exception as e:
                failed.append((name, str(e)[:120]))
                print(f"  FAIL {name}  {e}")
    return done, failed


def main():
    jobs = json.load(open(sys.argv[1], encoding="utf-8"))
    outdir = sys.argv[2] if len(sys.argv) > 2 else "/tmp/vcms-shots"
    os.makedirs(outdir, exist_ok=True)
    proc = launch()
    try:
        done, failed = asyncio.run(run(jobs, outdir))
    finally:
        proc.send_signal(signal.SIGTERM)
        time.sleep(1)
        lock = os.path.join(PROFILE, "SingletonLock")
        if os.path.exists(lock):
            os.remove(lock)
    print(f"\n완료 {len(done)} / 실패 {len(failed)}")
    for n, e in failed:
        print(f"  {n}: {e}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
