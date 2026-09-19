# CHANGELOG

## 2026-09-19
- 행 참조 해석이 반쪽이었던 것 수정. 텍스트 행 뒤에 줄바꿈 없이 붙는 행을 놓쳐서 참조 44개 중 30개가 번호째 해시되고 있었다. 행을 앞에서부터 길이대로 읽는다. 지문 30개 재기록, 데모 변경은 없다 (scripts/supademo_audit.py, audit/supademo/)
- 판매 상태 데모를 영어, 한국어 둘 다 드래그판으로 다시 찍었다. 2번 스텝이 전체 객실 행에서 셀 드래그로 바뀌어 본문의 '좌우로 끌어' 설명과 맞는다. 4스텝, 영상 0 (en/distributions/usage.mdx, ko/distributions/usage.mdx, audit/supademo/)
- '판매 중지는 드래그가 안 된다' 는 틀렸다. 토글 가운데서, 꺼진 원본으로 끌어서 안 된 것이다. 핸들에서 켜진 원본으로 끌면 CDP 로도 된다 (HANDOFF.md)
- 한국어 판매 상태 iframe 높이 415px 고정을 영어판과 같은 비율 1.6 으로, Dean 승인 한 줄 (ko/distributions/usage.mdx, CLAUDE.md)
- 새 데모 제목과 메타 설명을 손으로 지정, 영어 제목 'VCMS stop sell change' 를 섹션 제목에 맞춰 'VCMS sell status change' 로 (audit/supademo/)
- 촬영 하네스의 저장 바 감지가 한국어 UI 를 못 잡던 것 수정, 드래그 조건 주석 (scripts/supademo_take.py)
- `--check` 가 트리에 쓰고 git checkout, git clean 으로 되돌리던 것을 임시 디렉터리 비교로 바꿨다. 커밋 전 새 스냅샷을 지우고 있었다 (scripts/supademo_audit.py)
- 문서에서 빠진 데모의 스냅샷을 지운다. 교체된 잔여 재고 데모 cmtyc75ri0hrxqme9293l1cf5 가 옛 embeddedIn 을 달고 남아 있었다 (scripts/supademo_audit.py, audit/supademo/)
- 스냅샷에 메타 설명 `metadesc` 추가. 한국어 판매 상태 데모 설명에 'sales management' 가 있었는데 아무 검사기도 못 봤다 (scripts/supademo_audit.py, audit/supademo/)
- 데모 용어 검사가 영어 원본 데모 7편을 문자열 0개로 통과시키던 것 수정, 번역본이 없으면 핫스팟 문구를 본다. 메타 설명도 검사한다. 144개에서 199개 (scripts/demo_glossary_check.py)
- 스냅샷이 매번 바뀌던 것 수정. 핫스팟 DOM 지문을 RSC 행 참조(`$1b`)로 해시하고 있었다. 행 번호는 페이로드 위치라서 데모가 그대로여도 밀린다. 데모 13편이 바뀐 것처럼 보였다 (scripts/supademo_audit.py)
- 임베드 파싱을 `self.__next_f.push` 조각별 json.loads 로 교체. 통째 치환은 이스케이프된 따옴표까지 풀어서 문자열 경계가 깨진다 (scripts/supademo_audit.py)
- 위 수정으로 핫스팟 지문 42개 재기록, 실제 데모 변경은 없다 (audit/supademo/)
- 한국어 판매 상태 데모를 새로 찍었다. 한국어도 판매 상태와 잔여 재고가 같은 데모를 쓰고 있었다. 영어판과 같은 4스텝 구성 (ko/distributions/usage.mdx, audit/supademo/)

