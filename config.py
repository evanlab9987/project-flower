"""
🌸 프로젝트 꽃 - Streamlit MVP

실행: streamlit run app.py

구조:
- Sidebar 메뉴로 5개 페이지 전환
- Google Sheets 데이터 소스
- 캐시 60초 자동 갱신 + 수동 새로고침 버튼
"""
from datetime import datetime
import pandas as pd
import streamlit as st

from config import (
    APP_TITLE,
    APP_SUBTITLE,
    CITY_COORDS,
    MAX_NEARBY_RADIUS_KM,
    SHEET_EDIT_URL,
)
from utils.loader import (
    load_all_data,
    clear_cache,
    get_flowers,
    get_places,
    get_themes,
    get_flower_place,
    get_place_theme,
)
from utils.recommend import (
    get_blooming_flowers,
    places_by_flower,
    places_by_region,
    places_by_theme,
    nearby_places,
    is_blooming,
)


# ============================================================
# 페이지 설정
# ============================================================
st.set_page_config(
    page_title="프로젝트 꽃",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 데이터 로드
# ============================================================
try:
    data = load_all_data()
    flowers = get_flowers(data)
    places = get_places(data)
    themes = get_themes(data)
    flower_place = get_flower_place(data)
    place_theme = get_place_theme(data)
except Exception as e:
    st.error(f"❌ 데이터 로드 실패: {e}")
    st.info("Google Sheets 공유 설정이 '링크가 있는 모든 사용자'로 되어 있는지 확인하세요.")
    st.stop()


# ============================================================
# 공통 UI 함수
# ============================================================
def render_place_card(place_row, extra_info: str = ""):
    """장소 카드 공통 렌더러."""
    with st.container(border=True):
        col1, col2 = st.columns([1, 3])
        with col1:
            if pd.notna(place_row.get("image_url")):
                st.image(place_row["image_url"], use_container_width=True)
        with col2:
            st.markdown(f"### {place_row['name']}")
            st.caption(
                f"📍 {place_row['region_sido']} {place_row['region_sigungu']} "
                f"· {place_row['place_type']}"
            )
            if pd.notna(place_row.get("description")):
                st.write(place_row["description"])

            # 속성 태그
            tags = []
            if place_row.get("has_parking") == 1:
                tags.append("🅿️ 주차가능")
            if place_row.get("is_flat") == 1:
                tags.append("♿ 평탄")
            fee = place_row.get("entrance_fee", 0)
            if fee == 0:
                tags.append("🆓 무료")
            elif pd.notna(fee):
                tags.append(f"💰 {int(fee):,}원")

            if tags:
                st.caption(" · ".join(tags))

            if extra_info:
                st.info(extra_info)


def render_flower_card(flower_row, is_peak: bool = False):
    """꽃 카드 공통 렌더러."""
    with st.container(border=True):
        if pd.notna(flower_row.get("image_url")):
            st.image(flower_row["image_url"], use_container_width=True)

        peak_badge = " 🔥 절정" if is_peak else ""
        st.markdown(f"### {flower_row['name_ko']}{peak_badge}")
        st.caption(f"_{flower_row.get('name_en', '')}_")

        st.write(
            f"📆 **{flower_row['bloom_start_month']}월 ~ {flower_row['bloom_end_month']}월**"
            f" (절정 {flower_row['peak_month']}월)"
        )
        st.write(f"🎨 {flower_row['color']}")
        if pd.notna(flower_row.get("description")):
            st.caption(flower_row["description"])


# ============================================================
# 사이드바
# ============================================================
with st.sidebar:
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)

    menu = st.radio(
        "메뉴",
        [
            "🏠 홈 (이달의 꽃)",
            "🌸 꽃 둘러보기",
            "📍 지역별 명소",
            "🏷️ 테마 추천",
            "🧭 내 근처",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    # 데이터 새로고침 (발표 시연용)
    if st.button("🔄 데이터 새로고침", use_container_width=True):
        clear_cache()
        st.rerun()

    st.caption(f"📊 꽃 {len(flowers)}종 · 장소 {len(places)}곳")
    st.caption(f"[📝 데이터 시트 열기]({SHEET_EDIT_URL})")


# ============================================================
# 페이지: 홈
# ============================================================
if menu == "🏠 홈 (이달의 꽃)":
    current_month = datetime.now().month

    st.title(f"📅 {current_month}월, 지금 피는 꽃")
    st.caption("현재 개화 중인 대표 꽃들을 모아봤어요")

    blooming = get_blooming_flowers(flowers, current_month)

    if blooming.empty:
        st.warning("현재 월에 등록된 꽃 데이터가 없습니다.")
    else:
        # 꽃 카드 (4개씩 한 줄)
        flowers_list = list(blooming.iterrows())
        for i in range(0, len(flowers_list), 4):
            cols = st.columns(4)
            for j, (_, f) in enumerate(flowers_list[i : i + 4]):
                with cols[j]:
                    render_flower_card(f, is_peak=bool(f["is_peak"]))

        st.divider()

        # 테마 바로가기
        st.subheader("🎯 테마별 바로가기")
        theme_cols = st.columns(len(themes))
        for i, (_, t) in enumerate(themes.iterrows()):
            with theme_cols[i]:
                st.info(f"{t.get('icon', '🏷️')} **{t['theme_name']}**\n\n{t['description']}")


# ============================================================
# 페이지: 꽃 둘러보기
# ============================================================
elif menu == "🌸 꽃 둘러보기":
    st.title("🌸 꽃 둘러보기")

    # 현재 피는 꽃 먼저 표시
    current_month = datetime.now().month
    flowers_sorted = flowers.copy()
    flowers_sorted["blooming_now"] = flowers_sorted.apply(
        lambda r: is_blooming(r, current_month), axis=1
    )
    flowers_sorted = flowers_sorted.sort_values(
        ["blooming_now", "peak_month"], ascending=[False, True]
    )

    flower_options = [
        f"{'🌸 ' if r['blooming_now'] else ''}{r['name_ko']} "
        f"({r['bloom_start_month']}~{r['bloom_end_month']}월)"
        for _, r in flowers_sorted.iterrows()
    ]
    flower_ids = flowers_sorted["flower_id"].tolist()

    selected_idx = st.selectbox(
        "꽃 선택 (🌸 = 지금 개화 중)",
        range(len(flower_options)),
        format_func=lambda i: flower_options[i],
    )
    selected_flower_id = flower_ids[selected_idx]
    selected = flowers[flowers["flower_id"] == selected_flower_id].iloc[0]

    st.divider()

    # 꽃 정보
    col1, col2 = st.columns([1, 2])
    with col1:
        if pd.notna(selected.get("image_url")):
            st.image(selected["image_url"], use_container_width=True)
    with col2:
        st.header(selected["name_ko"])
        st.caption(f"_{selected.get('name_en', '')} · {selected.get('scientific_name', '')}_")

        st.write(f"📆 **개화**: {selected['bloom_start_month']}월 ~ {selected['bloom_end_month']}월")
        st.write(f"🔥 **절정**: {selected['peak_month']}월")
        st.write(f"🎨 **색상**: {selected['color']}")

        if is_blooming(selected, current_month):
            st.success("✅ 지금 피고 있어요!")
        else:
            st.info(f"💡 {selected['bloom_start_month']}월부터 볼 수 있어요")

        if pd.notna(selected.get("description")):
            st.write(selected["description"])

    st.divider()

    # 관련 장소
    st.subheader("📍 이 꽃을 볼 수 있는 명소")
    related = places_by_flower(selected_flower_id, places, flower_place)

    if related.empty:
        st.info("등록된 명소가 없습니다.")
    else:
        st.caption(f"총 {len(related)}곳")
        for _, p in related.iterrows():
            note = p.get("note", "")
            render_place_card(p, extra_info=f"💡 {note}" if pd.notna(note) and note else "")


# ============================================================
# 페이지: 지역별 명소
# ============================================================
elif menu == "📍 지역별 명소":
    st.title("📍 지역별 꽃 명소")

    sido_list = sorted(places["region_sido"].unique())
    col1, col2 = st.columns(2)
    with col1:
        selected_sido = st.selectbox("시/도 선택", sido_list)
    with col2:
        only_blooming = st.checkbox("지금 피는 꽃이 있는 곳만 보기", value=False)

    result = places_by_region(places, selected_sido)

    if only_blooming:
        current_month = datetime.now().month
        blooming_ids = set(get_blooming_flowers(flowers, current_month)["flower_id"])
        fp_now = flower_place[flower_place["flower_id"].isin(blooming_ids)]
        blooming_place_ids = set(fp_now["place_id"])
        result = result[result["place_id"].isin(blooming_place_ids)]

    st.caption(f"{selected_sido} 꽃 명소 {len(result)}곳")
    st.divider()

    if result.empty:
        st.info("해당 조건의 장소가 없습니다.")
    else:
        for _, p in result.iterrows():
            # 이 장소의 관련 꽃 찾기
            fp_here = flower_place[flower_place["place_id"] == p["place_id"]]
            flower_ids_here = fp_here["flower_id"].tolist()
            flowers_here = flowers[flowers["flower_id"].isin(flower_ids_here)]["name_ko"].tolist()
            flower_info = (
                f"🌸 볼 수 있는 꽃: {', '.join(flowers_here)}"
                if flowers_here
                else ""
            )
            render_place_card(p, extra_info=flower_info)


# ============================================================
# 페이지: 테마 추천
# ============================================================
elif menu == "🏷️ 테마 추천":
    st.title("🏷️ 테마별 추천")

    theme_cols = st.columns(len(themes))
    theme_names = themes["theme_name"].tolist()
    selected_theme_name = st.radio(
        "테마 선택",
        theme_names,
        horizontal=True,
        label_visibility="collapsed",
    )

    selected_theme = themes[themes["theme_name"] == selected_theme_name].iloc[0]
    st.info(f"{selected_theme.get('icon', '🏷️')} **{selected_theme['theme_name']}** — {selected_theme['description']}")

    result = places_by_theme(selected_theme["theme_id"], places, place_theme)
    st.caption(f"추천 장소 {len(result)}곳 (적합도 높은 순)")
    st.divider()

    for _, p in result.iterrows():
        stars = "⭐" * int(p["fit_score"])
        render_place_card(p, extra_info=f"적합도: {stars} ({int(p['fit_score'])}/5)")


# ============================================================
# 페이지: 내 근처
# ============================================================
elif menu == "🧭 내 근처":
    st.title("🧭 내 근처 꽃 명소")
    st.caption("위치를 입력하면 가까운 순서로 보여드려요")

    input_mode = st.radio(
        "위치 입력 방식",
        ["주요 도시 선택", "위경도 직접 입력"],
        horizontal=True,
    )

    if input_mode == "주요 도시 선택":
        city = st.selectbox("도시 선택", list(CITY_COORDS.keys()), index=list(CITY_COORDS.keys()).index("창원"))
        user_lat, user_lon = CITY_COORDS[city]
        st.caption(f"선택: {city} ({user_lat}, {user_lon})")
    else:
        col1, col2 = st.columns(2)
        with col1:
            user_lat = st.number_input("위도", value=35.2271, format="%.4f")
        with col2:
            user_lon = st.number_input("경도", value=128.6811, format="%.4f")

    max_km = st.slider("검색 반경 (km)", 10, 500, MAX_NEARBY_RADIUS_KM, step=10)
    limit = st.slider("최대 결과 수", 3, 20, 10)

    if st.button("🔍 찾기", type="primary"):
        result = nearby_places(user_lat, user_lon, places, max_km=max_km, limit=limit)

        if result.empty:
            st.warning(f"{max_km}km 이내에 등록된 장소가 없습니다. 반경을 늘려보세요.")
        else:
            st.success(f"✅ 가까운 순으로 {len(result)}곳 찾았어요")
            for _, p in result.iterrows():
                render_place_card(p, extra_info=f"📏 거리: {p['distance_km']:.1f}km")


# ============================================================
# 푸터
# ============================================================
st.divider()
st.caption(
    f"🌸 프로젝트 꽃 MVP | 데이터 소스: Google Sheets | "
    f"최종 갱신: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
)
