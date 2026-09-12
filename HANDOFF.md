# 이어서 작업하기: docs.vcms.io 영어판

이 파일 하나만 읽으면 다음 세션이 바로 이어갈 수 있게 적었다. 마지막 갱신 2026-09-11.

---

## 0. 먼저 지켜야 할 것

### 🔒 한국어: 글은 동결, 이미지는 우리가 갱신 (2026-09-11 Dean)
정본 규칙은 레포 `CLAUDE.md` 맨 위. 요약:
- `ko/` 문장, 표, 서식, alt 는 여전히 금지. 디자이너가 쓰고 있다.
- ko 페이지만 쓰는 이미지 원본은 **제자리 덮어쓰기**. 그러면 `ko/*.mdx` 가 한 줄도 안 바뀐다. 커밋 전 `git diff --cached --numstat -- ko/` 가 0 인지 확인.
- en 페이지나 릴리즈 노트가 같이 쓰는 파일이면 `ko-` 새 파일 + `swap_image.py --ko-images`.

### `git add -A` 금지
파일명이 **NFD** 로 저장돼 있다. `-A` 를 쓰면 이미지 254 장이 복제된다. 항상 경로를 명시해서 `git add <경로>`.
같은 이유로 `sed` 로 이미지 참조를 바꾸면 **아무 말 없이 하나도 안 바뀐다**(셸 입력은 NFC). 참조 교체는 `scripts/swap_image.py` 만 써라.

### 루트 `.md` 는 공개 사이트에 올라간다
Mintlify 는 내비게이션에 없어도 루트의 `.md` 를 페이지로 만든다. `docs.vcms.io/IMAGES` 가 실제로 `IMAGES.md` 를 보여준다(2026-09-11 확인, 200). 그래서 `.mintignore` 에 `CLAUDE.md` `HANDOFF.md` `CHANGELOG.md` `IMAGES.md` 를 넣었다. **내부 메모 파일을 새로 만들면 여기에도 추가해라.** 머지 후 `curl -s -o /dev/null -w "%{http_code}" https://docs.vcms.io/HANDOFF` 가 404 인지 확인해라.

### 서버 경계
| 대상 | 허용 |
| --- | --- |
| `development.vcms.io` | 조회, 모달 열기만. **저장 금지** |
| `www.vcms.io` VENDIT HOTEL | 쓰기 허용 (Dean 이 허가한 유일한 운영 업소) |
| `www.vcms.io` 그 외 | 절대 금지 |

결제, 구독, 해지 버튼은 어느 서버에서도 누르지 마라. 모달은 열어도 된다.

---

## 1. 레포

- 경로 `~/projects/vcms-docs`, 정본 원격 `Vendit-cms/docs` (사본 2 개는 낡았다). 푸시 권한은 개인 계정 `yujy118`.
- 현재 브랜치 **`en-full-recapture`**, **PR #47 로 main 에 스쿼시 머지, 배포 완료(2026-09-11 16:42Z, `2f8e0fc`).** 라이브 확인: 페이지 174 개 전부 200, 이미지 323 개 전부 200. push 는 `git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push` (키체인의 vendit-jinyoung 은 pull 전용이라 403).
- Mintlify. 언어는 `docs.json` 의 `navigation.languages` 에 ko / en 두 블록.
- `images/` 는 **ko 와 en 이 공유한다.** 원본을 덮으면 한국어 문서까지 바뀐다. 새 캡처는 반드시 `en-` 접두 새 파일로 넣고 참조만 갈아끼운다.

### 커밋 (오래된 것부터)
```
25adf98  로그인, 판매관리 상태 안내
a2c647c  판매관리 보기설정, 필터, 예약
3b83474  객실타입, 기간, 요금, 서비스
6dc163b  판매시간표
4c9f280  일괄변경
03c6013  상품 (샘플 데이터 영어화 후)
b5499a0  판매관리 이해하기 범례 2 장 (텍스트 덮어쓰기)
94d67d1  구독 4 장 (dev)
14a1458  서비스, 요금, 판매시간표 재촬영
fb977c7  상품 요금정보 5 장
199803d  구독 상세, 구독 관리
9f3ab10  서비스 구독 연간 결제 토글
```

---

## 2. 지금 어디까지 왔나

