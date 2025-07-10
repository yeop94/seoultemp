import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(page_title="어제 기온 vs 역대 기온", layout="centered")
st.title("📈 어제는 얼마나 더웠을까?")

# 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요 (기온 데이터, CP949 인코딩)", type="csv")

# 업로드된 파일이 없으면 기본 파일 사용
if not uploaded_file:
    # 현재 디렉토리에서 'ta'로 시작하는 CSV 파일 자동 탐색
    for fname in os.listdir("."):
        if fname.startswith("ta") and fname.endswith(".csv"):
            uploaded_file = fname
            break

if uploaded_file:
    try:
        # 파일 경로 설정
        file_path = uploaded_file if isinstance(uploaded_file, str) else uploaded_file

        # 데이터 불러오기
        df = pd.read_csv(file_path, encoding="cp949", skiprows=7)
        df["날짜"] = df["날짜"].str.strip()
        df["날짜"] = pd.to_datetime(df["날짜"], format="%Y-%m-%d")

        # 날짜 설정
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        st.subheader(f"🔍 분석 대상 날짜: {yesterday.strftime('%Y-%m-%d')}")

        df_yesterday = df[df["날짜"] == pd.to_datetime(yesterday)]
        if df_yesterday.empty:
            st.warning("해당 날짜의 데이터가 없습니다.")
        else:
            # 동일한 월-일의 과거 데이터 추출
            same_day_df = df[df["날짜"].dt.strftime("%m-%d") == yesterday.strftime("%m-%d")]

            # 최고기온 비교
            highest_temp_yesterday = df_yesterday["최고기온(℃)"].values[0]
            highest_ranks = same_day_df.sort_values("최고기온(℃)", ascending=False).reset_index(drop=True)
            highest_rank = highest_ranks[highest_ranks["날짜"] == pd.to_datetime(yesterday)].index[0] + 1
            highest_percentile = 100 * (1 - highest_rank / len(highest_ranks))

            # 최저기온 비교
            lowest_temp_yesterday = df_yesterday["최저기온(℃)"].values[0]
            lowest_ranks = same_day_df.sort_values("최저기온(℃)").reset_index(drop=True)
            lowest_rank = lowest_ranks[lowest_ranks["날짜"] == pd.to_datetime(yesterday)].index[0] + 1
            lowest_percentile = 100 * (1 - lowest_rank / len(lowest_ranks))

            # 카드 형태 출력
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🌡️ 어제 최고기온", f"{highest_temp_yesterday}℃", f"상위 {highest_percentile:.1f}%")
                st.info(f"역대 7월 {yesterday.day}일 중 **{highest_rank}위**")
            with col2:
                st.metric("🌙 어제 최저기온", f"{lowest_temp_yesterday}℃", f"상위 {lowest_percentile:.1f}%")
                st.info(f"역대 7월 {yesterday.day}일 중 **{lowest_rank}위**")

            st.markdown("---")
            st.subheader("🔥 역대 동일 날짜 중 가장 더웠던 날 Top 5")
            st.dataframe(highest_ranks.head(5).reset_index(drop=True))

            st.subheader("❄️ 역대 동일 날짜 중 가장 추웠던 날 Top 5")
            st.dataframe(lowest_ranks.head(5).reset_index(drop=True))

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
