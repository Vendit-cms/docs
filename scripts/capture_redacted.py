"""운영 화면을 찍으면서 업장을 특정할 수 있는 것만 가린다.

    ATTACH=1 CDP_PORT=9222 TAB_MATCH=vcms.io python3 scripts/capture_redacted.py <출력.png>

VENDIT HOTEL 로 못 찍는 화면(연결된 채널이 있어야 보이는 것들)을 실제 고객 업장에서
찍을 때 쓴다. **조회만 한다.** 저장, 연결, 연결 해제, 재연결은 절대 누르지 마라.

## 가리는 규칙 세 가지

1. **한글 = 계정 데이터.** UI 언어가 영어인데 한글이 보이면 번역 대상이 아니라 계정이
   소유한 문자열이다. 숙소명, 채널 상품명, 객실 타입명, 기간명. 전부 가린다.
   NFD(분해형 자모)까지 잡아야 한다. 맥이 만든 문자열은 자모로 저장된다.
2. **`만` 은 계정 데이터가 아니다.** 통화 단위 축약이라 가리면 요금값이 사라진다.
   가리기 전에 영어 자릿수로 바꾼다. 순서를 지키지 않으면 1번 규칙이 `+3만` 을 통째로 먹는다.
3. **식별자.** 이메일, 7~14자리 숫자, `661277-758971` 형태의 채널 상품 코드, ULID,
   `Last sync:` 바로 앞의 계정명, password/email 입력칸.

## 여기서 실제로 틀렸던 것들

- 값 정규식만 믿었더니 `thearcohotel` 이 통과했다. 이름을 못 맞히는 계정이 있다.
  그래서 `Last sync:` 앞 텍스트는 내용과 무관하게 계정 식별자로 본다.
- `postprocess` 에 dpr 을 안 넘겨서 블러가 절반 크기로 엉뚱한 데 찍혔다.
- 입력칸 값은 텍스트 노드가 아니라 TreeWalker 가 못 본다. 연결 폼이 저장된 계정으로
  미리 채워져 나와서 `root@vcms.io` 와 비밀번호가 그대로 찍혔다.
- 그렇다고 값 있는 입력칸을 다 가리면 판매관리 그리드가 통째로 뭉개진다(23칸이 날아갔다).
- 모달이 떠 있을 때 뒤에 깔린 요소의 좌표로 블러를 찍으면 모달 위 글씨를 뭉갠다.
  `elementFromPoint` 히트 테스트로 바꿨더니 오버레이가 전부를 덮어서 배경이 통째로
  안 가려졌다. 맞는 방법은 모달의 **불투명 패널** 상자를 찾아 그 부분만 잘라내는 것이다.
  `[role=dialog]` 가 화면 전체 오버레이인 경우가 있어서 그대로 쓰면 안 된다.

찍고 나면 눈으로 확인해라. 규칙이 못 잡는 식별자가 남았을 수 있다.
"""
import asyncio
import base64
import os
import sys

os.environ.setdefault("ATTACH", "1")
os.environ.setdefault("CDP_PORT", "9222")
os.environ.setdefault("TAB_MATCH", "vcms.io")
sys.path.insert(0, "/Users/vendit/projects/vcms-docs/scripts")
import cdp_capture as C  # noqa: E402
import websockets  # noqa: E402

FIX_MAN = (
    # 영어 그리드가 30,000 을 `+3만` 으로 찍는다. 통화별 축약이라 원화 업장이면 영어 UI 에도 한글이 박힌다.
    # 값은 그대로 두고 표기만 영어 자릿수로 되돌린다.
    # 억은 건드리지 마라. 1.3억을 130,000,000 으로 펴면 셀 폭을 넘어서 잘린다(2026-09-14 실측).
    # 축약이 있는 이유가 그것이다. 억은 영어 화면에도 그대로 남는다.
    '(()=>{const fixed=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;'
    'const conv=(s)=>s.replace(/([+\u2212-]?)(\\d+(?:\\.\\d+)?)(\uc5b5|\ub9cc)/g,'
    '(m,sg,num,unit)=>sg+Math.round(parseFloat(num)*(unit==="\uc5b5"?100000000:10000)).toLocaleString("en-US"));'
    'while(n=w.nextNode()){const t=n.nodeValue||"";if(t.indexOf("만")<0)continue;'
    'const c=conv(t);if(c!==t){n.nodeValue=c;fixed.push(c.trim());}}return fixed;})()')