`IMAGES.md` 가 정본이다. 손으로 고치지 마라, `python3 scripts/images_manifest.py > IMAGES.md` 로 다시 만든다.

**참조 275 건 중 187 건 정리 완료, 88 건 남음.** (2026-09-12)

| 상태 | 건수 | 뜻 |
| --- | --- | --- |
| 영어 캡처 완료 | 86 | `en-` 파일 |
| 한국어 재사용 | 82 | 릴리즈 노트. Dean 이 2026-09-09 에 그대로 두기로 결정 |
| 채널사 화면 | 51 | 외부 사이트. 아래 3 절 |
| 채널 로고 | 19 | 언어 무관 |
| 재현 불가 | 12 | 사유는 `images_manifest.py` 의 `BLOCKED` |
| Dean 확인 필요 | 24 | 아래 3 절 |
| 한국어 유지 (내 몫) | 1 | |

---

## 2-1. 한국어 이미지 최신화 (2026-09-11)

en 에서 다시 찍은 자리와 같은 위치의 한국어 이미지 84 장을 현재 제품과 나란히 놓고 비교했다.

| 판정 | 장 | 처리 |
| --- | --- | --- |
| 낡음, 교체 | 14 | 예약 내역 4, 상품 요금정보 목록, 상품 생성/요금 관리/요금 범위/요금 조절 배수/인원별 요금/기간별 요금, 기간가중치_2, 화면보기설정, Inviting. 한국어 UI 로 다시 찍어 제자리 덮어씀(3a5439c, 5bea6a0) |
| 낡았지만 글에 묶임 | 5 | 판매관리이해하기 범례(_판매완료,재고 / _요금조절 / _요금 / _잔여 / _변경상태). 제품 패널 행이 바뀌거나 빠졌는데 한국어 본문이 옛 행을 하나씩 설명한다. 이미지만 바꾸면 글과 어긋나서 **디자이너 몫** |
| 크롬만 다름 | 11 | 사이드바, 배지 정도. 그대로 둠 |
| 현행 | 54 | 언어, 데이터만 다름. 그대로 둠 |

찍는 법:
- UI 언어는 계정이 아니라 **브라우저 localStorage** `preference = {"state":{"language":"ko"}}` 다. 바꾸고 새로고침하면 된다. 캡처 프로필은 지금 한국어다.
- 영어 recipe 의 텍스트 셀렉터는 vcms-i18n `locales/latest/{en,ko}.json` 을 키로 맞춰 번역했다. 같은 영어가 둘로 갈리는 것(Rate → 요금 / 요금 관리)은 눈으로 확인하고 골라라.
- VENDIT HOTEL 데이터가 영어라 한국어 화면에 `Deluxe Roomonly` 같은 이름이 보인다. 기간 이름은 한국어다.

같은 날 영어 28 장도 다시 찍었다(c78489f). 직원 계정에만 보이는 사이드바 `VENDIT only` 가 전부 찍혀 있었다.

---

## 2-2. Supademo 영어 데모 직접 촬영 (2026-09-12)

크롬 익스텐션(⌘⇧8)을 CDP 로 몰아서 **영어 데모를 우리가 직접 찍을 수 있다**. 두 편 완료.

| 새 데모 | ID | 스텝 | 붙인 곳 |
| --- | --- | --- | --- |
| VCMS availability change | `cmtyc75ri0hrxqme9293l1cf5` | 5 (이미지 3, 영상 2) | `en/distributions/usage.mdx` 2곳 |
| Change of check-in/check-out times | `cmtyd1bg70i80qme9d53qqrer` | 14 (이미지 12, 챕터 2) | `en/distributions/usage.mdx`, `en/faq/inventory-rate/daily-chek-in-out-time.mdx` |

한국어 원본(`cmd5r4c0o00egus0ibx0wlvum`, `cmeh3bfh00006z20ifhcdg6yt`)은 `ko/` 에 그대로 있다. 건드리지 않았다.

