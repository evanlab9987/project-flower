"""
지리적 거리 계산

외부 지도 API 없이 두 지점 사이의 거리(km)를 계산.
Haversine 공식 사용.
"""
from math import radians, sin, cos, sqrt, asin
import pandas as pd


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """두 위경도 좌표 사이의 거리를 km 단위로 반환."""
    R = 6371  # 지구 반경 (km)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    return 2 * R * asin(sqrt(a))


def add_distance_column(
    places_df: pd.DataFrame, user_lat: float, user_lon: float
) -> pd.DataFrame:
    """places DataFrame에 거리 컬럼을 추가해서 반환."""
    df = places_df.copy()
    df["distance_km"] = df.apply(
        lambda r: haversine_km(user_lat, user_lon, r["latitude"], r["longitude"]),
        axis=1,
    )
    return df
