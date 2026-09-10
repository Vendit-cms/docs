# 이어서 작업하기 — docs.vcms.io 영어판

이 파일 하나만 읽으면 다음 세션이 바로 이어갈 수 있게 적었다. 마지막 갱신 2026-09-11.

---

## 0. 먼저 지켜야 할 것

### 🔒 한국어 동결
`ko/` 는 건드리지 마라. 디자이너가 작업 중이다. Dean 이 직접 풀기 전까지 유효하다.
오타여도, 명백한 버그여도 고치지 마라. `docs.json` 은 `navigation.languages[]` 안에서 **en 블록만** 만진다.
커밋 전마다 `git diff --cached --numstat -- ko/ | wc -l` 이 0 인지 확인해라. 지금까지 12 커밋 전부 0 이다.

### `git add -A` 금지
파일명이 **NFD** 로 저장돼 있다. `-A` 를 쓰면 이미지 254 장이 복제된다. 항상 경로를 명시해서 `git add <경로>`.
같은 이유로 `sed` 로 이미지 참조를 바꾸면 **아무 말 없이 하나도 안 바뀐다**(셸 입력은 NFC). 참조 교체는 `scripts/swap_image.py` 만 써라.

### 서버 경계
| 대상 | 허용 |
| --- | --- |
| `development.vcms.io` | 조회·모달 열기만. **저장 금지** |
| `www.vcms.io` VENDIT HOTEL | 쓰기 허용 (Dean 이 허가한 유일한 운영 업소) |
| `www.vcms.io` 그 외 | 절대 금지 |

결제·구독·해지 버튼은 어느 서버에서도 누르지 마라. 모달은 열어도 된다.

---

## 1. 레포

- 경로 `~/projects/vcms-docs`, 정본 원격 `Vendit-cms/docs` (사본 2 개는 낡았다). 푸시 권한은 개인 계정 `yujy118`.
- 현재 브랜치 **`en-full-recapture`**, `main` 대비 12 커밋. 아직 PR 없다.
- Mintlify. 언어는 `docs.json` 의 `navigation.languages` 에 ko / en 두 블록.
- `images/` 는 **ko 와 en 이 공유한다.** 원본을 덮으면 한국어 문서까지 바뀐다. 새 캡처는 반드시 `en-` 접두 새 파일로 넣고 참조만 갈아끼운다.

### 커밋 (오래된 것부터)
```
25adf98  로그인·판매관리 상태 안내
a2c647c  판매관리 보기설정·필터·예약
3b83474  객실타입·기간·요금·서비스
6dc163b  판매시간표
4c9f280  일괄변경
03c6013  상품 (샘플 데이터 영어화 후)
b5499a0  판매관리 이해하기 범례 2 장 (텍스트 덮어쓰기)
94d67d1  구독 4 장 (dev)
14a1458  서비스·요금·판매시간표 재촬영
fb977c7  상품 요금정보 5 장
199803d  구독 상세·구독 관리
9f3ab10  서비스 구독 연간 결제 토글
```

---

## 2. 지금 어디까지 왔나

`IMAGES.md` 가 정본이다. 손으로 고치지 마라, `python3 scripts/images_manifest.py > IMAGES.md` 로 다시 만든다.

**참조 275 건 중 175 건 정리 완료, 100 건 남음.**

| 상태 | 건수 | 뜻 |
| --- | --- | --- |
| 한국어 재사용 | 82 | 릴리즈 노트. Dean 이 2026-09-09 에 그대로 두기로 결정 |
| 영어 캡처 완료 | 74 | `en-` 파일 |
| 채널사 화면 | 74 | 야놀자·아고다·여기어때·네이버·에어비앤비·익스피디아·트립닷컴 파트너 화면. **Dean 몫** |
| 한국어 유지 | 21 | 내가 아직 못 찍은 것 (아래 3 절) |
| 채널 로고 | 19 | 언어 무관 |
| 재현 불가 | 5 | 사유는 `images_manifest.py` 의 `BLOCKED` 에 적어뒀다 |

구독 화면은 **9 장 전부 영어로 끝났다**(기본 2 탭, 결제수단, 결제일 변경, 서비스 구독, 연간 결제, 결제내역 상세, 구독 상세, 구독 관리).

---

## 3. 남은 21 건 — 다음에 할 일

| 페이지 | 이미지 | 메모 |
| --- | --- | --- |
| `en/inventory-rate/package-stay.mdx` | `create-pkg-rate-select`, `create-pkg-inclusions` | 빈 생성 폼은 요금 아래가 전부 비활성이다. 기존 상품 Deluxe Roomonly 의 정보 수정 모달에서 찍어라 |
| 〃 | `260903-add-multi-period`, `260903-single-pkg-add-period`, `260903-bulk-update-rate-plan-modal`, `260903-bulk-update-rate-plan-button`, `260903-single-pkg-import-rate-plan-button` | 상품 기간·요금제 가져오기 흐름 |
| 〃 | `pkg_delete` | |
| `en/faq/integrations/vcloud.mdx` | `연동서비스_2`, `연동서비스_4`, `연동서비스_5` | 설정 > 연동 서비스 `/setting/systems`. 버튼 `Delete@629,275` / `Settings@1191,248`. **연결 해제 다이얼로그는 열어도 확인은 절대 누르지 마라** — VENDIT HOTEL 예약이 그 연동으로 들어온다 |
| `en/faq/inventory-rate/bulk-period-rate-adjustment.mdx` | `기간가중치_1`, `기간가중치_2` | |
| `en/distributions/channel-sync.mdx` | `Distribution-Syncing`, `Distribution-Booking-Sync-Only` | |
| `en/faq/booking/...` | `cancel-booking-noti`, `faq-no-history` | |
| `en/faq/inventory-rate/airbnb-promotion-reset.mdx` | `image-34`, `image-(1...` | 채널 화면일 가능성 있음, 열어보고 판단 |
| `en/faq/inventory-rate/yanolja-hotdeal-goldclass.mdx` | `image(65`, `image(66` | 야놀자 화면이면 Dean 몫 |

