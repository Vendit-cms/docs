# CHANGELOG

## 2026-09-13
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
