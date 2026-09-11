"""cdp_capture.py 용 job 을 파이썬으로 만든다. JS 를 JSON 안에 손으로 이스케이프하지 마라.

    import sys; sys.path.insert(0, "scripts"); import jobkit as J
    J.dump("/tmp/x.json", [dict(name="en-foo.png", url=J.PROD, click_at=[J.at_text(r"/^Rate plan$/")],
                                box_js=J.box_text(r"/^Import$/"))])

at_text   : 텍스트 노드 중심 좌표 {x,y} (click_at / hover_at 용)
box_text  : 그 텍스트를 감싼 버튼/링크 사각형 (box_js 용)
anc_rect  : 텍스트에서 위로 올라가며 조건(cond)을 만족하는 첫 조상의 rect 식
KEBAB_*   : 상품 요금정보 탭의 ⋮ 버튼 (Collapse all 오른쪽, 텍스트 없는 버튼)
HIDE_DEV  : dev 의 DEVELOPMENT 배지 숨김 / BLUR_ROOMS : 판매관리 객실명 열 블러
HIDE_TOOLTIP : 다이얼로그가 ? 아이콘에 자동 포커스를 줘서 뜨는 툴팁 숨김(호버로는 안 닫힌다)
"""
import json

PROD = 'https://www.vcms.io/accommodations/01JT799TA002T8QJ8KJ48XKKHJ/setting/packages/nightuse'
DEV = "https://development.vcms.io/accommodations/"
CLK = 'button,a,[role=button],[role=menuitem],[role=option]'
DLG = "document.querySelector('[role=dialog]')"


def at_text(rx, scope="document.body", nth=0):
    return ("(()=>{const sc=%s;if(!sc)return null;const w=document.createTreeWalker(sc,NodeFilter.SHOW_TEXT);"
            "let n,k=0;while(n=w.nextNode()){if(%s.test((n.nodeValue||'').trim())){const rg=document.createRange();"
            "rg.selectNodeContents(n);const r=rg.getBoundingClientRect();if(r.width>0){if(k++===%d)"
            "return {x:r.left+r.width/2,y:r.top+r.height/2};}}}return null;})()") % (scope, rx, nth)

def box_text(rx, scope="document.body", nth=0, pad=6, closest=CLK):
    return ("(()=>{const sc=%s;if(!sc)return [];const w=document.createTreeWalker(sc,NodeFilter.SHOW_TEXT);"
            "let n,k=0;while(n=w.nextNode()){if(%s.test((n.nodeValue||'').trim())){const e=n.parentElement.closest('%s')||n.parentElement;"
            "const r=e.getBoundingClientRect();if(r.width>0&&k++===%d)return [[r.left-%d,r.top-%d,r.right+%d,r.bottom+%d]];}}return [];})()"
            ) % (scope, rx, closest, nth, pad, pad, pad, pad)

def anc_rect(rx, scope, cond, xcond="true", nth=0):
    # 텍스트 노드에서 위로 올라가며 cond(r) 를 만족하는 첫 조상의 rect 식
    return ("(()=>{const sc=%s;if(!sc)return null;const w=document.createTreeWalker(sc,NodeFilter.SHOW_TEXT);let n,k=0;"
            "while(n=w.nextNode()){if(%s.test((n.nodeValue||'').trim())){const rg=document.createRange();rg.selectNodeContents(n);"
            "const q=rg.getBoundingClientRect();if(!(q.width>0&&(%s)))continue;if(k++!==%d)continue;let e=n.parentElement;"
            "for(let i=0;i<14&&e;i++){const r=e.getBoundingClientRect();if(%s)return r;e=e.parentElement;}return null;}}return null;})()"
            ) % (scope, rx, xcond.replace("r.", "q."), nth, cond)

KEBAB_AT = "(()=>{const bs=[...document.querySelectorAll('button,a,[role=button]')];const c=bs.find(b=>(b.innerText||'').trim()==='Collapse all');if(!c)return null;const cr=c.getBoundingClientRect();const k=bs.filter(b=>{const r=b.getBoundingClientRect();return !(b.innerText||'').trim()&&r.width>0&&Math.abs((r.top+r.bottom)/2-(cr.top+cr.bottom)/2)<14&&r.left>=cr.right-2;})[0];if(!k)return null;const r=k.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2};})()"
KEBAB_BOX = "(()=>{const bs=[...document.querySelectorAll('button,a,[role=button]')];const c=bs.find(b=>(b.innerText||'').trim()==='Collapse all');if(!c)return [];const cr=c.getBoundingClientRect();const k=bs.filter(b=>{const r=b.getBoundingClientRect();return !(b.innerText||'').trim()&&r.width>0&&Math.abs((r.top+r.bottom)/2-(cr.top+cr.bottom)/2)<14&&r.left>=cr.right-2;})[0];if(!k)return [];const r=k.getBoundingClientRect();return [[r.left-5,r.top-5,r.right+5,r.bottom+5]];})()"
HIDE_DEV = "(()=>{let k=0;const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let t;while(t=w.nextNode()){if((t.nodeValue||'').trim()==='DEVELOPMENT'){let e=t.parentElement;for(let i=0;i<3&&e;i++){const r=e.getBoundingClientRect();if(r.width>90&&r.width<220){e.style.setProperty('visibility','hidden','important');k++;break;}e=e.parentElement;}}}return k;})()"
BLUR_ROOMS = "(()=>{const rs=re=>{const o=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){if(re.test((n.nodeValue||'').trim())){const g=document.createRange();g.selectNodeContents(n);const r=g.getBoundingClientRect();if(r.width>0)o.push(r);}}return o.sort((a,b)=>a.top-b.top);};const a=rs(/^All rooms$/)[0];const s=rs(/^Stop sell$/);if(!a||s.length<2)return [];return [[a.left-10,s[1].top-16,s[0].left-6,innerHeight]];})()"
HIDE_TOOLTIP = "(()=>{const a=document.activeElement;if(a&&a!==document.body)a.blur();let k=0;document.querySelectorAll('[role=tooltip]').forEach(t=>{const w=t.closest('[data-radix-popper-content-wrapper]')||t;w.style.setProperty('display','none','important');k++;});return k;})()"


def dump(path, jobs):
    json.dump(jobs, open(path, "w"), ensure_ascii=False, indent=1)