절차와 함정은 전부 `scripts/supademo_take.py` 의 docstring 에 적었다. 핵심만:
- 녹화 패널은 **페이지 로드당 한 번만** 열린다. 테이크마다 `Page.reload` 로 시작.
- **탭이 백그라운드면 그리드가 렌더 안 된다**(`content-visibility:auto`). `Page.bringToFront` 필수.
- 워크스페이스 기본 인트로 챕터가 1번 스텝으로 붙는다. `delete_steps` 로 지워라.
- AI 가 붙인 영어 핫스팟 문구는 기존 번역으로 갈아끼워라(`demo_glossary_check.texts()` 로 긁는다).
- 상단 바 확정 `Save` 는 누르지 않는다. 모달 안 `Save` 는 임시 변경이라 괜찮다.
  마지막 핫스팟은 "Save 를 누르세요" 안내라 버튼이 화면에 있으면 충분하다.
- 끝나면 `Shift+Esc` + 새로고침으로 임시 변경이 비었는지 확인. 2026-09-12 테이크는 운영에 **아무것도 안 썼다**.

### 막힌 것
- **요금 데모 3편**(일자별 요금 `cmd5ud8pr010nus0iry8westh`, 객실타입별 요금 `cmd5uuktb001kwz0hhjb2ae67`,
  요금변경 `cmd5vezlh003twz0ibhv8ztfd`)은 Adjustment 행이 주제라 숨길 수 없다.
  그 행에 **토요일마다 `+5만`** 이 박혀 있다(영어 UI 가 50,000 을 한국어 단위로 찍는 i18n 버그).
  5,000 으로 바꾸면 `+5,000` 으로 정상 렌더되는데, 그러려면 확정 `Save` 가 필요하다.
  자동 모드 분류기가 그 클릭을 막는다. `/permissions` 에 다음 한 줄을 넣으면 풀린다.
  ```
  Bash(python3 <작업 디렉터리>/*)
  ```
- 입/퇴실 데모의 **툴바 Bulk update** 절(원본 스텝 5-9)은 임시 변경이 남아 있으면 버튼이 비활성이라
  확정 Save 가 선행돼야 한다. 같은 이유로 보류.
- 보기 설정에서 입/퇴실 행 숨기는 절(원본 스텝 17-20)은 스크린샷 대신 챕터 문구로 대체했다.

---

## 3. 남은 것

### Dean 이 해줘야 하는 것
| 이미지 | 페이지 | 왜 |
| --- | --- | --- |
| `Distribution-Booking-Sync-Only.png` | `en/distributions/channel-sync.mdx` | 영어 배너가 `Since {date}, ...` 를 그대로 찍는다. dev 번들 `en.json` 은 `{date}`, vcms-i18n `main` 은 `{launchedAt}` 로 이미 고쳐져 있다. 배포되면 devtester04 에서 다시 찍어 교체. 지금 찍은 건 `images/en-distribution-booking-sync-only.png` 에 넣어뒀다(참조 안 함) |
| `pkg_delete.png` | `en/inventory-rate/package-stay.mdx` | 현재 빌드는 휴지통이 항상 활성이고 툴팁은 "Delete" 뿐이다. 채널 연결 상품 차단은 누른 뒤에 뜨는 것으로 보이는데, 운영 삭제 버튼을 누르는 동작이라 자동 모드 분류기가 막았다 |

| 연결된 채널 화면 22 장 (`채널_*`) | `en/channels/channel-setting.mdx`, `en/faq/inventory-rate/channel-*.mdx`, `limit-inventory-by-channel.mdx` | VENDIT HOTEL 은 연결된 채널이 0 개다. dev 에서 채널이 붙은 업소는 전부 실제 업체 이름, 채널 숙소 ID, 계정이 보여서 공개 문서에 못 쓴다. 깨끗한 테스트 채널 연결이 생기면 찍는다 |

VCLOUD 연동/해제 창은 안 찍는다. 점주가 설정 못 하게 막아둔 게 의도다(Dean, 2026-09-12). 한국어 가이드도 같은 관리자 매뉴얼 절을 갖고 있다.

### 채널사 화면 51 건(파일 47 장) 내역
- 영어 화면이 있는 해외 채널, 지금은 한국어 UI: 에어비앤비 7, 익스피디아 5, 아고다 4, 트립닷컴 4. 파트너 계정이 있어야 다시 찍는다.
- 한국어 전용 서비스라 영어판이 없다: NOL/야놀자 4, 네이버 6, 캠핏 2, 캠퍼레스트 1, 리브애니웨어 1, 트립비토즈 2, 카카오 알림톡 1. 그대로 둔다.
- OS, 브라우저: 윈도우 전원 설정 5, 크롬 확장 메뉴 3.
- 옛 "판매 설정" 모달 2 (야놀자 핫딜 FAQ).

