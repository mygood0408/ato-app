# ATO app — 장비구성뷰 (2호선 신호설비 고장분석 앱)

최종 목표: 신도림(SIN)은 기초일 뿐, **2호선 전 역 지원 범용 앱**. 화면 파일은 단일 `장비구성뷰_v3_시안.html`(서버 없음).

## 먼저 읽을 것 (이것만, 필요할 때만)
- 앱 구조·데이터↔HTML 변수 표·열린 항목: `claude/장비구성뷰_현황.md`
- 지난 세션 결과: `claude/완료세션_요약.md` (원본 인수인계서는 git 이력)
- 새 작업의 인수인계서가 있으면 사용자가 지정한 파일 하나만. 끝난 세션은 `claude/완료세션_요약.md`에 결과 3~8줄로 합치고 인수인계서는 삭제
- 사실 기록(다시 열지 말 것): `claude/현장설비_사진메모.md`, `claude/현장자료_메모.md`, `claude/역_인벤토리.md`, `claude/역확장_설계결정.md`

## 규칙
- **JSON 고치면 HTML 내장 변수도 같이 갱신.** 변수 교체는 정규식 `^var NAME = \{\n.*?^\};\n`, 줄번호 고정 금지. 변수↔파일 표는 현황 문서.
- **HTML 전체 Read·Grep 금지**(6MB, 한 줄 변수 최대 2.8MB). python으로 변수 단위 추출·교체. Grep은 `-o`와 짧은 패턴, 출력 제한.
- 큰 JSON(board-info 420KB 등)도 통째로 Read 금지. python으로 필요한 키만.
- PDF·사진 원문 덤프 금지. 텍스트는 스크립트 안에서 읽고 출력은 개수·쪽번호·한 줄 발췌만. 이미지는 필요한 영역만 크롭 1장. 한 번 본 것은 메모 파일에 저장하고 다시 열지 않음.
- 근거 없는 연결은 잇지 않고 `확인필요` 유지. 구조 동일 판단은 눈이 아니라 스크립트로 검증. 도면 "SIN1과 SIN2" = 같은 역의 다른 시스템.
- 용어: Sync-Loop·SL Track box = ATO LOOP(TWC 아님).
- 커밋은 영문 메시지 + `Co-Authored-By` 줄. push는 사용자가 요청할 때만. `claude/remedySteps_draft.json`은 보관용으로 커밋됨(앱 반영 완료). 그 외 untracked 초안·xlsx는 커밋 금지.
- 세션 끝에 인수인계서(있으면) 맨 아래 "결과" 3~8줄 추가. 일회용 스크립트는 끝나면 삭제.

## 경로·실행
- 원본 PDF: `C:\Users\김영추\Desktop\2호선 PDF 자료` (SICAS/ATP HW Design 역별, 매뉴얼들). KB: `...\2호선 PDF 자료\PDF_Knowledge_Base`.
- 미리보기: `.claude/launch.json`의 `ato-static`(포트 8765), 주소 `http://localhost:8765/장비구성뷰_v3_시안.html?v=번호`.
- KB 페이지 이미지 `kb_pages/`(127MB)는 gitignore, 배포용은 구글 드라이브 `ATO_kb_pages`. 새 쪽을 연결하면 `python claude/make_kb_pages.py` 후 Drive 업로드 필요.
- 보드 SVG 재생성: `python claude/gen_field_sw_svg/gen_field_sw_svg.py && python claude/sync_board_svg.py`.
- 역별 경로 스크립트: `claude/make_power_paths*.py`, `claude/sync_related_drawings.py`(`--station`·`stations.json`), 회귀 확인 `claude/s4_regress.py`.