## 2026-09-18
- 영어 판매 상태 데모를 새로 찍었다. 판매 상태와 잔여 재고 두 자리가 같은 데모를 쓰고 있었다. 잔여 재고 데모와 같은 4스텝 구성이고 영상 스텝은 없다 (en/distributions/usage.mdx, audit/supademo/)
- 영어 잔여 재고 데모 재촬영, 저장을 눌러서 적용된 화면과 컨페티까지 들어갔다. 영상 스텝은 안 쓴다 (en/distributions/usage.mdx)
- 슈파데모 스냅샷 갱신, 새 데모 하나 추가 (audit/supademo/)
- 3초를 넘는 영상 스텝 16개를 1초로 줄였다. 데모 6편, 최장 34.05초였다. 이제 문서에 박힌 데모 23편의 영상 스텝 31개가 전부 3초 이하다 (audit/supademo/)
- 스냅샷에 스텝 재생 길이 `sec` 추가. 이게 없어서 트림을 고쳐도 diff 가 조용했다 (scripts/supademo_audit.py)

## 2026-09-17
- 개인정보 동의서의 수집 항목을 현행 연동 채널로 교체, 한국어와 영어 양쪽 (ko/reference/personal-information-consent.mdx, en/reference/personal-information-consent.mdx)
- 동의서의 캠퍼레스트 항목을 화면 라벨과 같은 캠핑장 ID 로 정정, 호텔 코드가 아니다 (ko/reference/personal-information-consent.mdx, en/reference/personal-information-consent.mdx)
- sync 배너 캡처의 원인을 앱 버그로 정정, 번역 문제가 아니었다 (scripts/images_manifest.py)

## 2026-09-16
- 이용약관 논리 오류 4건 수정, 한국어 정본과 영어 양쪽 (ko/reference/terms-conditions.mdx, en/reference/terms-conditions.mdx)
- 영어 이용약관을 한국어 정본 전문 번역으로 교체, 요약본이라 제8조 회사의 의무가 없고 제8조부터 조 번호가 한 칸씩 밀려 있었다 (en/reference/terms-conditions.mdx)
- 캠핏 안내문에서 내가 지웠던 작은따옴표 2개 복원, 볼드는 닫는 ** 위치만 옮겨 살렸다 (ko/channels/camfit.mdx)
- 캠핏 제휴 옵션 절을 영어로 번역, ko 에만 있던 것 (en/channels/camfit.mdx)
- 상품 삭제 안내 캡처를 영어로 교체, 채널 매핑된 상품의 잠긴 휴지통과 툴팁 (images/en-pkg-delete.png)
- 다 찍은 pkg_delete.png 를 확인 대기 목록에서 제거, sync-banner 사유가 틀렸던 것 정정 (scripts/images_manifest.py)

## 2026-09-15
- 문서에 임베드된 Supademo 데모 23 편 스냅샷, git diff 가 변경 이력이 된다 (scripts/supademo_audit.py)
- 스냅샷 첫 기록 (audit/supademo/)
- 배포된 예약 목록 캡처에서 투숙객 이름 가림 (images/en-booking-status-filter.png)
- 예약 목록 Guest name 열을 통째로 가리는 규칙 추가 - 로마자 이름은 기존 규칙에 안 걸렸다 (scripts/capture_redacted.py)

