# 🌸 프로젝트 꽃 (Project Flower)

**지금, 내 근처에서 볼 수 있는 꽃과 나들이 장소를 추천하는 시즌형 웹 서비스**

대학교 과제 프로젝트 · 지속 발전 목적 · 웹 MVP → 앱 전환 계획

---

## ✨ 기능

- 🏠 **이달의 꽃**: 현재 월 기준 개화 중인 꽃 자동 노출
- 🌸 **꽃 둘러보기**: 꽃별 개화시기 및 관련 명소 조회
- 📍 **지역별 명소**: 시/도별 꽃 명소 탐색
- 🏷️ **테마 추천**: 부모님 · 데이트 · 산책 · 등산
- 🧭 **내 근처**: 위치 기반 거리순 추천

---

## 🚀 실행 방법

### 1. 환경 준비 (최초 1회)

```powershell
# 가상환경 생성 (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 패키지 설치
pip install -r requirements.txt
```

### 2. 연결 테스트 (권장)

```powershell
python test_connection.py
```

`🎉 전체 5개 시트 정상 연결!` 이 뜨면 다음 단계로.

### 3. 앱 실행

```powershell
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501` 접속.

---

## 📁 프로젝트 구조

```
project-flower/
├── app.py                 # Streamlit 메인 앱
├── config.py              # 데이터 소스 및 환경 설정
├── test_connection.py     # 연결 테스트 스크립트
├── requirements.txt
├── README.md
└── utils/
    ├── __init__.py
    ├── loader.py          # Google Sheets 데이터 로딩
    ├── geo.py             # 거리 계산 (Haversine)
    └── recommend.py       # 추천 로직
```

---

## 🗄️ 데이터 소스

Google Sheets를 데이터베이스로 사용합니다.

- **장점**: 브라우저에서 바로 편집 가능, 실시간 반영, 무료
- **구조**: 한 스프레드시트 안에 5개 시트(탭)
  - `flowers`: 꽃 마스터
  - `places`: 장소 마스터
  - `flower_place`: 꽃-장소 매핑
  - `themes`: 테마 마스터
  - `place_theme`: 장소-테마 적합도

데이터를 추가하려면: 구글 시트에 직접 행을 추가 → 앱 사이드바의 "🔄 데이터 새로고침" 클릭

---

## 🎬 발표 시연 시나리오

1. 홈 → 현재 월 꽃 자동 노출 (시간 기반 자동화)
2. 꽃 상세 → 벚꽃 선택 → 관련 명소 자동 연결 (데이터 관계)
3. 지역별 → 경남 선택 → 필터링
4. 테마 → 부모님 → 적합도 순 추천
5. 내 근처 → 창원 → 거리순 정렬
6. **구글 시트에서 새 꽃 추가 → 웹 새로고침 → 즉시 반영** ← 차별화 포인트

---

## 🛣️ 로드맵

| 단계 | 내용 | 상태 |
|---|---|---|
| 1 | MVP: 5개 핵심 페이지 | ✅ 현재 |
| 2 | 콘텐츠 강화 (사진, 스토리) | 🔜 |
| 3 | 회원/즐겨찾기/후기 | 📅 |
| 4 | 방문기록 기반 개인화 | 📅 |
| 5 | FastAPI + React Native 앱 | 🎯 |

---

## 📝 라이선스 / 크레딧

- 플레이스홀더 이미지: [Lorem Picsum](https://picsum.photos)
- 지도 API 미사용 (Haversine 공식 직접 구현)
