#!/usr/bin/env python3
"""캡처 프로필로 페이지를 열고 JS 를 실행해 결과를 찍는다. 라우트나 셀렉터를 확인할 때 쓴다.

    python3 scripts/cdp_eval.py <url> '<js expression>' [대기초]
"""
import asyncio, json, os, signal, subprocess, sys, time, urllib.request
import websockets  # type: ignore

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE = os.path.expanduser(os.environ.get("VCMS_CAPTURE_PROFILE", "~/.vcms-capture-profile"))
PORT = int(os.environ.get("CDP_PORT", "9334"))


def launch():
    lock = os.path.join(PROFILE, "SingletonLock")
    if os.path.exists(lock):
        os.remove(lock)
    p = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
         f"--user-data-dir={PROFILE}", f"--remote-debugging-port={PORT}",
         "--window-size=1440,900", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1)
            return p
        except Exception:
            time.sleep(0.5)
    raise SystemExit("디버깅 포트 안 열림")


async def go(url, expr, wait):
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
        await send("Page.navigate", url=url)
        await asyncio.sleep(wait)
        r = await send("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        res = r.get("result", {}).get("result", {})
        print(json.dumps(res.get("value", res), ensure_ascii=False, indent=1))


def main():
    url, expr = sys.argv[1], sys.argv[2]
    wait = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
    p = launch()
    try:
        asyncio.run(go(url, expr, wait))
    finally:
        p.send_signal(signal.SIGTERM)
        time.sleep(1)
        lock = os.path.join(PROFILE, "SingletonLock")
        if os.path.exists(lock):
            os.remove(lock)


if __name__ == "__main__":
    main()