## 2026-09-14
- 릴리즈노트 영어 캡처 12 장 (images/en-fixed-rate-protection.png 외 11 장)
- 현재 빌드와 다른 릴리즈노트 사진 17 장을 히스토리로 보존 처리, 재현 불가 10 장 기록 (scripts/images_manifest.py)
- 말풍선을 상자 위아래에도 붙일 수 있게, 상자 없이 말풍선만 그릴 수 있게 (scripts/annotate.py)
- 사이드바가 원래 없는 잘라낸 캡처 6 장을 검사 제외 (scripts/check_captures.py)
- 5월 15일 릴리즈노트 사진 3장 영어로 교체, 언어 선택, 객실 타입 최대값, 구독 안내 (images/en-260515-*.png)
- 1월 14일 슈파데모 임베드를 고정 415px 에서 비율 1.73 으로 교체 (en/release-notes/2026-01-14.mdx)
- 못 찍는 6장 사유 기록: 억 축약, 폰 합성 2장, 구독 취소, 드래그 2장 (scripts/images_manifest.py)
- 8월 20일 릴리즈노트 사진 3장, 8월 7일 4장을 영어 화면으로 교체 (images/en-260820-*.png, images/en-260807-*.png)
- 드래그 복사 2장과 예약 배수 비활성 1장은 재현 불가로 기록 (scripts/images_manifest.py)
- 스크롤로 가려진 항목 좌표에 블러가 찍혀 사이드바를 뭉개던 것 수정 (scripts/capture_redacted.py)
- 못 찍는 이유가 릴리즈노트 규칙에 덮이던 순서 수정 (scripts/images_manifest.py)
- 9월 3일 릴리즈노트 사진 11장을 영어 화면으로 교체, 한국어 말풍선을 영어로 다시 그렸다 (images/en-260903-*.png, en/release-notes/2026-09-03.mdx)
- 5월 15일 채널 연결 끊김 사진 영어판 추가, 숙소명만 가렸다 (images/en-distribution-channel-disconnected.png)
- 보라 강조 상자와 말풍선을 그리는 도구 추가 (scripts/annotate.py)
- 채널 캡처 9장 재촬영. 사이드바가 통째로 비어 있던 걸 고쳤다 (images/en-channel-*.png)
- 내부 메뉴 숨김이 부모를 3단계 무조건 올라가 nav 를 지우던 것 수정 (scripts/capture_redacted.py)
- 블러 좌표를 덜 그려진 DOM 에서 재던 경합 수정, settle() 추가 (scripts/capture_redacted.py)
- 입력칸 값이 로그에 찍히던 것 차단, 식별자 모양이면 <가림> 으로 (scripts/capture_redacted.py)
- 사이드바 빈 캡처를 기계로 잡는 검사기 추가 (scripts/check_captures.py)

## 2026-09-13
- 영어 페이지가 참조하던 한글 이름 이미지 32개를 영어 이름 사본으로 교체, 한국어 원본은 ko 가 계속 쓴다 (images/, en/**/*.mdx)
- 한국어 야놀자 지연 FAQ 의 알림 연락처 이미지를 새 파일명으로 옮겨 Mintlify 의 낡은 치수 캐시를 깼다 (images/설정_숙박업소_알림연락처-2.png, ko/faq/issue/yanolja-booking-delay.mdx)
- 채널사가 만든 화면 50장을 범위 밖으로 확정, 한국어 사진 유지하고 본문 번역만 한다 (scripts/images_manifest.py, CLAUDE.md)
- 알림톡 원문 channel-auto-disconnect-noti.png 을 재현 불가로 분류, 크롬 확장 메뉴 2장은 브라우저 UI로 분리 (scripts/images_manifest.py)
- 완료 판정이 접두사 "영어" 로 재캡처 대기까지 세던 것 수정 (scripts/images_manifest.py)
- 채널 화면 영어 캡처 9장 추가, 한국어 원본 참조 20건 교체 (images/en-channel-*.png, en/channels/channel-setting.mdx, en/faq/inventory-rate/*.mdx)
- 업장 식별자를 가리고 찍는 캡처 스크립트 추가 (scripts/capture_redacted.py)
- 연결 플로우 2장은 조회 전용 권한으로 재현 불가라 사유와 함께 한국어 유지 (scripts/images_manifest.py)
- 영어 페이지 Supademo 임베드 13건을 고정 높이에서 데모별 실제 비율로 교체, 레터박스 여백 제거하고 반응형으로 (en/**/*.mdx)
- 영어 페이지 이미지 7장을 새 파일명으로 옮겨 Mintlify 의 낡은 치수 캐시를 깼다 (images/en-legend-*-2.png, images/en-booking-*-2.png)
- 위 7장의 참조를 새 이름으로 교체 (en/distributions/understanding.mdx, en/bookings/bookings.mdx)
- 라이브 선언 치수와 레포 실제 치수를 대조하는 검사기 추가 (scripts/check_image_dims.py)
- Mintlify 이미지 치수 캐시 함정을 레포 함정 절에 기록 (CLAUDE.md)
- IMAGES.md 재생성 (IMAGES.md)
- 영어 Supademo 데모 4편 신규 촬영, 영어 페이지의 한국어 데모 교체 (en/distributions/usage.mdx, en/faq/inventory-rate/move-room-to-other-type.mdx)
- 전체 객실 요금조절 cmtz313ow0sv8qme9m0s845be, 객실타입 요금조절 cmtz35id90swnqme9v8xtizqs, 요금 변경 cmtz49f960tajqme9fiwfjexr, 객실 타입 이동 cmtz4k5800tcwqme9w39nmeeb
- 입/퇴실 데모에 보기 설정으로 행 숨기는 구간 5스텝 추가 (cmtyd1bg70i80qme9d53qqrer, 14 -> 19스텝)
- 촬영 하네스 보강: 만 단위 표기 실시간 보정 관찰자, 행 숨김, Cancel 로 임시 변경 폐기, selectAll 입력 (scripts/supademo_take.py)
- 영어 데모 현황과 제품 이슈 4건 정리 (HANDOFF.md)

