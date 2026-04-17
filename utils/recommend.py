"""
추천 로직

규칙 기반 추천 엔진. 설명 가능한 점수 공식 사용.

★ 향후 확장 포인트:
  - 사용자 방문기록 기반 개인화 (4단계)
  - 협업 필터링 추가 (5단계)
  - 여기 함수들은 순수 함수라 FastAPI 엔드포인트로 그대로 이동 가능
"""
from datetime import datetime
import pandas as pd

from config import RECOMMEND_WEIGHTS
from utils.geo import haversine_km


# ============================================================
# 개화 판정
# ============================================================
def is_blooming(row: pd.Series, month: int) -> bool:
    """해당 월에 이 꽃이 피는가?"""
    start, end = row["bloom_start_month"], row["bloom_end_month"]
    if start <= end:
        return start <= month <= end
    # 겨울 경계 (예: 12~3월 동백)
    return month >= start or month <= end


def get_blooming_flowers(flowers_df: pd.DataFrame, month: int) -> pd.DataFrame:
    """해당 월에 피는 꽃 목록. 절정월 일치 꽃이 우선."""
    mask = flowers_df.apply(lambda r: is_blooming(r, month), axis=1)
    result = flowers_df[mask].copy()
    result["is_peak"] = result["peak_month"] == month
    return result.sort_values(["is_peak", "flower_id"], ascending=[False, True])


# ============================================================
# 점수 계산
# ============================================================
def bloom_score(flower_row: pd.Series, month: int) -> float:
    """개화 적합도 0~100."""
    if not is_blooming(flower_row, month):
        return 0
    if flower_row["peak_month"] == month:
        return 100
    return 70


def distance_score(distance_km: float) -> float:
    """거리 점수 0~100. 가까울수록 높음."""
    return max(0, 100 - distance_km * 2)


def theme_score(fit_score: int) -> float:
    """테마 적합도 0~100. fit_score 1~5 → 20~100."""
    return fit_score * 20


def combined_score(
    bloom_s: float, distance_s: float, theme_s: float
) -> float:
    """가중 평균 점수."""
    w = RECOMMEND_WEIGHTS
    return bloom_s * w["bloom"] + distance_s * w["distance"] + theme_s * w["theme"]


# ============================================================
# 조회 함수 (UI에서 직접 호출)
# ============================================================
def places_by_flower(
    flower_id: int, places_df: pd.DataFrame, flower_place_df: pd.DataFrame
) -> pd.DataFrame:
    """특정 꽃을 볼 수 있는 장소 목록."""
    fp = flower_place_df[flower_place_df["flower_id"] == flower_id]
    return places_df.merge(fp, on="place_id", how="inner")


def places_by_region(places_df: pd.DataFrame, sido: str) -> pd.DataFrame:
    """시/도별 장소 목록."""
    return places_df[places_df["region_sido"] == sido].copy()


def places_by_theme(
    theme_id: int, places_df: pd.DataFrame, place_theme_df: pd.DataFrame
) -> pd.DataFrame:
    """테마별 장소 목록. 적합도 높은 순."""
    pt = place_theme_df[place_theme_df["theme_id"] == theme_id]
    merged = places_df.merge(pt, on="place_id", how="inner")
    return merged.sort_values("fit_score", ascending=False)


def nearby_places(
    user_lat: float,
    user_lon: float,
    places_df: pd.DataFrame,
    max_km: float = 200,
    limit: int = 10,
) -> pd.DataFrame:
    """사용자 위치에서 가까운 장소 목록."""
    df = places_df.copy()
    df["distance_km"] = df.apply(
        lambda r: haversine_km(user_lat, user_lon, r["latitude"], r["longitude"]),
        axis=1,
    )
    df = df[df["distance_km"] <= max_km]
    return df.sort_values("distance_km").head(limit)


# ============================================================
# 통합 추천 (향후 확장용 - 월+위치+테마 가중 점수)
# ============================================================
def recommend_combined(
    places_df: pd.DataFrame,
    flowers_df: pd.DataFrame,
    flower_place_df: pd.DataFrame,
    place_theme_df: pd.DataFrame,
    month: int,
    user_lat: float = None,
    user_lon: float = None,
    theme_id: int = None,
    limit: int = 10,
) -> pd.DataFrame:
    """
    월 + 위치 + 테마를 종합한 추천.
    현재는 MVP의 개별 조회로 충분하지만, 확장 시 이 함수 사용.
    """
    # 1. 현재 월 개화 꽃
    blooming = get_blooming_flowers(flowers_df, month)
    blooming_ids = set(blooming["flower_id"])

    # 2. 개화 중인 꽃과 연결된 장소
    fp_blooming = flower_place_df[flower_place_df["flower_id"].isin(blooming_ids)]
    candidate_places = places_df.merge(fp_blooming, on="place_id", how="inner")

    # 3. 각 장소에 점수 부여
    rows = []
    for _, p in candidate_places.iterrows():
        flower_row = blooming[blooming["flower_id"] == p["flower_id"]].iloc[0]
        b_score = bloom_score(flower_row, month)

        # 거리 점수
        if user_lat is not None and user_lon is not None:
            dist = haversine_km(user_lat, user_lon, p["latitude"], p["longitude"])
            d_score = distance_score(dist)
        else:
            dist = None
            d_score = 50  # 위치 정보 없으면 중립값

        # 테마 점수
        if theme_id is not None:
            pt = place_theme_df[
                (place_theme_df["place_id"] == p["place_id"])
                & (place_theme_df["theme_id"] == theme_id)
            ]
            t_score = theme_score(pt["fit_score"].iloc[0]) if len(pt) else 0
        else:
            t_score = 50  # 테마 미선택 시 중립값

        total = combined_score(b_score, d_score, t_score)
        rows.append({
            "place_id": p["place_id"],
            "place_name": p["name"],
            "flower_name": flower_row["name_ko"],
            "region": f"{p['region_sido']} {p['region_sigungu']}",
            "distance_km": dist,
            "bloom_score": b_score,
            "distance_score": d_score,
            "theme_score": t_score,
            "total_score": total,
        })

    result = pd.DataFrame(rows)
    if len(result) == 0:
        return result
    return result.sort_values("total_score", ascending=False).head(limit)
