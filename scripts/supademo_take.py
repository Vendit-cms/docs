#!/usr/bin/env python3
"""Supademo 데모를 크롬 익스텐션 + CDP 로 직접 촬영하는 하네스.

2026-09-12 에 실제로 두 편을 찍어서 검증한 절차다. 한국어 원본 데모를
영어 UI 로 다시 찍을 때 이 파일의 조각들을 그대로 쓴다.

## 먼저 알아야 할 것

- **익스텐션 녹화 패널은 페이지 로드당 한 번만 열린다.** 모든 테이크는 `Page.reload` 로 시작해야 한다.
- **탭이 백그라운드면 판매관리 그리드가 렌더되지 않는다**(`content-visibility:auto`).
  스크립트마다 `Page.bringToFront` 를 넣고 3초쯤 기다려라. 안 그러면 셀 좌표를 못 찾는다.
- CDP 로 보낸 키/마우스는 신뢰된 이벤트라 익스텐션에 그대로 전달된다.
  녹화 토글은 `⌘⇧8` = `Input.dispatchKeyEvent(key="8", code="Digit8", vk=56, modifiers=12)`.
- 익스텐션은 클릭마다 스크린샷 스텝을, 드래그 구간은 mp4 비디오 스텝을 만든다.
- 워크스페이스 기본 **인트로 챕터**가 1번 스텝으로 따라붙는다. 찍고 나서 `delete_steps` 로 지운다.
  (아웃트로 Tally 설문은 2026-09-12 에 Dean 이 워크스페이스 기본값에서 껐다.)
- AI Enhancement 가 영어 핫스팟 문구를 자동으로 붙인다. 그대로 두지 말고
  기존 데모의 영어 번역 문구로 교체해라. `scripts/demo_glossary_check.py` 의 `texts()` 로 긁을 수 있다.

## 운영 서버 경계

`www.vcms.io` VENDIT HOTEL 만 허용. **상단 바의 확정 `Save` 는 누르지 않는다.**
자동 모드 분류기가 막기도 하고, 데모에도 필요 없다 - 마지막 핫스팟은 "Save 를 누르세요" 안내라
그 버튼이 화면에 있으면 충분하다. 모달 안 `Save` 는 임시 변경이라 통과된다.
테이크가 끝나면 `Shift+Esc` 로 임시 변경을 버리고, 새로고침해서 `pending` 이 비었는지 확인해라.

## 화면 정리

`HIDE_ADJ_ROW` 는 Adjustment 행을 통째로 숨긴다. 영어 UI 가 50,000 을 `+5만` 으로 찍는
i18n 버그가 있어서, 그 행이 주제가 아닌 데모에서는 숨기고 찍어야 한글이 안 박힌다.
`HIDE_INTERNAL` 은 직원 계정에만 보이는 사이드바 `VENDIT only` 를 숨긴다.
찍기 직전에 `KOREAN_LEFT` 로 화면에 한글이 남았는지 반드시 확인해라.
"""
import asyncio
import json
import os
import sys

os.environ.setdefault("ATTACH", "1")
os.environ.setdefault("CDP_PORT", "9222")
os.environ.setdefault("TAB_MATCH", "www.vcms.io")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cdp_capture as C  # noqa: E402

# ---------------------------------------------------------------- 화면 정리

HIDE_ADJ_ROW = (
    '(()=>{'
    'const labels=[...document.querySelectorAll("*")].filter(e=>e.childElementCount===0&&'
    '/^Adjustment/.test((e.innerText||"").trim()));'
    'if(!labels.length)return 0;'
    'const bands=labels.map(L=>{const r=L.getBoundingClientRect();return (r.top+r.bottom)/2;});'
    'const hits=[];'
    'for(const el of document.querySelectorAll("div")){const p=el.parentElement;if(!p)continue;'
    ' if(!/flex-col/.test((p.className||"").toString()))continue;'
    ' const r=el.getBoundingClientRect();'
    ' if(r.height<20||r.height>60||r.width<40)continue;'
    ' const cy=(r.top+r.bottom)/2;'
    ' if(bands.some(b=>Math.abs(cy-b)<14))hits.push(el);}'
    'hits.forEach(e=>e.style.setProperty("display","none","important"));return hits.length;})()')