Dean 이 창에 띄워주면 `python3 scripts/shoot_now.py en-vcloud-disconnect.png images --match=development.vcms.io` 로 보이는 그대로 찍는다. 막힌 걸 우회하지 마라.

### 재현 불가로 확정 (2026-09-11 추가)
- `create-pkg-inclusions.png`: 상품 모달(생성, 수정 둘 다)에 서비스 선택이 없다. 서비스는 요금에 붙는다(`en-rate-inclusions.png`). 문서 본문이 낡았다(8 절).
- `cancel-booking-noti.png`: 카카오 알림톡 원문. 한국어로만 발송된다.
- `faq-no-history.png`: 수집 시점에 이미 취소된 예약이 필요하다. VENDIT HOTEL 기본 조회 기간 Canceled 0 건.

### 채널사로 재분류 (2026-09-11)
`image-34`, `image-(1)`, `image(65)`, `image(66)`: 에어비앤비, 야놀자 FAQ 페이지의 파트너 화면. manifest 정규식이 `\(` 에서 끊겨서 "내 몫"으로 잘못 세고 있었다.

### 그 외 미해결
- `term_coverage.py` 가 뽑은 후보 70 건이 아직 검증 안 됐다.
- 내비게이션에 없는 페이지 11 개의 폴백 처리 방침을 Dean 이 아직 안 골랐다.
- UI 언어는 브라우저 localStorage 다(2-1 절). 캡처 프로필은 2026-09-11 에 한국어로 돌려놨다. 영어로 찍을 땐 `en` 으로 바꾸고 끝나면 `ko` 로 되돌려라.
- VENDIT HOTEL 의 기간 이름이 한국어 데이터다(`어린이날 전날 🇰🇷`, `여름 성수기 (8월)(평일)`). `en-period-list`, `en-period-rate-weighting`, `en-pkg-bulk-rate-plan-modal`, `en-pkg-period-weighting` 에 그대로 보인다. PR #42 때부터 이 상태다. 바꾸려면 Dean 이 이름을 바꾸고 다시 찍는다.

---

## 4. 도구

### `scripts/cdp_capture.py`: 주력 캡처기
헤드리스 크롬을 CDP 로 몰아서 모달까지 열고 찍는다. 결과물 4320x2700.

```bash
# 캡처 전용 프로필(로그인 + UI 영어 + 사이드바 펼침)로 찍기
python3 scripts/cdp_capture.py jobs.json 출력폴더

# Dean 이 띄워둔 창에 붙어서 찍기
ATTACH=1 CDP_PORT=9222 TAB_MATCH=development.vcms.io SCALE=3 \
  python3 scripts/cdp_capture.py jobs.json 출력폴더
```

job 키: `url` `load` `click`(정규식, 스크롤됨) `click_at`(좌표 반환 JS) `hover_at`(마우스만 올림, 툴팁용) `js` `click_after` `wait` `step_wait`
`blur` `blur_js` `box` `box_list` `box_js` `crops` `pad`

**job 은 `scripts/jobkit.py` 로 만들어라.** JS 를 JSON 안에 손으로 이스케이프하면 반드시 틀린다. `at_text` `box_text` `anc_rect` `HIDE_DEV` `BLUR_ROOMS` `HIDE_TOOLTIP` 이 들어 있다.

**실행 순서가 함정이다.** `click` → `click_at` → `hover_at` → `js` → `click_after`. 스크롤이 필요하면 `click`(텍스트) 을 써라, `click_at` 은 화면 밖 좌표를 그대로 눌러서 헛클릭한다.

