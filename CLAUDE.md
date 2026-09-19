# vcms-docs

## 🔒 한국어 글 동결: 이 조건은 Dean 이 직접 풀기 전까지 유효하다

**`ko/` 의 글은 건드리지 마라.** (2026-09-10, Dean) 한국어 문장은 디자이너가 별도로 작업 중이다.

**이미지 최신화만 풀렸다.** (2026-09-11, Dean: "한국 문서도 혹시 사진 최신화해야하면 우리가하자")

- 문장, 표, 서식, alt 텍스트, 페이지 추가/삭제는 여전히 금지. 오타여도 고치지 마라. 발견하면 말만 한다.
- 한국어 이미지는 **ko 페이지만 쓰는 원본 파일이면 제자리에서 덮어쓴다.** 그러면 `ko/*.mdx` 를 한 줄도 안 건드려서 디자이너 작업과 안 부딪친다.
  덮기 전에 그 파일을 en 페이지나 릴리즈 노트가 참조하는지 반드시 센다. 참조하면 `ko-` 접두 새 파일로 넣고 `python3 scripts/swap_image.py --ko-images ...` 로 참조 한 줄만 바꾼다.
- 파일명이 NFD 다. 덮을 땐 디렉터리 목록의 실제 이름으로 써라. 셸에 한글을 쳐서 `cp` 하면 NFC 복제본이 새로 생긴다.
- `docs.json` 은 `navigation.languages[]` 안에서 **en 블록만** 만진다. ko 블록은 그대로 둔다.
- 영어 캡처는 여전히 `en-` 접두 새 파일로 넣는다.

승인된 ko 변경, 이 목록 밖은 없다:
- 채널 카드 아이콘 19개를 실제 브랜드 SVG 로 교체 (`51e7e39`, `0ffec72`)
- `ko/distributions/usage.mdx` 8행 판매 상태 데모 iframe `src` 교체 (`382a8a2`, Dean 2026-09-19 "수정하고 배포한다")
- 같은 iframe 을 한국어 드래그판 데모로 다시 교체하고 `height="415"` 를 영어판과 같은
  `style={{ aspectRatio:"1.6", height:"auto" }}` 로 (Dean 2026-09-19, 이 한 줄만 서식 허용)

iframe 한 줄 허용이 ko iframe 일반 허용은 아니다. 다른 ko 페이지는 여전히 묻는다.

## 레포 함정

- **파일명이 NFD 로 저장돼 있다.** 맥에서 `git add -A` 하면 이미지 254장이 유령 중복으로
  커밋된다. `git config core.precomposeunicode false` 로 잡히지만, **`git add -A` 자체를 쓰지 마라.**
  경로를 명시해서 `git add <path>` 로만 스테이징한다.
- 새로 쓰는 페이지에서 한글 이미지를 참조할 때도 **경로를 NFD 로** 써야 한다.
  NFC 로 쓰면 눈으로는 똑같은데 배포 사이트에서 404 난다.
- `images/Camfit-1.png` 와 `images/camfit-1.png` 가 대소문자로 충돌한다.
  `git update-index --skip-worktree` 걸려 있다.
- **이미지를 같은 이름으로 덮으면 Mintlify 가 옛 치수를 계속 쓴다.** 새 바이트는 내려주면서
  `width`/`height` 와 `style="aspect-ratio:"` 는 캐시된 값이라 `class="object-contain"` 이
  그 낡은 박스 안에 레터박싱한다. 2026-09-13 에 `en-legend-*` 4장이 7680x3520(가로 2.18:1)인데
  900x974(세로 0.92:1) 박스에 갇혀 화면 절반이 빈칸이었다. `#47` 에 올린 판을 `#48` 이 덮은 게 원인이고,
  **그 뒤로 배포를 두 번 더 해도 안 풀렸다.** 고치는 법은 파일명을 바꾸는 것뿐이다.
  점검은 `python3 scripts/check_image_dims.py`(라이브 선언값 vs 레포 실제값, 불일치면 exit 1).

## 용어는 추측하지 마라

정본 두 개, 둘 다 `~/projects/vcms-i18n`:

1. `glossary/glossary.json` — 135 항목, PM 결정 note 포함
2. `locales/latest/en.json` — 3,278 키, 실제 화면에 뜨는 영어

검사기 두 개가 레포에 있다:

```
python3 scripts/glossary_check.py en        # 금칙어 18 규칙, 각 규칙에 i18n 키 경로 붙어 있음
python3 scripts/term_coverage.py            # 반대 방향. ko 원문에 있는 용어가 en 에 canon 으로 나오나
python3 scripts/demo_glossary_check.py      # Supademo 라이브 임베드 페이로드에 같은 규칙 적용
```

## 캡처

`scripts/cdp_capture.py jobs.json <출력폴더>` 가 정본. 헤드리스 크롬 + CDP, 창 1440x900 에
`--force-device-scale-factor=3` = 4320px 원본급.

- 프로필 `~/.vcms-capture-profile` 에 VENDIT HOTEL 로그인 + UI 언어 English + 사이드바 펼침.
- **React 는 `el.click()` 을 무시한다**(탭·라디오). `Input.dispatchMouseEvent` 로 진짜 마우스 이벤트를 쏴야 한다.
- **`click` 단계가 `click_at` 단계보다 먼저 실행된다.** 메뉴를 `click_at` 으로 열고 항목을
  `click` 으로 고르는 순서는 안 먹는다. 전부 `click_at` 으로 써라.
- VENDIT HOTEL 은 연결된 채널이 0개다. `채널_*` 이미지는 재현 불가.
- 못 찍는 건 한국어 이미지를 그대로 둔다(Dean, 2026-09-09).
- **VENDIT HOTEL 로 못 찍는 채널 화면은 실제 고객 업장(대구 아르코, 연결 채널 6개)에서 찍는다.**
  Dean 이 2026-09-13 에 열어줬고 **조건은 조회만**이다. 저장, 연결, 연결 해제, 재연결은 누르지 마라.
  가리는 건 `scripts/capture_redacted.py` 가 한다. 규칙과 실패 사례는 그 파일 맨 위에 적어놨다.
  요약: 영어 UI 에 한글이 보이면 계정 데이터니 가린다. `만` 은 통화 축약이라 가리지 말고 숫자로 바꾼다.
  찍고 나면 **눈으로 확인해라** - 규칙이 못 잡는 식별자가 실제로 두 번 빠져나갔다.
- **찍고 나면 `python3 scripts/check_captures.py` 를 돌려라.** 사이드바가 통째로 빈 캡처 9장이
  그대로 배포된 적이 있다(2026-09-13). 모달만 보면 안 보인다.
- 작업 끝나면 VENDIT HOTEL UI 언어를 한국어로 되돌린다.

## 이미지 정책

- release-notes 82장은 한국어 이미지 재사용으로 결정(Dean, 2026-09-09).
- **채널사가 만든 화면(야놀자 파트너센터, 아고다 YCS, 익스피디아 콘솔, 에어비앤비 등)은 범위 밖이다(Dean, 2026-09-13).** 사진은 한국어 그대로 두고 본문 영어 번역만 한다. 50장이 여기 해당한다.
  우리가 손대는 건 VCMS 자체 화면뿐이다. 크롬 확장 프로그램 메뉴도 브라우저 UI라 범위 밖이다.
- 카카오 알림톡 원문(`cancel-booking-noti.png`, `channel-auto-disconnect-noti.png`)은 한국어로만 발송된다.
- **영어 페이지에는 한글 파일명을 두지 마라(Dean, 2026-09-13).** 사진이 한국어로 남더라도 파일 이름은 영어로 간다.
  `images/` 는 ko 와 공유하니 옮기지 말고 영어 이름 사본을 새로 넣어라. ko 쪽 참조는 건드리지 마라.
  이름은 지어내지 말고 그 페이지의 alt 텍스트에서 가져와라. **`en-` 접두사는 금지** — `images_manifest.py` 가 그걸 영어 캡처 완료 표지로 쓴다.
- 페이지별 현황은 `IMAGES.md`.