HIDE_INTERNAL = (
    "(()=>{let k=0;const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let t;"
    "while(t=w.nextNode()){if(/^(VENDIT 전용|VENDIT only)$/.test((t.nodeValue||'').trim())){"
    "let e=t.parentElement;for(let i=0;i<4&&e;i++){const r=e.getBoundingClientRect();"
    "if(r.height>24&&r.width<280){e.style.setProperty('visibility','hidden','important');k++;break;}"
    "e=e.parentElement;}}}return k;})()")

KOREAN_LEFT = (
    '(()=>{const bad=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;'
    'while(n=w.nextNode()){const t=(n.nodeValue||"").trim();if(!t||!/[가-힣]/.test(t))continue;'
    'const g=document.createRange();g.selectNodeContents(n);const r=g.getBoundingClientRect();'
    'if(r.width>0&&r.bottom>0&&r.top<innerHeight)bad.push(t);}return [...new Set(bad)];})()')

# ---------------------------------------------------------------- 좌표 찾기

TODAY = ('(()=>{const b=[...document.querySelectorAll("button")].find(e=>(e.innerText||"").trim()==="Today");'
         'if(!b)return null;const r=b.getBoundingClientRect();'
         'return {x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)};})()')

HEADING = ('(()=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;'
           'while(n=w.nextNode()){if((n.nodeValue||"").trim()!=="Distribution")continue;'
           'const g=document.createRange();g.selectNodeContents(n);const r=g.getBoundingClientRect();'
           'if(r.width>0&&r.top<90)return {x:Math.round((r.left+r.right)/2),y:Math.round((r.top+r.bottom)/2)};}'
           'return null;})()')

PENDING_BAR = ('(()=>{const o=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;'
               'while(n=w.nextNode()){const t=(n.nodeValue||"").trim();if(!t)continue;'
               'const g=document.createRange();g.selectNodeContents(n);const r=g.getBoundingClientRect();'
               'if(r.width>0&&r.top<120&&/temporary change|^Save$|^Cancel$/i.test(t))'
               'o.push([t,Math.round((r.left+r.right)/2),Math.round((r.top+r.bottom)/2)]);}return o;})()')


def row_cells(label):
    """판매관리 그리드에서 한 행의 날짜별 셀 좌표. label 예: "Availability", "Check-in/out"."""
    return ('(()=>{const tx=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;'
            'while(n=w.nextNode()){const t=(n.nodeValue||"").trim();if(!t)continue;'
            'const g=document.createRange();g.selectNodeContents(n);const r=g.getBoundingClientRect();'
            'if(r.width>0)tx.push([t,r]);}'
            f'const h=tx.find(([t])=>t==="{label}");if(!h)return null;'
            'const cy=(h[1].top+h[1].bottom)/2;'
            'return tx.filter(([t,r])=>Math.abs((r.top+r.bottom)/2-cy)<16&&r.left>h[1].right)'
            '.sort((a,b)=>a[1].left-b[1].left)'
            '.map(([t,r])=>({t:t,l:Math.round(r.left),t0:Math.round(r.top),'
            'x:Math.round((r.left+r.right)/2),y:Math.round((r.top+r.bottom)/2)}));})()')


INPUT_CELLS = ('(()=>{const tx=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;'
               'while(n=w.nextNode()){if((n.nodeValue||"").trim()!=="Availability")continue;'
               'const g=document.createRange();g.selectNodeContents(n);const r=g.getBoundingClientRect();'
               'if(r.width>0)tx.push(r);}if(!tx.length)return null;const cy=(tx[0].top+tx[0].bottom)/2;'
               'return [...document.querySelectorAll("input")].map(e=>{const p=e.closest(".rt-TextFieldRoot")||e;'
               'const r=p.getBoundingClientRect();return {l:Math.round(r.left),t:Math.round(r.top),'
               'w:Math.round(r.width),h:Math.round(r.height),v:e.value};})'
               '.filter(p=>Math.abs(p.t+p.h/2-cy)<14&&p.w>40);})()')

