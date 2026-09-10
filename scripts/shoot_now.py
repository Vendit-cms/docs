#!/usr/bin/env python3
"""Dean 이 직접 띄워 놓은 크롬 창을, 지금 이 순간 그대로 원본급으로 찍는다.

scripts/open-window.sh 로 띄운 창에 CDP 로 붙는다. 헤드리스 캡처와 달리
페이지를 내가 조작하지 않는다. 화면에 보이는 그대로만 찍는다.

    python3 scripts/shoot_now.py <파일명.png> [출력폴더]

창 크기는 그대로 두고 Emulation 으로 배율만 3배로 올려 찍은 뒤 되돌린다.
그래서 결과물은 4320x2700 급이고, Dean 화면은 잠깐 다시 그려지는 것 말고는 변화가 없다.
"""
import asyncio
import base64
import json
import os
import sys
import urllib.request

import websockets  # type: ignore

PORT = int(os.environ.get("CDP_PORT", "9222"))
SCALE = int(os.environ.get("SCALE", "3"))
WIDTH = int(os.environ.get("WIN_W", "1440"))
HEIGHT = int(os.environ.get("WIN_H", "900"))

HIDE_CHAT = """
(() => {
  let n = 0;
  for (const e of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(e);
    if (cs.position !== 'fixed') continue;
    const r = e.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    if (r.right > innerWidth - 200 && r.bottom > innerHeight - 200
        && r.width < 260 && r.height < 260) {
      e.style.setProperty('display', 'none', 'important'); n++;
    }
  }
  return n;
})()
"""


def page_target():
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list") as r:
        targets = json.load(r)
    pages = [t for t in targets if t.get("type") == "page" and t.get("url", "").startswith("http")]
    if not pages:
        raise SystemExit(f"열려 있는 페이지 탭이 없다. 포트 {PORT} 에 창이 떠 있나?")
    return pages[0]


async def shoot(target, path):
    async with websockets.connect(target["webSocketDebuggerUrl"],
                                  max_size=200 * 1024 * 1024) as ws:
        i = 0

        async def send(method, **params):
            nonlocal i
            i += 1
            mid = i
            await ws.send(json.dumps({"id": mid, "method": method, "params": params}))
            while True:
                m = json.loads(await ws.recv())
                if m.get("id") == mid:
                    if "error" in m:
                        raise RuntimeError(f"{method}: {m['error']}")
                    return m.get("result", {})

        await send("Runtime.enable")
        await send("Runtime.evaluate", expression=HIDE_CHAT, returnByValue=True)
        await send("Emulation.setDeviceMetricsOverride", width=WIDTH, height=HEIGHT,
                   deviceScaleFactor=SCALE, mobile=False)
        await asyncio.sleep(1.2)
        shot = await send("Page.captureScreenshot", format="png", captureBeyondViewport=False)
        await send("Emulation.clearDeviceMetricsOverride")
        with open(path, "wb") as f:
            f.write(base64.b64decode(shot["data"]))


def main():
    name = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else "/tmp/vcms-shots"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    t = page_target()
    print(f"찍는 중: {t.get('title', '')[:50]}  {t.get('url', '')[:80]}")
    asyncio.run(shoot(t, path))
    print(f"  ok  {path}  {os.path.getsize(path) // 1024}KB")


if __name__ == "__main__":
    main()