HIDE_INTERNAL = '''(()=>{let n=0;
 // 3단계를 무조건 올라가면 안 된다. 2026-09-14 에 대구 아르코에서 사이드바 nav 전체를 지웠고
 // 그대로 배포됐다(en-channel-*.png 9장). DOM 중첩은 업장마다 다르다.
 // 부모가 "VENDIT only" 말고 아무것도 안 가진 동안만 올라간다. 형제가 있으면 거기서 멈춘다.
 for(const e of document.querySelectorAll("*")){
  if(e.childElementCount)continue;
  if(/^VENDIT only$/.test((e.innerText||"").trim())){
    let t=e;
    while(t.parentElement&&/^VENDIT only$/.test((t.parentElement.innerText||"").trim()))t=t.parentElement;
    t.style.visibility="hidden";n++;}}
 return n;})()'''

FIND = r'''(()=>{
 // UI 언어가 영어인데 한글이 보이면 그건 전부 계정이 소유한 문자열이다.
 // 숙소명, 채널 상품명, 객실 타입명, 기간명 - 번역 대상이 아니라 영어 화면에도 한글로 남는다.
 // NFD(분해형 자모)까지 잡아야 한다. 맥이 만든 문자열은 자모로 저장된다.
 const han=/[가-힣ᄀ-ᇿ㄰-㆏ꥠ-꥿ힰ-퟿]/;
 // `661277-758971` 같은 채널 상품 코드도 업장을 특정한다. 하이픈으로 끊겨서
 // \b\d{7,14}\b 로는 안 걸리니 따로 잡는다.
 const re=/아르코|arco|vendit(?!\s|$)|[\w.+-]+@[\w.-]+|\b\d{5,}-\d{5,}\b|\b\d{7,14}\b|\b01[A-Z0-9]{24}\b/i;
 const out=[],seen=new Set();
 // 모달이 떠 있으면 뒤에 깔린 요소도 레이아웃 박스는 그대로 남는다. 그 좌표로 블러를 찍으면
 // 위에 있는 모달 글씨를 뭉갠다(2026-09-13 실측, 영어 안내문이 반쯤 날아갔다).
 //
 // elementFromPoint 히트 테스트로 바꿨다가 더 크게 틀렸다. 오버레이가 화면 전체를 덮어서
 // 배경이 통째로 "안 보임"이 되고, 숙소명이 그대로 노출됐다. 오버레이는 어둡게만 할 뿐 안 가린다.
 //
 // 맞는 규칙은 하나다: **모달 밖에 있으면서 모달 상자와 겹치는 것만** 건너뛴다.
 // 그건 불투명한 패널 뒤라 어차피 안 보인다. 나머지는 모달 안이든 밖이든 다 가린다.
 // [role=dialog] 가 화면 전체를 덮는 오버레이인 경우가 있다. 그걸 그대로 모달 상자로 쓰면
 // 배경 전체가 "가려짐"으로 판정돼서 숙소명이 안 가려진 채 나간다(2026-09-13 실측).
 // 실제로 글씨를 가리는 건 그 안의 불투명 패널이다. 그놈을 찾는다.
 const opaquePanel=(root)=>{
   let best=null;
   for(const e of (root||document).querySelectorAll("*")){
     const s=getComputedStyle(e);
     const m=/^rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)$/.exec(s.backgroundColor||"");
     if(!m)continue;
     const alpha=m[4]===undefined?1:parseFloat(m[4]);
     if(alpha<0.9)continue;                       // 딤 오버레이 제외
     const r=e.getBoundingClientRect();
     if(r.width<200||r.height<150)continue;
     if(r.width>innerWidth*0.95&&r.height>innerHeight*0.95)continue;
     if(!best||r.width*r.height>best.width*best.height)best=r;}
   return best;};
 const modal=(()=>{
   const d=document.querySelector("[role=dialog],dialog[open]");
   if(!d)return null;
   const r=d.getBoundingClientRect();
   if(r.width>innerWidth*0.95&&r.height>innerHeight*0.95)return opaquePanel(d);
   return r;})();
 // 배경 행은 모달보다 넓은 경우가 흔하다. "완전히 가려졌나"로 판정하면 그런 행은 그대로 통과해서
 // 모달 위 글씨를 뭉갠다(2026-09-13 실측, 노란 안내문이 두 번 날아갔다).
 // 건너뛰지 말고 모달 상자와 겹치는 부분만 잘라낸다. 남은 조각만 가린다.
 const clipOut=(r,m)=>{
   if(r.right<=m.left||r.left>=m.right||r.bottom<=m.top||r.top>=m.bottom)return [r];
   const parts=[];
   if(r.top<m.top)parts.push({left:r.left,right:r.right,top:r.top,bottom:m.top});
   if(r.bottom>m.bottom)parts.push({left:r.left,right:r.right,top:m.bottom,bottom:r.bottom});
   const bt=Math.max(r.top,m.top),bb=Math.min(r.bottom,m.bottom);
   if(r.left<m.left)parts.push({left:r.left,right:m.left,top:bt,bottom:bb});
   if(r.right>m.right)parts.push({left:m.right,right:r.right,top:bt,bottom:bb});
   return parts.filter(p=>p.right-p.left>3&&p.bottom-p.top>3);};
 const emit=(r,why)=>{const k=[r.left,r.top,r.right,r.bottom].join();if(seen.has(k))return;
   seen.add(k);out.push([Math.round(r.left-4),Math.round(r.top-2),
                         Math.round(r.right+4),Math.round(r.bottom+2),why]);};
 const push=(r,why,el)=>{
   const inModal=!!(el&&el.closest&&el.closest("[role=dialog],dialog[open]"));
   if(modal&&!inModal){for(const p of clipOut(r,modal))emit(p,why);return;}
   emit(r,why);};
 const clipper=(el)=>{
   // 스크롤 컨테이너 밖으로 밀려난 항목은 화면에 없다. 그런데 레이아웃 박스는 남아서
   // 그 좌표로 블러를 찍으면 뒤에 있는 사이드바 글씨를 뭉갠다(2026-09-14 실측).
   let p=el&&el.parentElement;
   while(p&&p!==document.body){
     const s=getComputedStyle(p);
     if(/(auto|scroll|hidden)/.test(s.overflowY+s.overflowX)&&
        (p.scrollHeight>p.clientHeight+2||p.scrollWidth>p.clientWidth+2))return p.getBoundingClientRect();
     p=p.parentElement;}
   return null;};
 const onscreen=(r,el)=>{
   const c=clipper(el);
   if(!c)return true;
   return !(r.bottom<=c.top||r.top>=c.bottom||r.right<=c.left||r.left>=c.right);};
 const rect=(n)=>{const g=document.createRange();g.selectNodeContents(n);
                  return g.getBoundingClientRect();};
 const vis=(p)=>{const s=getComputedStyle(p);
   return s.visibility!=="hidden"&&s.display!=="none"&&s.opacity!=="0";};
 const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
 let n;const texts=[];
 while(n=w.nextNode()){const t=(n.nodeValue||"").trim();if(!t)continue;
   const p=n.parentElement;if(!p||!vis(p))continue;texts.push([n,t]);}
 for(let i=0;i<texts.length;i++){
   const [node,t]=texts[i];
   if(re.test(t)||han.test(t)){const r=rect(node);
     if(r.width>3&&r.height>3&&onscreen(r,node.parentElement))push(r,t.slice(0,32),node.parentElement);continue;}
   if(/^Last sync/.test(t)&&i>0){const [pn,pt]=texts[i-1];const r=rect(pn);
     if(r.width>3&&r.height>3)push(r,"acct:"+pt.slice(0,32),pn.parentElement);}
 }
 // 입력칸 값은 텍스트 노드가 아니라서 위 TreeWalker 가 못 본다.
 // 연결 폼은 브라우저 프로필에 저장된 계정으로 미리 채워져 나온다(2026-09-13 실측,
 // root@vcms.io 와 비밀번호가 그대로 찍혔다). 값이 든 입력칸은 무조건 가린다.
 // 값이 있다고 다 가리면 안 된다. 판매관리 그리드는 재고/요금 셀이 전부 input 이라
 // 무조건 가리면 화면이 통째로 뭉개진다(2026-09-13 실측, 23칸이 날아갔다).
 // 자격증명과 식별자만 고른다: password/email 타입, 한글이 든 값, 식별자 정규식에 걸리는 값.
 for(const el of document.querySelectorAll("input,textarea")){
   if(el.type==="checkbox"||el.type==="radio")continue;
   const v=el.value||"";
   if(!v)continue;
   const cred=el.type==="password"||el.type==="email";
   if(!cred&&!han.test(v)&&!re.test(v))continue;
   const r=el.getBoundingClientRect();
   if(!vis(el)||r.width<8||r.height<8)continue;
   const safe=!cred&&!re.test(v);
   push(r,"input["+(el.type||"text")+"] "+(safe?v.slice(0,24):"<가림>"),el);
 }
 // 예약 목록의 Guest name 칸은 로마자 이름이라 위 규칙 어디에도 안 걸린다.
 // 2026-09-14 에 투숙객 이름 하나가 그대로 공개 문서에 나갔다. 열을 통째로 가린다.
 const guestHdr=[...document.querySelectorAll("th,[role=columnheader]")]
   .find(h=>/^(Guest name|\uc608\uc57d\uc790)/.test((h.innerText||"").trim()));
 if(guestHdr){
   const hr=guestHdr.getBoundingClientRect();
   if(hr.width>8){
     for(const cell of document.querySelectorAll("td,[role=cell],[role=gridcell]")){
       const cr=cell.getBoundingClientRect();
       if(cr.width<8||cr.height<8)continue;
       if(cr.left>=hr.right-2||cr.right<=hr.left+2)continue;
       if(cr.top<hr.bottom-2)continue;
       if(!(cell.innerText||"").trim())continue;
       if(!onscreen(cr,cell))continue;
       push(cr,"guest-col",cell);}}}
 return out;})()'''


