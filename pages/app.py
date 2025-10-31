import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="수산물 무역 분석", layout="wide")
st.title('수산물 무역 분석: 2023-2024 전년도 대비 분석')

# GitHub에서 직접 로드
data_path = 'trade2023-2024.csv'

try:
    df = pd.read_csv(data_path, encoding='utf-8')
    
    # 데이터 정제
    df_clean = df[df['기간'] != '총계'].copy()
    df_clean['기간'] = pd.to_numeric(df_clean['기간'], errors='coerce')
    df_clean = df_clean.dropna(subset=['기간'])
    df_clean['기간'] = df_clean['기간'].astype(int)
    
    # 단위 변환 함수 (천 달러 → 표시 형식)
    def format_currency(value):
        """천 달러를 읽기 쉬운 형식으로 변환"""
        if value >= 1_000_000:
            return f"${value/1_000_000:,.1f}B"
        elif value >= 1_000:
            return f"${value/1_000:,.1f}M"
        else:
            return f"${value:,.0f}K"
    
    def format_currency_num(value):
        """숫자로만 표시 (백만 단위)"""
        return f"${value/1_000:,.0f}M"
    
    years = sorted(df_clean['기간'].unique())
    st.sidebar.write(f"**분석 기간**: {years[0]}년 ~ {years[-1]}년")
    st.sidebar.write(f"**단위**: 금액(천 달러), 건수(건)")
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["📊 연도별 비교", "🌍 국가별 분석", "📈 전년도 대비"])
    
    with tab1:
        st.subheader("연도별 수출입 무역량")
        
        yearly = df_clean.groupby('기간')[['수출 금액', '수입 금액', '무역수지']].sum().reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(yearly, x='기간', y=['수출 금액', '수입 금액'], 
                         barmode='group', 
                         title='연도별 수출/수입 금액',
                         labels={'기간': '연도', 'value': '금액 (천 달러)'},
                         text_auto=',.0f')
            fig1.update_traces(textposition='outside')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.line(yearly, x='기간', y='무역수지', 
                          title='연도별 무역수지',
                          labels={'기간': '연도', '무역수지': '무역수지 (천 달러)'},
                          markers=True,
                          line_shape='linear')
            fig2.add_hline(y=0, line_dash="dash", line_color="red")
            st.plotly_chart(fig2, use_container_width=True)
        
        st.write("**연도별 상세 통계 (단위: 천 달러):**")
        yearly_display = yearly.copy()
        yearly_display['수출 금액'] = yearly_display['수출 금액'].apply(format_currency_num)
        yearly_display['수입 금액'] = yearly_display['수입 금액'].apply(format_currency_num)
        yearly_display['무역수지'] = yearly_display['무역수지'].apply(format_currency_num)
        st.dataframe(yearly_display.rename(columns={
            '기간': '연도', '수출 금액': '수출액', '수입 금액': '수입액'
        }), use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("국가별 수출입 분석")
        
        select_year = st.selectbox("분석 연도 선택:", sorted(df_clean['기간'].unique(), reverse=True))
        
        country_data = df_clean[df_clean['기간'] == select_year].sort_values('수출 금액', ascending=False)
        
        top_n = st.slider("상위 N개국:", min_value=5, max_value=30, value=15)
        country_top = country_data.head(top_n)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig3 = px.bar(country_top, x='국가', y='수출 금액', 
                         title=f'{select_year}년 주요 수출 대상국',
                         labels={'국가': '국가', '수출 금액': '수출액 (천 달러)'},
                         color='수출 금액',
                         color_continuous_scale='Blues',
                         text_auto=',.0f')
            fig3.update_traces(textposition='outside')
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            fig4 = px.bar(country_top, x='국가', y='수입 금액', 
                         title=f'{select_year}년 주요 수입 원산국',
                         labels={'국가': '국가', '수입 금액': '수입액 (천 달러)'},
                         color='수입 금액',
                         color_continuous_scale='Reds',
                         text_auto=',.0f')
            fig4.update_traces(textposition='outside')
            st.plotly_chart(fig4, use_container_width=True)
        
        st.write(f"**{select_year}년 국가별 무역 상위 {top_n}개국:**")
        country_display = country_top[['국가', '수출 금액', '수입 금액', '무역수지', '수출 건수', '수입 건수']].copy()
        country_display['수출 금액'] = country_display['수출 금액'].apply(format_currency_num)
        country_display['수입 금액'] = country_display['수입 금액'].apply(format_currency_num)
        country_display['무역수지'] = country_display['무역수지'].apply(format_currency_num)
        st.dataframe(country_display.rename(columns={
            '국가': '국가', '수출 금액': '수출액', '수입 금액': '수입액', 
            '무역수지': '수지', '수출 건수': '수출건수', '수입 건수': '수입건수'
        }), use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader("2023년 vs 2024년 전년도 대비 분석")
        
        if len(years) >= 2:
            # 연도별 비교
            yearly_change = df_clean.groupby('기간')[['수출 금액', '수입 금액', '수출 건수', '수입 건수']].sum().reset_index()
            yearly_change['수출_증감률(%)'] = yearly_change['수출 금액'].pct_change() * 100
            yearly_change['수입_증감률(%)'] = yearly_change['수입 금액'].pct_change() * 100
            yearly_change['수출건수_증감률(%)'] = yearly_change['수출 건수'].pct_change() * 100
            yearly_change['수입건수_증감률(%)'] = yearly_change['수입 건수'].pct_change() * 100
            
            # 연도별 증감률 시각화
            fig5_data = yearly_change[yearly_change['기간'] == 2024][['수출_증감률(%)', '수입_증감률(%)']].values[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("수출액 증감률", f"{yearly_change[yearly_change['기간'] == 2024]['수출_증감률(%)'].values[0]:+.2f}%", 
                         help="2024년 vs 2023년")
            with col2:
                st.metric("수입액 증감률", f"{yearly_change[yearly_change['기간'] == 2024]['수입_증감률(%)'].values[0]:+.2f}%",
                         help="2024년 vs 2023년")
            with col3:
                st.metric("수출건수 증감률", f"{yearly_change[yearly_change['기간'] == 2024]['수출건수_증감률(%)'].values[0]:+.2f}%",
                         help="2024년 vs 2023년")
            with col4:
                st.metric("수입건수 증감률", f"{yearly_change[yearly_change['기간'] == 2024]['수입건수_증감률(%)'].values[0]:+.2f}%",
                         help="2024년 vs 2023년")
            
            # 국가별 성장률 분석
            st.subheader("국가별 수출 성장률 (2024 vs 2023)")
            
            country_2023 = df_clean[df_clean['기간'] == 2023][['국가', '수출 금액']].copy()
            country_2024 = df_clean[df_clean['기간'] == 2024][['국가', '수출 금액']].copy()
            
            country_growth = country_2023.merge(country_2024, on='국가', suffixes=('_2023', '_2024'))
            country_growth['수출_성장률(%)'] = ((country_growth['수출 금액_2024'] - country_growth['수출 금액_2023']) / 
                                             country_growth['수출 금액_2023'] * 100)
            country_growth = country_growth.sort_values('수출_성장률(%)', ascending=False)
            
            # 상위/하위 성장률 국가
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**수출 성장 상위 10개국:**")
                growth_top = country_growth.head(10)[['국가', '수출_성장률(%)', '수출 금액_2024']].copy()
                growth_top['수출_성장률(%)'] = growth_top['수출_성장률(%)'].apply(lambda x: f"{x:+.1f}%")
                growth_top['수출 금액_2024'] = growth_top['수출 금액_2024'].apply(format_currency_num)
                st.dataframe(growth_top.rename(columns={
                    '국가': '국가', '수출_성장률(%)': '성장률', '수출 금액_2024': '2024년 수출액'
                }), use_container_width=True, hide_index=True)
            
            with col2:
                st.write("**수출 성장 하위 10개국 (감소 상위):**")
                growth_bottom = country_growth.tail(10)[['국가', '수출_성장률(%)', '수출 금액_2024']].copy()
                growth_bottom['수출_성장률(%)'] = growth_bottom['수출_성장률(%)'].apply(lambda x: f"{x:+.1f}%")
                growth_bottom['수출 금액_2024'] = growth_bottom['수출 금액_2024'].apply(format_currency_num)
                st.dataframe(growth_bottom.rename(columns={
                    '국가': '국가', '수출_성장률(%)': '성장률', '수출 금액_2024': '2024년 수출액'
                }), use_container_width=True, hide_index=True)
            
            # 성장률 분포 차트
            fig6 = px.histogram(country_growth, x='수출_성장률(%)', nbins=30,
                              title='국가별 수출 성장률 분포',
                              labels={'수출_성장률(%)': '성장률 (%)', 'count': '국가 수'},
                              color_discrete_sequence=['#636EFA'])
            fig6.add_vline(x=0, line_dash="dash", line_color="red")
            st.plotly_chart(fig6, use_container_width=True)

        else:
            st.info("💡 전년도 대비 분석을 위해 2개 이상의 연도 데이터가 필요합니다.")

except FileNotFoundError:
    st.error(f"❌ 파일을 찾을 수 없습니다: {data_path}")
    st.info("📝 GitHub에서 'trade2023-2024.csv'를 같은 디렉토리에 놓으세요.")
    st.code("""
Tradepg/
├── app.py
├── requirements.txt
└── trade2023-2024.csv
    """)