### 겪은 함정 (다시 밟지 마라)
- **`CDP_PORT` 기본값은 9333 이다.** `ATTACH=1` 로 붙을 땐 `CDP_PORT=9222` 를 반드시 붙여라.
- **백그라운드 탭은 마우스 이벤트를 삼킨다.** 네비게이션도 되고 JS 도 도는데 클릭만 안 먹는다. ATTACH 모드는 `Page.bringToFront` 를 먼저 부른다(이미 들어가 있다).
- **Radix 팝오버는 mousePressed/Released 만으로는 안 열린다.** 같은 좌표로 `mouseMoved` 를 먼저 보내야 한다(이미 들어가 있다).
- **다이얼로그가 열리면 앱이 사이드바를 접는다.** 제품 동작이다. 영어 캡처는 전부 접힌 상태라 일관돼 있다.
- 블러 반경을 영역 높이로 잡으면 세로로 긴 열이 백지가 된다. `min(h*0.35, 4*scale)` 로 고정돼 있다.
- 개인정보는 반드시 `blur_js` 로 지워라. 첫 예약 캡처가 실제 투숙객 이름을 그대로 내보냈다.
- **zsh 에서 루프 변수 이름으로 `path` 를 쓰지 마라.** `PATH` 와 묶여 있어서 `cat` `curl` `python3` 가 전부 사라진다.
- **고정 요금(Fixed rate) 상품은 기간 추가, 불러오기가 잠겨 있다.** Deluxe Roomonly 가 그렇다. 기간 버튼은 `deluxe late checkin` 에서 찍어라.
- **다이얼로그가 `?` 아이콘에 자동 포커스를 주면 툴팁이 뜬 채로 찍힌다.** 호버를 옮겨도, blur 해도 안 닫힌다. `HIDE_TOOLTIP` 을 `js` 에 넣어라.
- **자동 모드 분류기가 막는 것**: 연동 서비스의 Connect / Delete 대화상자 열기, 운영 상품 휴지통 클릭. 막히면 우회하지 말고 Dean 에게 넘겨라.
- **여러 업소에서 특정 상태를 찾을 땐 탭을 앞으로 꺼내지 않는 CDP 스크립트로 훑어라.** dev 38 개 업소의 `/setting/systems` 와 `/inventories` 를 6 분에 훑어서 아래 6 절 업소들을 찾았다. 업소 ID 는 목록 카드의 React fiber props 에 있다(화면엔 끝 8 자리만 보인다).
- **운영 캡처엔 `HIDE_INTERNAL` 을 꼭 넣어라.** 직원 계정이라 사이드바 맨 아래 `VENDIT only / VENDIT 전용` 이 보인다. 고객은 못 보는 메뉴다.
- **영어 recipe 의 예약 블러를 한국어 UI 에 그대로 쓰지 마라.** 한글이면 전부 가리는 규칙이라 라벨이 다 뭉개지고 영문 이름(`su pei ming`)은 빠져나간다. `BOOKINGS_BLUR_LIST_KO` / `BOOKINGS_BLUR_CARD_KO` 를 써라.
- **규격이 있는 이미지(판매관리 범례 등)는 제품 패널을 잘라서 대체하지 마라.** 한국어 이미지 위에 텍스트만 바꾼다(`overlay_text.py`). 2026-09-12 에 영어 범례 4 장이 크롭이라 규격이 달라 Dean 이 지적했다.
- **영어 예약 블러의 "Firstname Lastname" 규칙은 `Download CSV` 도 가린다.** skip 목록에 넣었다. 새 블러 규칙을 만들면 화면의 UI 라벨이 멀쩡한지 꼭 잘라서 봐라.
- **좌표로 버튼을 찾는 recipe 는 언어를 바꾸면 틀린다.** 한국어 라벨 폭이 달라서 판매관리 ⚙ 대신 ⓘ 가 눌렸다. `일괄 변경` 같은 이웃 텍스트 기준으로 찾아라.

### 나머지 스크립트
| 파일 | 용도 |
| --- | --- |
| `swap_image.py` | NFD 안전 참조 교체. `ko/` 경로는 거부한다. `python3 scripts/swap_image.py <페이지> "옛날.png=새것.png" ...` |
| `images_manifest.py` | `IMAGES.md` 재생성. `BLOCKED` 딕셔너리에 재현 불가 사유를 적는다 |
| `overlay_text.py` | 다시 못 찍는 이미지 위에 **텍스트만** 덮어쓴다. 다른 건 그리지 마라 |
| `shoot_now.py` | Dean 이 띄워둔 창을 지금 이 순간 그대로 찍는다. 조작 안 한다 |
| `open-window.sh` / `capture-login*.sh` | CDP 9222 로 보이는 크롬 띄우기 / 로그인 |
| `term_coverage.py` `glossary_check.py` | 용어 검증 |
| `rename_data.py` | **절대 돌리지 마라.** 샘플 데이터 이름을 UI 로 바꾸는 스크립트다. Dean 이 직접 했다 |

