# CHANGELOG

## 2026-09-16
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
