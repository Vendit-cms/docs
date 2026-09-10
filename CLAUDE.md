# vcms-docs

## 🔒 한국어 동결 — 이 조건은 Dean 이 직접 풀기 전까지 유효하다

**`ko/` 는 건드리지 마라. 영어(`en/`)만 수정한다.** (2026-09-10, Dean)

한국어 문서는 디자이너가 별도로 작업 중이다. 내가 손대면 그쪽 작업과 충돌한다.

- `ko/**` 수정·추가·삭제 전부 금지. 오타여도, 명백한 버그여도 고치지 마라. 발견하면 말만 하고 넘어가라.
- `docs.json` 은 `navigation.languages[]` 안에서 **en 블록만** 만진다. ko 블록은 그대로 둔다.
- `images/` 는 ko/en 공유다. **원본을 덮으면 한국어 문서가 같이 바뀐다.**
  새 캡처는 반드시 `en-` 접두 새 파일로 넣고 `en/` 페이지의 참조만 갈아끼운다.
- 예외 없음. 조건 해제는 Dean 의 명시적 지시로만.

마지막으로 승인된 ko 변경: 채널 카드 아이콘 19개를 실제 브랜드 SVG 로 교체
(`51e7e39`, `0ffec72`). 여기까지가 끝이다.

## 레포 함정

- **파일명이 NFD 로 저장돼 있다.** 맥에서 `git add -A` 하면 이미지 254장이 유령 중복으로
  커밋된다. `git config core.precomposeunicode false` 로 잡히지만, **`git add -A` 자체를 쓰지 마라.**
  경로를 명시해서 `git add <path>` 로만 스테이징한다.
- 새로 쓰는 페이지에서 한글 이미지를 참조할 때도 **경로를 NFD 로** 써야 한다.
  NFC 로 쓰면 눈으로는 똑같은데 배포 사이트에서 404 난다.
- `images/Camfit-1.png` 와 `images/camfit-1.png` 가 대소문자로 충돌한다.
  `git update-index --skip-worktree` 걸려 있다.

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
- 작업 끝나면 VENDIT HOTEL UI 언어를 한국어로 되돌린다.

## 이미지 정책

- release-notes 82장은 한국어 이미지 재사용으로 결정(Dean, 2026-09-09).
- 채널사 화면(야놀자·아고다 YCS 등)은 Dean 이 직접 찍는다.
- 페이지별 현황은 `IMAGES.md`.