MODAL_TEXT = ('(()=>{const all=[...document.querySelectorAll("*")];'
              'const a=all.find(e=>e.childElementCount<=2&&new RegExp("^"+TITLE+"$").test((e.innerText||"").trim()));'
              'if(!a)return null;let b=a;for(let i=0;i<10&&b;i++){const r=b.getBoundingClientRect();'
              'if(r.width>400&&r.height>300)break;b=b.parentElement;}'
              'const out=[];const w=document.createTreeWalker(b,NodeFilter.SHOW_TEXT);let n;'
              'while(n=w.nextNode()){const t=(n.nodeValue||"").trim();if(!t)continue;'
              'const g=document.createRange();g.selectNodeContents(n);const r=g.getBoundingClientRect();'
              'if(r.width>0)out.push([t.slice(0,60),Math.round((r.left+r.right)/2),Math.round((r.top+r.bottom)/2)]);}'
              'return out;})()')


def modal_text(title_regex):
    """모달 안의 텍스트와 좌표. `[role=dialog]` 은 이 앱에서 못 믿는다 - 제목을 앵커로 잡는다."""
    return "const TITLE=" + json.dumps(title_regex) + ";" + MODAL_TEXT


# react-select 드롭다운은 현재 값 근처로 스크롤된 채 열린다.
# 옵션 24개가 전부 DOM 에 있지만 화면 밖이면 클릭이 안 먹으니 먼저 스크롤해라.
def scroll_option_into_view(value):
    return ('(()=>{const lb=document.querySelector("[role=listbox]");if(!lb)return -1;'
            'const o=[...lb.querySelectorAll("[role=option]")].find(e=>(e.innerText||"").trim()==='
            + json.dumps(value) + ');'
            'if(!o)return -2;o.scrollIntoView({block:"center"});return lb.scrollTop;})()')


def find_option(value):
    return ('(()=>{const lb=document.querySelector("[role=listbox]");if(!lb)return null;'
            'const o=[...lb.querySelectorAll("[role=option]")].find(e=>(e.innerText||"").trim()==='
            + json.dumps(value) + ');'
            'if(!o)return null;const r=o.getBoundingClientRect();'
            'return {x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)};})()')


def shadow_button(rx):
    """익스텐션 UI 는 `SUPADEMO-UI` 의 열린 shadow root 안에 있다. 라이트 DOM 에는 아무것도 없다."""
    return ('(()=>{const hs=[...document.querySelectorAll("*")].filter(e=>e.shadowRoot);'
            'for(const h of hs){for(const b of h.shadowRoot.querySelectorAll("button")){'
            'const t=(b.innerText||"").replace(/\\s+/g," ").trim();'
            f'if(!/{rx}/i.test(t))continue;const r=b.getBoundingClientRect();if(r.width<10)continue;'
            'return {x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2),txt:t.slice(0,24)};}}'
            'return null;})()')


# ---------------------------------------------------------------- 입력

