"""
데이터 로더

Google Sheets에서 CSV export URL로 데이터를 읽어온다.
Streamlit 캐시로 네트워크 호출을 최소화.

★ 향후 확장 포인트:
  - SQLite/PostgreSQL로 교체 시 여기만 수정하면 앱 나머지는 동일
  - gspread 기반 인증 방식으로 전환 시 get_csv_url만 변경
"""
import pandas as pd
import streamlit as st

from config import SHEET_ID, SHEET_GIDS, CACHE_TTL_SECONDS


def get_csv_url(sheet_id: str, gid: int) -> str:
    """Google Sheets를 CSV로 export하는 공개 URL 생성."""
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="데이터 불러오는 중...")
def load_all_data() -> dict:
    """
    5개 시트를 모두 읽어서 딕셔너리로 반환.

    Returns:
        {
            'flowers': DataFrame,
            'places': DataFrame,
            'flower_place': DataFrame,
            'themes': DataFrame,
            'place_theme': DataFrame,
        }
    """
    data = {}
    for name, gid in SHEET_GIDS.items():
        url = get_csv_url(SHEET_ID, gid)
        data[name] = pd.read_csv(url)
    return data


def clear_cache():
    """캐시 수동 삭제 (발표 시연 시 '새로고침' 버튼용)."""
    st.cache_data.clear()


# ============================================================
# 개별 조회 헬퍼 (코드 가독성용)
# ============================================================
def get_flowers(data: dict) -> pd.DataFrame:
    return data["flowers"]


def get_places(data: dict) -> pd.DataFrame:
    return data["places"]


def get_themes(data: dict) -> pd.DataFrame:
    return data["themes"]


def get_flower_place(data: dict) -> pd.DataFrame:
    return data["flower_place"]


def get_place_theme(data: dict) -> pd.DataFrame:
    return data["place_theme"]