## 2026-09-12
- 영어 Supademo 데모 2개를 크롬 익스텐션 + CDP 로 새로 촬영 (en/distributions/usage.mdx, en/faq/inventory-rate/daily-chek-in-out-time.mdx)
- 잔여 재고 일괄 변경 영어 데모 cmtyc75ri0hrxqme9293l1cf5, 입/퇴실 시간 변경 영어 데모 cmtyd1bg70i80qme9d53qqrer
- 촬영 하네스 추가: 녹화 시작, Adjustment 행/직원 메뉴 숨김, 드래그 전파, 임시 변경 폐기
- 영어 판매관리 범례 4 장을 한국어 범례 규격으로 다시 만듦, 텍스트만 교체 (images/en-legend-*.png)
- 채널 화면 27 장 재분류, 연결된 채널 화면 22 장은 테스트 연결 대기 (scripts/images_manifest.py)
- 숙박업소 설정, 연결 가능 채널 영어 캡처, 한국어 숙박업소 설정 교체 (images/)
- 예약 내역 영어 캡처의 Download CSV 라벨 블러 수정 (images/en-booking-*.png)

## 2026-09-11
- 한국어 글 동결 유지, 이미지만 해제 (CLAUDE.md, scripts/swap_image.py --ko-images)
- 한국어 이미지 84 장 비교 후 낡은 14 장 한국어 UI 로 교체, 제자리 덮어쓰기 (images/)
- 영어 캡처 28 장 재촬영, 직원 전용 사이드바 메뉴 제거 (images/en-*.png)
- 운영 캡처 공용 헬퍼 추가: 직원 메뉴 숨김, 한국어 예약 블러 (scripts/jobkit.py)
- 상품 요금정보 기간 5 장, 요금 선택, 기간 가중치 2 장, 판매관리 동기화, VCLOUD 연동 실패 영어 캡처 (images/en-*.png)
- 영어 배너 {date} 버그로 보류한 판매관리 캡처 (images/en-distribution-booking-sync-only.png)
- job 헬퍼 추가 (scripts/jobkit.py), 마우스만 올리는 hover_at 스텝 추가 (scripts/cdp_capture.py)
- 괄호 파일명 인식, 채널 FAQ 페이지 분류, Dean 확인 필요 상태 추가 (scripts/images_manifest.py)
- 루트 내부 문서를 공개 사이트에서 제외 (.mintignore)
- 이어서 작업하기 인수인계 문서 생성 (HANDOFF.md)
- 서비스 구독 연간 결제 토글 영어 캡처 (images/en-subscription-annual.png)
- 구독 상세, 구독 관리 모달 영어 캡처 (images/en-subscription-detail.png, images/en-subscription-manage.png)
- 재현 불가 목록에서 구독 3 건 해제 (scripts/images_manifest.py)