async def click(cdp, x, y, label="", wait=1.6):
    if label:
        print(f"    click {label} ({x},{y})")
    await cdp.send("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y, buttons=0)
    await asyncio.sleep(0.35)
    for t in ("mousePressed", "mouseReleased"):
        await cdp.send("Input.dispatchMouseEvent", type=t, x=x, y=y,
                       button="left", buttons=1, clickCount=1)
        await asyncio.sleep(0.08)
    await asyncio.sleep(wait)


async def key(cdp, k, code, vk, mods=0):
    for t in ("rawKeyDown", "keyUp"):
        await cdp.send("Input.dispatchKeyEvent", type=t, key=k, code=code,
                       windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk, modifiers=mods)
        await asyncio.sleep(0.08)


async def type_into(cdp, x, y, text, label=""):
    """셀을 눌러 전체 선택한 뒤 값을 바꾼다."""
    await click(cdp, x, y, label or "cell", 0.8)
    await cdp.send("Input.dispatchKeyEvent", type="keyDown", key="a", code="KeyA",
                   windowsVirtualKeyCode=65, nativeVirtualKeyCode=65, modifiers=4)
    await cdp.send("Input.dispatchKeyEvent", type="keyUp", key="a", code="KeyA",
                   windowsVirtualKeyCode=65, nativeVirtualKeyCode=65, modifiers=4)
    await asyncio.sleep(0.3)
    await cdp.send("Input.insertText", text=text)
    await asyncio.sleep(1.2)


async def drag(cdp, x0, y0, x1, y1, steps=14):
    """셀 우하단 손잡이를 잡아 오른쪽으로 끌어 값을 전파한다. 익스텐션이 이 구간을 mp4 로 만든다."""
    await cdp.send("Input.dispatchMouseEvent", type="mouseMoved", x=x0, y=y0, buttons=0)
    await asyncio.sleep(0.5)
    await cdp.send("Input.dispatchMouseEvent", type="mousePressed", x=x0, y=y0,
                   button="left", buttons=1, clickCount=1)
    await asyncio.sleep(0.3)
    for i in range(1, steps + 1):
        await cdp.send("Input.dispatchMouseEvent", type="mouseMoved",
                       x=x0 + round((x1 - x0) * i / steps), y=y0 + round((y1 - y0) * i / steps),
                       button="left", buttons=1)
        await asyncio.sleep(0.09)
    await asyncio.sleep(0.4)
    await cdp.send("Input.dispatchMouseEvent", type="mouseReleased", x=x1, y=y1,
                   button="left", buttons=1, clickCount=1)
    await asyncio.sleep(1.5)


# ---------------------------------------------------------------- 테이크 골격

async def prepare(cdp, click_today=True, wait=13.0):
    """새로고침하고 화면을 정리한다. 한글이 남아 있으면 False."""
    await cdp.send("Page.bringToFront"); await asyncio.sleep(0.5)
    await cdp.send("Page.reload"); await asyncio.sleep(wait)
    await cdp.send("Page.bringToFront"); await asyncio.sleep(3.0)
    if click_today:
        t = await cdp.js(TODAY)
        if t:
            await click(cdp, t["x"], t["y"], "Today", 3.0)
    return await tidy(cdp)


async def tidy(cdp):
    a = await cdp.js(HIDE_ADJ_ROW)
    b = await cdp.js(HIDE_INTERNAL)
    left = await cdp.js(KOREAN_LEFT)
    print(f"  tidy adj={a} internal={b} korean={json.dumps(left, ensure_ascii=False)}")
    return not left


async def start_recording(cdp):
    """⌘⇧8 -> Start Recording -> Get started. 창이 리사이즈되니 이후 좌표는 다시 따야 한다."""
    await key(cdp, "8", "Digit8", 56, 12)
    await asyncio.sleep(4)
    st = await cdp.js(shadow_button("Start Recording"))
    if not st:
        print("  !! 녹화 패널이 안 떴다. 페이지를 새로고침하고 다시 시도해라.")
        return False
    await click(cdp, st["x"], st["y"], "Start Recording", 4.0)
    gs = await cdp.js(shadow_button("^Get started$"))
    if gs:
        await click(cdp, gs["x"], gs["y"], "Get started", 5.0)
    await tidy(cdp)
    return True


async def stop_recording(cdp, settle=15.0):
    stop = await cdp.js(shadow_button("Stop|Finish|Done|End recording|Complete"))
    if stop:
        await click(cdp, stop["x"], stop["y"], "Stop", 1.0)
    else:
        await key(cdp, "8", "Digit8", 56, 12)
    await asyncio.sleep(settle)


async def discard_changes(cdp):
    """Shift+Esc 로 임시 변경을 버리고, 새로고침해서 실제로 비었는지 확인한다."""
    await key(cdp, "Escape", "Escape", 27, 8)
    await asyncio.sleep(2.5)
    await cdp.send("Page.reload"); await asyncio.sleep(13)
    await cdp.send("Page.bringToFront"); await asyncio.sleep(3.0)
    bar = await cdp.js(PENDING_BAR)
    print("  pending after discard:", json.dumps(bar, ensure_ascii=False))
    return not bar


def connect():
    """`async with connect() as ws:` 로 쓰고 `C.CDP(ws)` 를 만들어라."""
    import websockets
    return websockets.connect(C.page_ws(), max_size=None)