SETTLE = ('(()=>[document.body.innerText.length,'
          'document.querySelectorAll("*").length])()')


async def settle(cdp, tries=25, gap=0.4):
    """DOM 이 멈출 때까지 기다린다.

    이게 없으면 블러 좌표를 덜 그려진 화면에서 계산하고, 그 다음 순간 렌더된 글씨가
    그대로 찍힌다. 2026-09-14 에 실제로 났다. 객실 타입명 4개와 ULID 4개가
    안 가려진 채 나왔고 블러는 1건만 잡혔다. 찍기 직전에 한 번 더 재는 게 아니라
    **멈춘 걸 확인하고** 재야 한다.
    """
    prev = None
    for _ in range(tries):
        cur = await cdp.js(SETTLE)
        if cur == prev:
            return cur
        prev = cur
        await asyncio.sleep(gap)
    return prev

async def main():

    out_path = sys.argv[1]
    do_blur = "--no-blur" not in sys.argv
    async with websockets.connect(C.page_ws(), max_size=None) as ws:
        cdp = C.CDP(ws)
        await cdp.send("Page.enable")
        await cdp.send("Runtime.enable")
        await cdp.send("Page.bringToFront")
        await asyncio.sleep(2.5)
        await settle(cdp)
        hidden = await cdp.js(HIDE_INTERNAL)
        # `만` 은 계정 데이터가 아니라 통화 단위 축약이다. 가리면 요금값이 사라지니
        # 가리기 전에 영어 자릿수로 바꿔놓는다. 안 바꾸면 아래 한글 규칙이 `+3만` 을 통째로 먹는다.
        fixed = await cdp.js(C.__dict__.get("FIX_MAN_UNIT") or FIX_MAN)
        dpr = await cdp.js("window.devicePixelRatio")
        sens = await cdp.js(FIND) if do_blur else []
        print(f"URL: {await cdp.js('location.href')}")
        print(f"내부 메뉴 숨김 {hidden}개 · 만→숫자 {len(fixed or [])}건 "
              f"· dpr {dpr} · 블러 {len(sens or [])}건")
        for s in (sens or []):
            print("   가림:", s[4])
        raw = base64.b64decode((await cdp.send("Page.captureScreenshot", format="png"))["data"])
        img = C.postprocess(raw, [s[:4] for s in (sens or [])], None, dpr)
        open(out_path, "wb").write(img)
        print("saved:", out_path, len(img), "bytes")


if __name__ == "__main__":
    # import 로 불러다 쓰는 파일이다. 가드 없이 두면 run.py 가 import 하는 순간
    # 여기 main() 이 돌면서 sys.argv[1] (시나리오 json) 을 PNG 로 덮어쓴다. 실제로 덮었다.
    asyncio.run(main())
