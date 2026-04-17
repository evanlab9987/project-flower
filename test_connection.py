"""
Google Sheets 연결 테스트 스크립트
먼저 이걸 실행해서 구글 시트가 잘 읽히는지 확인한 후
Streamlit 앱으로 넘어가세요.

실행: python test_connection.py
"""
import pandas as pd

SHEET_ID = "1sIDbnDMpTE9f7dTm4_zWYn5k-3QHkxHnk_Qz5_iYlT0"

GIDS = {
    "flowers": 0,
    "places": 1382239227,
    "flower_place": 1877529906,
    "themes": 223886316,
    "place_theme": 1345396072,
}


def csv_url(sheet_id: str, gid: int) -> str:
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def main():
    print("=" * 60)
    print("🔍 Google Sheets 연결 테스트")
    print("=" * 60)

    all_ok = True
    dfs = {}

    for name, gid in GIDS.items():
        url = csv_url(SHEET_ID, gid)
        try:
            df = pd.read_csv(url)
            dfs[name] = df
            print(f"✅ {name:15s} | {len(df):3d}행 × {len(df.columns):2d}열")
        except Exception as e:
            all_ok = False
            print(f"❌ {name:15s} | 오류: {type(e).__name__}: {str(e)[:80]}")

    print("\n" + "=" * 60)
    if all_ok:
        print("🎉 전체 5개 시트 정상 연결!")
        print("\n📊 데이터 현황:")
        print(f"  - 꽃: {len(dfs['flowers'])}종")
        print(f"  - 장소: {len(dfs['places'])}곳")
        print(f"  - 꽃-장소 매핑: {len(dfs['flower_place'])}건")
        print(f"  - 테마: {len(dfs['themes'])}개")
        print(f"  - 장소-테마 매핑: {len(dfs['place_theme'])}건")

        print("\n🌸 꽃 데이터 미리보기 (상위 3건):")
        print(dfs["flowers"][["flower_id", "name_ko", "bloom_start_month", "bloom_end_month"]].head(3).to_string(index=False))

        print("\n📍 장소 데이터 미리보기 (상위 3건):")
        print(dfs["places"][["place_id", "name", "region_sido"]].head(3).to_string(index=False))

        print("\n✅ 다음 단계: streamlit run app.py 실행")
    else:
        print("⚠️ 연결 실패")
        print("\n점검 항목:")
        print("1. 스프레드시트 공유 설정이 '링크가 있는 모든 사용자'로 되어 있는지")
        print("2. 인터넷 연결이 정상인지")
        print("3. SHEET_ID와 gid가 정확한지")


if __name__ == "__main__":
    main()