그 외 미해결:
- `term_coverage.py` 가 뽑은 후보 70 건이 아직 검증 안 됐다.
- 내비게이션에 없는 페이지 11 개의 폴백 처리 방침을 Dean 이 아직 안 골랐다.
- 캡처 끝나면 **VENDIT HOTEL 의 UI 언어를 한국어로 되돌려야 한다.**

---

## 4. 도구

### `scripts/cdp_capture.py` — 주력 캡처기
헤드리스 크롬을 CDP 로 몰아서 모달까지 열고 찍는다. 결과물 4320x2700.

```bash
# 캡처 전용 프로필(로그인 + UI 영어 + 사이드바 펼침)로 찍기
python3 scripts/cdp_capture.py jobs.json 출력폴더

# Dean 이 띄워둔 창에 붙어서 찍기
ATTACH=1 CDP_PORT=9222 TAB_MATCH=development.vcms.io SCALE=3 \
  python3 scripts/cdp_capture.py jobs.json 출력폴더
```

job 키: `url` `load` `click`(정규식, 스크롤됨) `click_at`(좌표 반환 JS) `js` `click_after` `wait` `step_wait`
`blur` `blur_js` `box` `box_list` `box_js` `crops` `pad`

**실행 순서가 함정이다.** `click` → `click_at` → `js` → `click_after`. 스크롤이 필요하면 `click`(텍스트) 을 써라, `click_at` 은 화면 밖 좌표를 그대로 눌러서 헛클릭한다.

### 겪은 함정 (다시 밟지 마라)
- **`CDP_PORT` 기본값은 9333 이다.** `ATTACH=1` 로 붙을 땐 `CDP_PORT=9222` 를 반드시 붙여라.
- **백그라운드 탭은 마우스 이벤트를 삼킨다.** 네비게이션도 되고 JS 도 도는데 클릭만 안 먹는다. ATTACH 모드는 `Page.bringToFront` 를 먼저 부른다(이미 들어가 있다).
- **Radix 팝오버는 mousePressed/Released 만으로는 안 열린다.** 같은 좌표로 `mouseMoved` 를 먼저 보내야 한다(이미 들어가 있다).
- **다이얼로그가 열리면 앱이 사이드바를 접는다.** 제품 동작이다. 영어 캡처는 전부 접힌 상태라 일관돼 있다.
- 블러 반경을 영역 높이로 잡으면 세로로 긴 열이 백지가 된다. `min(h*0.35, 4*scale)` 로 고정돼 있다.
- 개인정보는 반드시 `blur_js` 로 지워라. 첫 예약 캡처가 실제 투숙객 이름을 그대로 내보냈다.

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
| 수연스테이(유료고객) | `01K56E56BCN5ERZ28CR2TXTFZD` | 재고·요금 연간 구독 중, 52 rooms. **구독 상세 / 구독 관리** 모달이 여기서만 열린다 |
| 결제미납업장테스트 | `01JQVCCF9QRVWCW381E0VQ9YA8` | 결제 실패 상태 |

VENDIT HOTEL(운영) 은 무료체험이라 구독 화면 자체가 없다.

---

## 7. 사고 기록 — 같은 실수 반복 금지

운영 VENDIT HOTEL 에서 두 번 저장이 나갔고 둘 다 되돌렸다.

1. **디럭스 최대 인원 5 → 4.** 객실타입 수정의 확인 다이얼로그는 CMS 관리 타입 + 범위를 벗어난 상품이 있을 때만 뜬다. VENDIT HOTEL 은 전부 채널 관리라 저장이 그대로 나갔다. 5 로 복구, 행을 다시 읽어 확인했다.
2. **디럭스 9/15~20 판매중지.** 일괄변경 모달의 고정 `Add` 푸터가 `Open sell` 라디오와 같은 y 에 있다(`Open sell@555,659` vs `Add@530,651`). 라디오를 노렸는데 Add 가 눌렸다. 패널을 스크롤한 뒤 라디오 원을 눌러 되돌렸고, 2 주치 그리드를 읽어 기존 9/14 토글만 남은 걸 확인했다.

---

## 8. 문서가 제품과 어긋난 곳 (디자이너에게 넘길 것)

판매관리 상태 안내 패널이 실제로는 **4 섹션 11 행**인데 문서는 **6 섹션 18 행**으로 적혀 있다. 요금조절과 판매완료/재고가 제품에서 빠졌고 고정요금 행이 들어왔다. All / 재고 / 요금 탭 어디서나 같아서 조건부 노출도 아니다. **한국어·영어 문서 둘 다 낡았다.**