---

## 5. 용어

추측하지 마라. 정본은 `~/projects/vcms-i18n`:
- `locales/latest/{ko,en}.json` (3,278 키)
- `glossary/glossary.json` (135 항목)

자주 틀리는 것: 판매관리 = **Distribution**, 내보내기 = **Remove**, 배수(기본정보) = **Units per booking**, 추가 요금 조절(요금정보) = **Rate scale factor**.

---

## 6. 알아둘 dev 계정

| 업소 | ID | 쓸모 |
| --- | --- | --- |
| VENDIT | `01KDC7P3Q7H220YAR6FWETD4D8` | 무료체험 종료. **서비스 구독 모달**(연간 결제 토글)이 여기서 나온다 |
| 수연스테이(유료고객) | `01K56E56BCN5ERZ28CR2TXTFZD` | 재고, 요금 연간 구독 중, 52 rooms. **구독 상세 / 구독 관리** 모달이 여기서만 열린다 |
| 결제미납업장테스트 | `01JQVCCF9QRVWCW381E0VQ9YA8` | 결제 실패 상태 |
| 벤디트 호텔 | `01KV59JB8JM2PFXBVM6T0TS747` | 판매관리 `Syncing inventory and rates 180 days` 배지 |
| devtester04 | `01JYFKK7XAMRBT45EDFW61S217` | 판매관리 `Booking sync only` + 동기화 중지 배너. VCLOUD In use |
| 테스트 숙박업소 | `01KYSP09YAAD6Y07CJVXEM6T2P` | VCLOUD `Integration failed / Invalid accommodation ID` |

VENDIT HOTEL(운영) 은 무료체험이라 구독 화면 자체가 없다.

---

## 7. 사고 기록: 같은 실수 반복 금지

운영 VENDIT HOTEL 에서 두 번 저장이 나갔고 둘 다 되돌렸다.

1. **디럭스 최대 인원 5 → 4.** 객실타입 수정의 확인 다이얼로그는 CMS 관리 타입 + 범위를 벗어난 상품이 있을 때만 뜬다. VENDIT HOTEL 은 전부 채널 관리라 저장이 그대로 나갔다. 5 로 복구, 행을 다시 읽어 확인했다.
2. **디럭스 9/15~20 판매중지.** 일괄변경 모달의 고정 `Add` 푸터가 `Open sell` 라디오와 같은 y 에 있다(`Open sell@555,659` vs `Add@530,651`). 라디오를 노렸는데 Add 가 눌렸다. 패널을 스크롤한 뒤 라디오 원을 눌러 되돌렸고, 2 주치 그리드를 읽어 기존 9/14 토글만 남은 걸 확인했다.

---

## 8. 문서가 제품과 어긋난 곳 (디자이너에게 넘길 것)

판매관리 상태 안내 패널이 실제로는 **4 섹션 11 행**인데 문서는 **6 섹션 18 행**으로 적혀 있다. 요금조절과 판매완료/재고가 제품에서 빠졌고 고정요금 행이 들어왔다. All / 재고 / 요금 탭 어디서나 같아서 조건부 노출도 아니다. **한국어, 영어 문서 둘 다 낡았다.**

상품 서비스 선택도 상품 모달에서 빠졌다. 서비스는 이제 요금에 붙는다. `en/inventory-rate/package-stay.mdx` 의 "Package inclusions" 절이 낡았고 한국어도 같다.

상품 삭제: 문서는 "채널 연결 상품은 삭제할 수 없다"고 쓰는데 현재 목록의 휴지통은 전부 활성이다. 누른 뒤에 막히는지는 확인 못 했다(3 절).

판매관리이해하기 범례 5 장(2-1 절): 현재 패널은 4 섹션 11 행이고 한국어 본문은 옛 행을 설명한다. 글과 이미지를 같이 바꿔야 한다. 현재 한국어 패널은 판매관리 화면의 ⓘ (판매 상태 보기)를 누르면 나온다.

영어 본문도 같은 곳이 낡았다. 상품 "Extra rate adjustment" 절은 금액/비율 가산을 설명하는데 제품은 `Rate scale factor`(배수) 체크박스다.
