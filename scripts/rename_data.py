#!/usr/bin/env python3
"""VENDIT HOTEL 의 샘플 데이터 이름을 영어로 바꾼다.

영어 문서 스크린샷에 `테스트`, `디럭스 패키지(와인)` 같은 한글 데이터가 그대로 찍히면
영어판 완성도가 떨어진다. 이름만 바꾼다. 재고·요금·연동은 건드리지 않는다.

    python3 scripts/rename_data.py <라우트> "옛이름=새이름" ["옛이름=새이름" ...]
    python3 scripts/rename_data.py setting/packages/nightuse "디럭스=Deluxe standard"

동작: 목록에서 그 텍스트를 가진 잎 노드를 클릭 -> 모달의 input[name=name] 을
네이티브 세터로 바꾸고 input/change 를 쏜다(React 는 el.value 직접 대입을 무시한다)
-> Save 클릭 -> 모달이 닫혔는지 확인.

**VENDIT HOTEL 전용.** Dean 이 이 업소에 한해 쓰기를 허용했다. 다른 업소에 쓰지 마라.
"""
import asyncio
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request

import websockets  # type: ignore

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE = os.path.expanduser(os.environ.get("VCMS_CAPTURE_PROFILE", "~/.vcms-capture-profile"))
PORT = int(os.environ.get("CDP_PORT", "9336"))
ACC = os.environ.get("VCMS_ACC", "01JT799TA002T8QJ8KJ48XKKHJ")
BASE = f"https://www.vcms.io/accommodations/{ACC}"

RENAME_JS = """
(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const setNative = (el, v) => {
    const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
    s.call(el, v);
    el.dispatchEvent(new Event("input", {bubbles: true}));
    el.dispatchEvent(new Event("change", {bubbles: true}));
  };
  const pairs = %s;
  const log = [];
  for (const [oldName, newName] of pairs) {
    const el = [...document.querySelectorAll("*")]
      .find(e => e.children.length === 0 && (e.textContent || "").trim() === oldName);
    if (!el) { log.push([oldName, "목록에 없음"]); continue; }
    el.click(); await sleep(2500);
    const inp = document.querySelector("[role=dialog] input[name=name]")
             || document.querySelector("input[name=name]");
    if (!inp) { log.push([oldName, "이름 입력칸 없음"]); continue; }
    setNative(inp, newName); await sleep(700);
    const save = [...document.querySelectorAll("[role=dialog] button")]
      .find(b => (b.innerText || "").trim() === "Save");
    if (!save) { log.push([oldName, "Save 버튼 없음"]); continue; }
    save.click(); await sleep(3000);
    log.push([oldName + " -> " + newName,
              document.querySelector("[role=dialog]") ? "모달 안 닫힘" : "ok"]);
    await sleep(1200);
  }
  const left = [...document.querySelectorAll("*")]
    .filter(e => e.children.length === 0 && /[가-힣]/.test(e.textContent || ""))
    .map(e => e.textContent.trim()).filter(t => t.length < 40);
  return {log, remainingKorean: [...new Set(left)]};
})()
"""


def launch():
    lock = os.path.join(PROFILE, "SingletonLock")
    if os.path.exists(lock):
        os.remove(lock)
    p = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
         f"--user-data-dir={PROFILE}", f"--remote-debugging-port={PORT}",
         "--window-size=1440,1200", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1)
            return p
        except Exception:
            time.sleep(0.5)
    raise SystemExit("디버깅 포트 안 열림")


async def go(route, pairs):
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list") as r:
        ws_url = next(t["webSocketDebuggerUrl"] for t in json.load(r) if t["type"] == "page")
    async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
        i = 0

        async def send(method, **params):
            nonlocal i
            i += 1
            mid = i
            await ws.send(json.dumps({"id": mid, "method": method, "params": params}))
            while True:
                m = json.loads(await ws.recv())
                if m.get("id") == mid:
                    return m
        await send("Page.enable")
        await send("Runtime.enable")
        await send("Page.navigate", url=f"{BASE}/{route}")
        await asyncio.sleep(9)
        expr = RENAME_JS % json.dumps(pairs, ensure_ascii=False)
        r = await send("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        res = r.get("result", {}).get("result", {})
        print(json.dumps(res.get("value", res), ensure_ascii=False, indent=1))


def main():
    route = sys.argv[1]
    pairs = [a.split("=", 1) for a in sys.argv[2:]]
    p = launch()
    try:
        asyncio.run(go(route, pairs))
    finally:
        p.send_signal(signal.SIGTERM)
        time.sleep(1)
        lock = os.path.join(PROFILE, "SingletonLock")
        if os.path.exists(lock):
            os.remove(lock)


if __name__ == "__main__":
    main()
