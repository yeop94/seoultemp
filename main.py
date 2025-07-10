import streamlit as st
import pandas as pd
import datetime
import os
import plotly.express as px

st.set_page_config(page_title="어제 기온 vs 역대 기온", layout="centered")
st.title("📈 어제는 얼마나 더웠을까?")

# 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요 (기온 데이터, CP949 인코딩)", type="csv")

# 업로드된 파일이 없으면 기본 파일 사용
if not uploaded_file:
    for fname in os.listdir("."):
        if fname.startswith("ta") and fname.endswith(".csv"):
            uploaded_file = fname
            break

if uploaded_file:
    try:
        file_path = uploaded_file if isinstance(uploaded_file, str) else uploaded_file

        df = pd.read_csv(file_path, encoding="cp949", skiprows=7)
        df["날짜"] = df["날짜"].str.strip()
        df["날짜"] = pd.to_datetime(df["날짜"], format="%Y-%m-%d")

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        st.subheader(f"🔍 분석 대상 날짜: {yesterday.strftime('%Y-%m-%d')}")

        df_yesterday = df[df["날짜"] == pd.to_datetime(yesterday)]
        if df_yesterday.empty:
            st.warning("해당 날짜의 데이터가 없습니다.")
        else:
            # 연도 선택 슬라이더 추가
            year_min = df["날짜"].dt.year.min()
            year_max = df["날짜"].dt.year.max()
            selected_years = st.slider("비교할 연도 범위", min_value=year_min, max_value=year_max, value=(year_min, year_max))

            same_day_df = df[(df["날짜"].dt.strftime("%m-%d") == yesterday.strftime("%m-%d")) &
                             (df["날짜"].dt.year >= selected_years[0]) &
                             (df["날짜"].dt.year <= selected_years[1])]

            highest_temp_yesterday = df_yesterday["최고기온(℃)"].values[0]
            highest_ranks = same_day_df.sort_values("최고기온(℃)", ascending=False).reset_index(drop=True)
            highest_rank = highest_ranks[highest_ranks["날짜"] == pd.to_datetime(yesterday)].index[0] + 1
            highest_percentile = 100 * (highest_rank / len(highest_ranks))

            lowest_temp_yesterday = df_yesterday["최저기온(℃)"].values[0]
            lowest_ranks = same_day_df.sort_values("최저기온(℃)").reset_index(drop=True)
            lowest_rank = lowest_ranks[lowest_ranks["날짜"] == pd.to_datetime(yesterday)].index[0] + 1
            lowest_percentile = 100 * (lowest_rank / len(lowest_ranks))

            # 역대 최고 및 최저 1위 정보 출력
            total_high = len(highest_ranks)
            total_low = len(lowest_ranks)
            high_percent = 100 * highest_rank / total_high
            low_percent = 100 * lowest_rank / total_low
            record_high = same_day_df.sort_values("최고기온(℃)", ascending=False).iloc[0]
            record_low = same_day_df.sort_values("최저기온(℃)").iloc[0]

            st.markdown("### 🏆 역대 기록")
            st.write(f"📈 **역대 최고기온**: {record_high['최고기온(℃)']}℃ on {record_high['날짜'].date()}")
            st.write(f"➡️ 어제보다 {(record_high['최고기온(℃)'] - highest_temp_yesterday):.1f}℃ {'높았습니다' if record_high['최고기온(℃)'] > highest_temp_yesterday else '낮았습니다'}")
            st.write(f"📊 어제는 역대 {total_high}일 중 **상위 {high_percent:.1f}%** 더운 날")
            st.write(f"❄️ **역대 최저기온**: {record_low['최저기온(℃)']}℃ on {record_low['날짜'].date()}")
            st.write(f"➡️ 어제보다 {(record_low['최저기온(℃)'] - lowest_temp_yesterday):.1f}℃ {'낮았습니다' if record_low['최저기온(℃)'] < lowest_temp_yesterday else '높았습니다'}")
            st.write(f"📉 어제는 역대 {total_low}일 중 **상위 {low_percent:.1f}%** 추운 날")

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

            st.subheader("📊 최고기온 추이 (Plotly)")
            fig_high = px.line(same_day_df.sort_values("날짜"), x="날짜", y="최고기온(℃)",
                               title="역대 7월 {}일 최고기온 추이".format(yesterday.day))
            fig_high.add_scatter(x=[yesterday], y=[highest_temp_yesterday], mode='markers+text',
                                 name='어제', marker=dict(size=12, color='red'),
                                 text=["어제"], textposition="top center")
            st.plotly_chart(fig_high)

            st.markdown("---")
            st.subheader("❄️ 역대 동일 날짜 중 가장 추웠던 날 Top 5")
            st.dataframe(lowest_ranks.head(5).reset_index(drop=True))

            st.subheader("📊 최저기온 추이 (Plotly)")
            fig_low = px.line(same_day_df.sort_values("날짜"), x="날짜", y="최저기온(℃)",
                              title="역대 7월 {}일 최저기온 추이".format(yesterday.day))
            fig_low.add_scatter(x=[yesterday], y=[lowest_temp_yesterday], mode='markers+text',
                                name='어제', marker=dict(size=12, color='blue'),
                                text=["어제"], textposition="top center")
            st.plotly_chart(fig_low)

            st.markdown("---")
            st.subheader("📅 최근 기간 평균 기온 분석")
            day_range = st.slider("비교할 최근 일 수를 선택하세요", min_value=3, max_value=30, value=7)
            start_day = pd.to_datetime(today) - pd.Timedelta(days=day_range)
            recent_df = df[(df["날짜"] >= start_day) & (df["날짜"] < pd.to_datetime(today))]

            avg_high = recent_df["최고기온(℃)"].mean()
            avg_low = recent_df["최저기온(℃)"].mean()
            avg_avg = recent_df["평균기온(℃)"].mean()

            st.write(f"최근 {day_range}일간 평균 최고기온: **{avg_high:.2f}℃**")
            st.write(f"최근 {day_range}일간 평균 최저기온: **{avg_low:.2f}℃**")
            st.write(f"최근 {day_range}일간 평균기온: **{avg_avg:.2f}℃**")

            historical_trend = recent_mean_df.groupby(df["날짜"].dt.strftime("%m-%d"))[["최고기온(℃)", "평균기온(℃)", "최저기온(℃)"]].mean().reset_index()
            historical_trend["날짜"] = [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(day_range, 0, -1)]
            historical_trend = pd.melt(historical_trend, id_vars="날짜", var_name="기온유형", value_name="역대 평균")
            recent_plot_df = pd.melt(recent_df.sort_values("날짜"), id_vars="날짜", value_vars=["최고기온(℃)", "평균기온(℃)", "최저기온(℃)"], var_name="기온유형", value_name="최근 측정")

            combined = pd.merge(recent_plot_df, historical_trend, on=["날짜", "기온유형"], how="left")
            fig_combined = px.line(combined, x="날짜", y="최근 측정", color="기온유형",
                                   title=f"최근 {day_range}일간 기온 변화 vs 역대 평균 추이")
            for col in combined["기온유형"].unique():
                fig_combined.add_scatter(x=combined[combined["기온유형"] == col]["날짜"],
                                         y=combined[combined["기온유형"] == col]["역대 평균"],
                                         mode="lines", name=f"{col} (역대 평균)", line=dict(dash="dot"))
            st.plotly_chart(fig_combined)

            # 최고기온 vs 최저기온 스캐터플롯
            scatter_df = same_day_df.copy()
            scatter_df["날짜"] = scatter_df["날짜"].dt.strftime("%Y-%m-%d")
            scatter_df["어제"] = scatter_df["날짜"] == str(yesterday)
            record_label = scatter_df.loc[scatter_df["최고기온(℃)"].idxmax(), "날짜"]

            fig_scatter = px.scatter(scatter_df, x="최고기온(℃)", y="최저기온(℃)", color="어제",
                                     hover_name="날짜", title="📍 최고기온 vs 최저기온 분포",
                                     labels={"어제": "어제 여부"})

            st.plotly_chart(fig_scatter)

            recent_mean_df = df[df["날짜"].dt.strftime("%m-%d").isin(
                [(today - datetime.timedelta(days=i)).strftime("%m-%d") for i in range(1, day_range + 1)])]

            hist_avg_high = recent_mean_df.groupby(df["날짜"].dt.strftime("%m-%d"))["최고기온(℃)"].mean().mean()
            hist_avg_low = recent_mean_df.groupby(df["날짜"].dt.strftime("%m-%d"))["최저기온(℃)"].mean().mean()
            hist_avg_avg = recent_mean_df.groupby(df["날짜"].dt.strftime("%m-%d"))["평균기온(℃)"].mean().mean()

            st.markdown(f"### 🧮 최근 {day_range}일 평균 vs 역대 {day_range}일 평균")
            st.write(f"📊 **최근 {day_range}일 평균 최고기온**: {avg_high:.2f}℃ vs **역대 평균**: {hist_avg_high:.2f}℃")
            st.write(f"➡️ {(avg_high - hist_avg_high):.2f}℃ {'더웠습니다' if avg_high > hist_avg_high else '덜 더웠습니다'}")
            st.write(f"🌙 **최근 {day_range}일 평균 최저기온**: {avg_low:.2f}℃ vs **역대 평균**: {hist_avg_low:.2f}℃")
            st.write(f"➡️ {(avg_low - hist_avg_low):.2f}℃ {'더웠습니다' if avg_low > hist_avg_low else '덜 더웠습니다'}")
            st.write(f"🌡️ **최근 {day_range}일 평균기온**: {avg_avg:.2f}℃ vs **역대 평균**: {hist_avg_avg:.2f}℃")
            st.write(f"➡️ {(avg_avg - hist_avg_avg):.2f}℃ {'더웠습니다' if avg_avg > hist_avg_avg else '덜 더웠습니다'}")

           # 백분위 계산
            msg = (
            f"📈 평균기온 기준으로 최근 {day_range}일은 역대 {len(temp_diff_df)}개 연중 동일 기간 중 "
            f"상위 {100 - percentile_rank:.1f}% 더운 편입니다\n"
            f"(전체 {len(temp_diff_df)}일 중 {rank_number}위)"
            )
            st.write(msg)




    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
