import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="수산물 무역 분석", layout="wide")
st.title('수산물 무역량 시각화 및 전년도 대비 분석')

# GitHub에서 직접 로드 (또는 로컬 파일)
import os
data_path = 'trade2023-2024.CSV'

try:
    df = pd.read_csv(data_path, encoding='cp949')
    
    # 데이터 정제
    df['기준년월'] = pd.to_datetime(df['기준년월'], format='%Y-%m')
    df['연도'] = df['기준년월'].dt.year
    df['월'] = df['기준년월'].dt.month
    
    # 단위 변환 함수
    def kg_to_ton(kg):
        """킬로그램을 톤으로 변환"""
        return kg / 1000
    
    def usd_to_thousand(usd):
        """달러를 천 달러로 변환"""
        return usd / 1000
    
    def format_unit(value, unit_type):
        """숫자를 읽기 쉬운 형식으로 변환"""
        if unit_type == 'ton':
            if value >= 1_000_000:
                return f"{value/1_000_000:,.1f} 백만 톤"
            elif value >= 1_000:
                return f"{value/1_000:,.1f} 천 톤"
            else:
                return f"{value:,.0f} 톤"
        elif unit_type == 'million_usd':
            if value >= 1_000_000:
                return f"${value/1_000_000:,.1f}B"
            elif value >= 1_000:
                return f"${value/1_000:,.1f}M"
            else:
                return f"${value:,.0f}K"
    
    years = sorted(df['연도'].unique())
    st.sidebar.write(f"**데이터 포함 기간**: {df['기준년월'].min().strftime('%Y.%m')} ~ {df['기준년월'].max().strftime('%Y.%m')}")
    st.sidebar.write(f"**단위**: 무게(톤), 금액(천 달러)")
    
    # 데이터 변환
    df['중량_톤'] = kg_to_ton(df['당월수출입중량(킬로그램)'])
    df['금액_천달러'] = usd_to_thousand(df['당월수출입미화금액(달러)'])
    df['누계중량_톤'] = kg_to_ton(df['당해누계수출입중량(킬로그램)'])
    df['누계금액_천달러'] = usd_to_thousand(df['당해누계수출입미화금액(달러)'])
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["📊 월별 추이", "🌍 국가별 분석", "📈 누적 현황"])
    
    with tab1:
        st.subheader("월별 수출입 무역량 추이")
        
        monthly = df.groupby(['기준년월', '수출입구분명'])[[
            '중량_톤', '금액_천달러'
        ]].sum().reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.line(monthly, x='기준년월', y='중량_톤', color='수출입구분명',
                          title='월별 수출입 중량 추이',
                          labels={'기준년월': '기간', '중량_톤': '중량 (톤)', '수출입구분명': '구분'},
                          markers=True)
            fig1.update_layout(hovermode='x unified')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.line(monthly, x='기준년월', y='금액_천달러', color='수출입구분명',
                          title='월별 수출입 금액 추이',
                          labels={'기준년월': '기간', '금액_천달러': '금액 (천 달러)', '수출입구분명': '구분'},
                          markers=True)
            fig2.update_layout(hovermode='x unified')
            st.plotly_chart(fig2, use_container_width=True)
        
        st.write("**월별 상세 통계:**")
        monthly_display = monthly.copy()
        monthly_display['기준년월'] = monthly_display['기준년월'].dt.strftime('%Y.%m')
        monthly_display['중량_톤'] = monthly_display['중량_톤'].apply(lambda x: format_unit(x, 'ton'))
        monthly_display['금액_천달러'] = monthly_display['금액_천달러'].apply(lambda x: format_unit(x, 'million_usd'))
        st.dataframe(monthly_display.rename(columns={
            '기준년월': '기간', '수출입구분명': '구분', '중량_톤': '중량', '금액_천달러': '금액'
        }), use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("국가별 수출입 분석")
        
        select_month = st.selectbox("기간 선택:", 
                                   sorted(df['기준년월'].unique(), reverse=True),
                                   format_func=lambda x: x.strftime('%Y.%m'))
        
        country_data = df[df['기준년월'] == select_month].groupby(['국가명', '수출입구분명'])[[
            '중량_톤', '금액_천달러'
        ]].sum().reset_index()
        
        export_data = country_data[country_data['수출입구분명'] == '수출'].sort_values('금액_천달러', ascending=False)
        import_data = country_data[country_data['수출입구분명'] == '수입'].sort_values('금액_천달러', ascending=False)
        
        top_n = st.slider("상위 N개국:", min_value=5, max_value=20, value=10)
        
        col1, col2 = st.columns(2)
        
        with col1:
            export_top = export_data.head(top_n)
            fig3 = px.bar(export_top, x='국가명', y='금액_천달러',
                         title=f'{select_month.strftime("%Y.%m")} 주요 수출 대상국',
                         labels={'국가명': '국가', '금액_천달러': '수출액 (천 달러)'},
                         color='금액_천달러',
                         color_continuous_scale='Blues')
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            import_top = import_data.head(top_n)
            fig4 = px.bar(import_top, x='국가명', y='금액_천달러',
                         title=f'{select_month.strftime("%Y.%m")} 주요 수입 원산국',
                         labels={'국가명': '국가', '금액_천달러': '수입액 (천 달러)'},
                         color='금액_천달러',
                         color_continuous_scale='Reds')
            st.plotly_chart(fig4, use_container_width=True)
        
        st.write(f"**{select_month.strftime('%Y.%m')} 국가별 무역 상위 {top_n}개국 (금액 기준):**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**수출 상위국:**")
            export_display = export_top[['국가명', '중량_톤', '금액_천달러']].copy()
            export_display['중량_톤'] = export_display['중량_톤'].apply(lambda x: format_unit(x, 'ton'))
            export_display['금액_천달러'] = export_display['금액_천달러'].apply(lambda x: format_unit(x, 'million_usd'))
            st.dataframe(export_display.rename(columns={
                '국가명': '국가', '중량_톤': '중량', '금액_천달러': '금액'
            }), use_container_width=True, hide_index=True)
        
        with col2:
            st.write("**수입 상위국:**")
            import_display = import_top[['국가명', '중량_톤', '금액_천달러']].copy()
            import_display['중량_톤'] = import_display['중량_톤'].apply(lambda x: format_unit(x, 'ton'))
            import_display['금액_천달러'] = import_display['금액_천달러'].apply(lambda x: format_unit(x, 'million_usd'))
            st.dataframe(import_display.rename(columns={
                '국가명': '국가', '중량_톤': '중량', '금액_천달러': '금액'
            }), use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader("누적 무역량 현황")
        
        cumulative = df.groupby(['기준년월', '수출입구분명'])[[
            '누계중량_톤', '누계금액_천달러'
        ]].max().reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig5 = px.line(cumulative, x='기준년월', y='누계중량_톤', color='수출입구분명',
                          title='월별 누적 중량',
                          labels={'기준년월': '기간', '누계중량_톤': '누적 중량 (톤)', '수출입구분명': '구분'},
                          markers=True)
            st.plotly_chart(fig5, use_container_width=True)
        
        with col2:
            fig6 = px.line(cumulative, x='기준년월', y='누계금액_천달러', color='수출입구분명',
                          title='월별 누적 금액',
                          labels={'기준년월': '기간', '누계금액_천달러': '누적 금액 (천 달러)', '수출입구분명': '구분'},
                          markers=True)
            st.plotly_chart(fig6, use_container_width=True)
        
        st.write("**누적 통계 (최신 기준):**")
        latest_cumulative = df.groupby('수출입구분명')[['누계중량_톤', '누계금액_천달러']].max()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("수출 누적 중량", format_unit(latest_cumulative.loc['수출', '누계중량_톤'], 'ton'))
            st.metric("수출 누적 금액", format_unit(latest_cumulative.loc['수출', '누계금액_천달러'], 'million_usd'))
        with col2:
            st.metric("수입 누적 중량", format_unit(latest_cumulative.loc['수입', '누계중량_톤'], 'ton'))
            st.metric("수입 누적 금액", format_unit(latest_cumulative.loc['수입', '누계금액_천달러'], 'million_usd'))

except FileNotFoundError:
    st.error(f"❌ 파일을 찾을 수 없습니다: {data_path}")
    st.info("📝 GitHub에서 'trade2023-2024.CSV'를 같은 디렉토리에 놓으세요.")
