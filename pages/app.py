import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="수산물 무역 분석", layout="wide")
st.title('수산물 무역량 시각화 및 전년도 대비 분석')

uploaded = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded, encoding='utf-8')
    
    # 데이터 정제
    df_clean = df[df['기간'] != '총계'].copy()
    df_clean['기간'] = pd.to_numeric(df_clean['기간'], errors='coerce')
    df_clean = df_clean.dropna(subset=['기간'])
    df_clean['기간'] = df_clean['기간'].astype(int)
    
    years = sorted(df_clean['기간'].unique())
    st.sidebar.write(f"**데이터 포함 연도**: {years[0]} ~ {years[-1]}")
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["📊 연도별 비교", "🌍 국가별 분석", "📈 전년도 대비"])
    
    with tab1:
        st.subheader("연도별 수출입 무역량")
        
        yearly = df_clean.groupby('기간')[['수출 금액', '수입 금액']].sum().reset_index()
        yearly['무역수지'] = yearly['수출 금액'] - yearly['수입 금액']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(yearly, x='기간', y=['수출 금액', '수입 금액'], 
                         barmode='group', title='연도별 수출/수입 금액',
                         labels={'기간': '연도', 'value': '금액 (USD)'})
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.line(yearly, x='기간', y='무역수지', 
                          title='연도별 무역수지', markers=True,
                          labels={'기간': '연도', '무역수지': '무역수지 (USD)'})
            st.plotly_chart(fig2, use_container_width=True)
        
        st.write("**연도별 상세 통계:**")
        yearly_display = yearly.copy()
        yearly_display['수출 금액'] = yearly_display['수출 금액'].apply(lambda x: f"${x:,.0f}")
        yearly_display['수입 금액'] = yearly_display['수입 금액'].apply(lambda x: f"${x:,.0f}")
        yearly_display['무역수지'] = yearly_display['무역수지'].apply(lambda x: f"${x:,.0f}")
        st.dataframe(yearly_display, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("국가별 수출입 분석")
        
        select_year = st.selectbox("연도 선택:", sorted(df_clean['기간'].unique(), reverse=True))
        
        country_data = df_clean[df_clean['기간'] == select_year].sort_values('수출 금액', ascending=False)
        
        top_n = st.slider("상위 N개국:", min_value=5, max_value=30, value=10)
        country_top = country_data.head(top_n)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig3 = px.bar(country_top, x='국가', y='수출 금액', title=f'{select_year}년 주요 수출 대상국',
                         labels={'국가': '국가', '수출 금액': '수출 금액 (USD)'})
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            fig4 = px.bar(country_top, x='국가', y='수입 금액', title=f'{select_year}년 주요 수입 원산국',
                         labels={'국가': '국가', '수입 금액': '수입 금액 (USD)'})
            st.plotly_chart(fig4, use_container_width=True)
        
        st.write(f"**{select_year}년 국가별 무역 상위 {top_n}개국:**")
        country_display = country_top[['국가', '수출 금액', '수입 금액', '무역수지', '수출 건수', '수입 건수']].copy()
        country_display['수출 금액'] = country_display['수출 금액'].apply(lambda x: f"${x:,.0f}")
        country_display['수입 금액'] = country_display['수입 금액'].apply(lambda x: f"${x:,.0f}")
        country_display['무역수지'] = country_display['무역수지'].apply(lambda x: f"${x:,.0f}")
        st.dataframe(country_display, use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader("전년도 대비 증감 분석")
        
        if len(years) >= 2:
            yearly_change = df_clean.groupby('기간')[['수출 금액', '수입 금액', '무역수지']].sum().reset_index()
            yearly_change['수출_증감률(%)'] = yearly_change['수출 금액'].pct_change() * 100
            yearly_change['수입_증감률(%)'] = yearly_change['수입 금액'].pct_change() * 100
            yearly_change['무역수지_증감률(%)'] = yearly_change['무역수지'].pct_change() * 100
            
            fig5 = px.line(yearly_change.dropna(), x='기간', y=['수출_증감률(%)', '수입_증감률(%)'],
                          title='연도별 전년도 대비 수출/수입 증감률', markers=True,
                          labels={'기간': '연도', 'value': '증감률 (%)'})
            st.plotly_chart(fig5, use_container_width=True)
            
            st.write("**전년도 대비 증감률 통계:**")
            change_display = yearly_change[['기간', '수출_증감률(%)', '수입_증감률(%)', '무역수지_증감률(%)']].dropna()
            change_display['수출_증감률(%)'] = change_display['수출_증감률(%)'].apply(lambda x: f"{x:+.2f}%")
            change_display['수입_증감률(%)'] = change_display['수입_증감률(%)'].apply(lambda x: f"{x:+.2f}%")
            change_display['무역수지_증감률(%)'] = change_display['무역수지_증감률(%)'].apply(lambda x: f"{x:+.2f}%")
            st.dataframe(change_display, use_container_width=True, hide_index=True)
            
            # 국가별 성장률
            st.subheader("국가별 수출 성장률")
            
            if len(years) >= 2:
                year_latest = years[-1]
                year_prev = years[-2]
                
                country_latest = df_clean[df_clean['기간'] == year_latest][['국가', '수출 금액']].copy()
                country_prev = df_clean[df_clean['기간'] == year_prev][['국가', '수출 금액']].copy()
                
                country_growth = country_latest.merge(country_prev, on='국가', suffixes=('_최신', '_전년'))
                country_growth['수출_성장률(%)'] = ((country_growth['수출 금액_최신'] - country_growth['수출 금액_전년']) / country_growth['수출 금액_전년'] * 100)
                country_growth = country_growth.sort_values('수출_성장률(%)', ascending=False)
                
                top_growth = st.slider("상위/하위 N개국:", min_value=5, max_value=20, value=10)
                
                fig6 = px.bar(pd.concat([country_growth.head(top_growth), country_growth.tail(top_growth)]),
                             x='국가', y='수출_성장률(%)', 
                             title=f'{year_latest}년 {year_prev}년 대비 국가별 수출 성장률 (상위/하위 {top_growth}개국)',
                             labels={'국가': '국가', '수출_성장률(%)': '성장률 (%)'})
                st.plotly_chart(fig6, use_container_width=True)
        else:
            st.info("💡 전년도 대비 분석을 위해 2개 이상의 연도 데이터가 필요합니다.")

else:
    st.info("📁 CSV 파일을 업로드하면 자동으로 시각화와 분석이 시작됩니다.")
