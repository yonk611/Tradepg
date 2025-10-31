import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="수출입 확정통계", layout="wide", initial_sidebar_state="collapsed")

# CSS 커스텀 스타일
st.markdown("""
    <style>
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }
    .metric-title {
        font-size: 14px;
        opacity: 0.9;
        margin-bottom: 5px;
        font-weight: 500;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .metric-change {
        font-size: 14px;
        opacity: 0.85;
    }
    .export-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .import-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    </style>
""", unsafe_allow_html=True)

# 파일 로드
data_path = 'trade2022-2024.csv'

try:
    df = pd.read_csv(data_path, encoding='utf-8')
    
    # 데이터 정제
    df_clean = df[df['기간'] != '총계'].copy()
    df_clean['기간'] = pd.to_numeric(df_clean['기간'], errors='coerce')
    df_clean = df_clean.dropna(subset=['기간'])
    df_clean['기간'] = df_clean['기간'].astype(int)
    
    # ============ 단위 변환 함수 (직관적 한국식) ============
    def format_korean_currency(value_thousand_usd):
        """직관적인 한국식 표기 (천달러 → 조/억)"""
        if value_thousand_usd >= 1_000_000:  # 1조 이상
            jo = value_thousand_usd / 1_000_000
            return f"{jo:.2f}조달러"
        elif value_thousand_usd >= 10_000:  # 10억 이상
            eok = value_thousand_usd / 10_000
            if eok >= 100:
                return f"{eok:.0f}억달러"
            else:
                return f"{eok:.1f}억달러"
        else:
            return f"{value_thousand_usd:,.0f}천달러"
    
    years = sorted(df_clean['기간'].unique())
    
    # ============ 상단 헤더 - 주요 지표 ============
    st.title('🌊 수출입 확정통계 대시보드')
    st.markdown("---")
    
    yearly = df_clean.groupby('기간')[['수출 금액', '수입 금액', '수출 건수', '수입 건수']].sum()
    latest_year = years[-1]
    prev_year = years[-2]
    
    export_latest = yearly.loc[latest_year, '수출 금액']
    import_latest = yearly.loc[latest_year, '수입 금액']
    export_prev = yearly.loc[prev_year, '수출 금액']
    import_prev = yearly.loc[prev_year, '수입 금액']
    
    export_change_pct = ((export_latest - export_prev) / export_prev) * 100
    import_change_pct = ((import_latest - import_prev) / import_prev) * 100
    export_change_amount = export_latest - export_prev
    import_change_amount = import_latest - import_prev
    
    # 주요 지표 표시
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box export-box">
            <div class="metric-title">✈️ 수출 {format_korean_currency(export_latest)}</div>
            <div class="metric-value">{format_korean_currency(export_latest)}</div>
            <div class="metric-change">전년 동기대비 <span style="font-weight: bold; color: #FFD700;">{export_change_pct:+.1f}%({format_korean_currency(export_change_amount)} 증가)</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box import-box">
            <div class="metric-title">🚢 수입 {format_korean_currency(import_latest)}</div>
            <div class="metric-value">{format_korean_currency(import_latest)}</div>
            <div class="metric-change">전년 동기대비 <span style="font-weight: bold; color: #FFD700;">{import_change_pct:+.1f}%({format_korean_currency(import_change_amount)} 증가)</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============ 탭 구성 ============
    tab1, tab2, tab3 = st.tabs(["📊 연도별 분석", "🌍 국가별 분석", "📈 상세 현황"])
    
    with tab1:
        st.subheader("연도별 수출입 추이")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 연도별 수출입 금액 - 디자인 개선
            yearly_data = df_clean.groupby('기간')[['수출 금액', '수입 금액']].sum().reset_index()
            yearly_data['수출_표시'] = yearly_data['수출 금액'].apply(format_korean_currency)
            yearly_data['수입_표시'] = yearly_data['수입 금액'].apply(format_korean_currency)
            
            fig1 = go.Figure()
            
            # 수출 바 추가
            fig1.add_trace(go.Bar(
                x=yearly_data['기간'].astype(str),
                y=yearly_data['수출 금액'],
                name='수출',
                marker=dict(
                    color='rgba(102, 126, 234, 0.8)',
                    line=dict(color='rgba(102, 126, 234, 1)', width=2),
                    cornerradius=8
                ),
                text=yearly_data['수출_표시'],
                textposition='outside',
                hovertemplate='<b>%{x}년 수출</b><br>%{customdata}<extra></extra>',
                customdata=yearly_data['수출_표시'],
                showlegend=True
            ))
            
            # 수입 바 추가
            fig1.add_trace(go.Bar(
                x=yearly_data['기간'].astype(str),
                y=yearly_data['수입 금액'],
                name='수입',
                marker=dict(
                    color='rgba(245, 87, 108, 0.8)',
                    line=dict(color='rgba(245, 87, 108, 1)', width=2),
                    cornerradius=8
                ),
                text=yearly_data['수입_표시'],
                textposition='outside',
                hovertemplate='<b>%{x}년 수입</b><br>%{customdata}<extra></extra>',
                customdata=yearly_data['수입_표시'],
                showlegend=True
            ))
            
            fig1.update_layout(
                title='연도별 수출/수입 금액',
                barmode='group',
                xaxis_title='연도',
                yaxis_title='금액',
                height=450,
                hovermode='x unified',
                plot_bgcolor='rgba(240, 240, 245, 0.5)',
                paper_bgcolor='white',
                font=dict(size=12),
                margin=dict(b=80),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                )
            )
            fig1.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.2)')
            fig1.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.2)')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # 무역수지 - 디자인 개선
            yearly_trade = df_clean.groupby('기간')[['수출 금액', '수입 금액']].sum()
            yearly_trade['무역수지'] = yearly_trade['수출 금액'] - yearly_trade['수입 금액']
            yearly_trade_reset = yearly_trade.reset_index()
            yearly_trade_reset['무역수지_표시'] = yearly_trade_reset['무역수지'].apply(format_korean_currency)
            yearly_trade_reset['색상'] = yearly_trade_reset['무역수지'].apply(
                lambda x: 'rgba(102, 126, 234, 0.8)' if x > 0 else 'rgba(245, 87, 108, 0.8)'
            )
            yearly_trade_reset['테두리색'] = yearly_trade_reset['무역수지'].apply(
                lambda x: 'rgba(102, 126, 234, 1)' if x > 0 else 'rgba(245, 87, 108, 1)'
            )
            
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=yearly_trade_reset['기간'].astype(str),
                y=yearly_trade_reset['무역수지'],
                marker=dict(
                    color=yearly_trade_reset['색상'],
                    line=dict(color=yearly_trade_reset['테두리색'], width=2),
                    cornerradius=8
                ),
                text=yearly_trade_reset['무역수지_표시'],
                textposition='outside',
                hovertemplate='<b>%{x}년 무역수지</b><br>%{customdata}<extra></extra>',
                customdata=yearly_trade_reset['무역수지_표시'],
                showlegend=False
            ))
            
            fig2.add_hline(y=0, line_dash='dash', line_color='gray', opacity=0.7)
            
            fig2.update_layout(
                title='연도별 무역수지 (흑자/적자)',
                xaxis_title='연도',
                yaxis_title='금액',
                height=450,
                hovermode='x unified',
                plot_bgcolor='rgba(240, 240, 245, 0.5)',
                paper_bgcolor='white',
                font=dict(size=12),
                margin=dict(b=80)
            )
            fig2.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.2)')
            fig2.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.2)')
            st.plotly_chart(fig2, use_container_width=True)
        
        # 연도별 상세 통계
        st.subheader("📊 연도별 상세 통계")
        yearly_detail = df_clean.groupby('기간')[['수출 건수', '수출 금액', '수입 건수', '수입 금액', '무역수지']].sum().reset_index()
        yearly_detail['수출 금액'] = yearly_detail['수출 금액'].apply(format_korean_currency)
        yearly_detail['수입 금액'] = yearly_detail['수입 금액'].apply(format_korean_currency)
        yearly_detail['무역수지'] = yearly_detail['무역수지'].apply(format_korean_currency)
        
        st.dataframe(yearly_detail.rename(columns={
            '기간': '연도', '수출 건수': '수출 건수', '수출 금액': '수출액',
            '수입 건수': '수입 건수', '수입 금액': '수입액'
        }), use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("🌍 국가별 수출입 분석")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            select_year = st.selectbox("📅 분석 연도", sorted(df_clean['기간'].unique(), reverse=True), key="year_select")
        
        with col2:
            top_n = st.slider("🔝 상위 국가 수", min_value=5, max_value=20, value=10, key="top_n")
        
        country_data = df_clean[df_clean['기간'] == select_year].sort_values('수출 금액', ascending=False)
        country_top = country_data.head(top_n).copy()
        country_top['수출_표시'] = country_top['수출 금액'].apply(format_korean_currency)
        country_top['수입_표시'] = country_top['수입 금액'].apply(format_korean_currency)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(
                y=country_top['국가'],
                x=country_top['수출 금액'],
                orientation='h',
                marker=dict(
                    color=country_top['수출 금액'],
                    colorscale='Blues',
                    line=dict(color='rgba(102, 126, 234, 1)', width=1),
                    cornerradius=6
                ),
                text=country_top['수출_표시'],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>수출: %{customdata}<extra></extra>',
                customdata=country_top['수출_표시'],
                showlegend=False
            ))
            
            fig3.update_layout(
                title=f'🚀 {select_year}년 주요 수출 대상국',
                xaxis_title='금액',
                yaxis_title='국가',
                height=450,
                plot_bgcolor='rgba(240, 240, 245, 0.5)',
                paper_bgcolor='white',
                margin=dict(l=100, b=50),
                font=dict(size=11)
            )
            fig3.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.2)')
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            fig4 = go.Figure()
            fig4.add_trace(go.Bar(
                y=country_top['국가'],
                x=country_top['수입 금액'],
                orientation='h',
                marker=dict(
                    color=country_top['수입 금액'],
                    colorscale='Reds',
                    line=dict(color='rgba(245, 87, 108, 1)', width=1),
                    cornerradius=6
                ),
                text=country_top['수입_표시'],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>수입: %{customdata}<extra></extra>',
                customdata=country_top['수입_표시'],
                showlegend=False
            ))
            
            fig4.update_layout(
                title=f'⛴️ {select_year}년 주요 수입 원산국',
                xaxis_title='금액',
                yaxis_title='국가',
                height=450,
                plot_bgcolor='rgba(240, 240, 245, 0.5)',
                paper_bgcolor='white',
                margin=dict(l=100, b=50),
                font=dict(size=11)
            )
            fig4.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.2)')
            st.plotly_chart(fig4, use_container_width=True)
        
        # 국가별 상세 데이터
        st.subheader(f"📋 {select_year}년 국가별 상위 {top_n}개국 상세 데이터")
        country_display = country_top[['국가', '수출 금액', '수입 금액', '무역수지', '수출 건수', '수입 건수']].copy()
        country_display['수출 금액'] = country_display['수출 금액'].apply(format_korean_currency)
        country_display['수입 금액'] = country_display['수입 금액'].apply(format_korean_currency)
        country_display['무역수지'] = country_display['무역수지'].apply(format_korean_currency)
        
        st.dataframe(country_display.rename(columns={
            '국가': '국가', '수출 금액': '수출액', '수입 금액': '수입액',
            '무역수지': '수지', '수출 건수': '수출건수', '수입 건수': '수입건수'
        }), use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader("📈 3년간 성장률 및 추이 분석")
        
        # 연도별 선 그래프 (추이) - 디자인 개선
        yearly_line = df_clean.groupby('기간')[['수출 금액', '수입 금액']].sum().reset_index()
        
        fig5 = go.Figure()
        
        fig5.add_trace(go.Scatter(
            x=yearly_line['기간'].astype(str),
            y=yearly_line['수출 금액'],
            name='수출',
            mode='lines+markers',
            line=dict(color='rgba(102, 126, 234, 1)', width=3, shape='spline'),
            marker=dict(size=10, symbol='circle'),
            fill=None,
            hovertemplate='<b>%{x}년 수출</b><br>%{customdata}<extra></extra>',
            customdata=yearly_line['수출 금액'].apply(format_korean_currency)
        ))
        
        fig5.add_trace(go.Scatter(
            x=yearly_line['기간'].astype(str),
            y=yearly_line['수입 금액'],
            name='수입',
            mode='lines+markers',
            line=dict(color='rgba(245, 87, 108, 1)', width=3, shape='spline'),
            marker=dict(size=10, symbol='circle'),
            fill=None,
            hovertemplate='<b>%{x}년 수입</b><br>%{customdata}<extra></extra>',
            customdata=yearly_line['수입 금액'].apply(format_korean_currency)
        ))
        
        fig5.update_layout(
            title='3년 추이 (수출/수입)',
            xaxis_title='연도',
            yaxis_title='금액',
            height=450,
            hovermode='x unified',
            plot_bgcolor='rgba(240, 240, 245, 0.5)',
            paper_bgcolor='white',
            font=dict(size=12),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            )
        )
        fig5.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.2)')
        fig5.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.2)')
        st.plotly_chart(fig5, use_container_width=True)
        
        # 성장률 비교
        st.subheader("📊 연도별 성장률")
        
        yearly_growth = df_clean.groupby('기간')[['수출 금액', '수입 금액']].sum().reset_index()
        yearly_growth['수출_증감률(%)'] = yearly_growth['수출 금액'].pct_change() * 100
        yearly_growth['수입_증감률(%)'] = yearly_growth['수입 금액'].pct_change() * 100
        
        col1, col2, col3 = st.columns(3)
        
        for idx, year in enumerate(years):
            if idx == 0:
                with col1:
                    st.metric(f"📍 {year}년", "기준연도", "-")
            else:
                growth_data = yearly_growth[yearly_growth['기간'] == year].iloc[0]
                export_growth = growth_data['수출_증감률(%)']
                import_growth = growth_data['수입_증감률(%)']
                
                if idx == 1:
                    with col1:
                        st.metric(
                            f"📊 {year}년",
                            f"수출: {export_growth:+.1f}%",
                            f"수입: {import_growth:+.1f}%",
                            delta_color="off"
                        )
                elif idx == 2:
                    with col2:
                        st.metric(
                            f"📊 {year}년",
                            f"수출: {export_growth:+.1f}%",
                            f"수입: {import_growth:+.1f}%",
                            delta_color="off"
                        )
        
        # 국가별 성장률 (최신 2년 비교) - 디자인 개선
        st.subheader(f"🚀 {prev_year}년 vs {latest_year}년 국가별 수출 성장률")
        
        country_prev = df_clean[df_clean['기간'] == prev_year][['국가', '수출 금액']].copy()
        country_latest_comp = df_clean[df_clean['기간'] == latest_year][['국가', '수출 금액']].copy()
        
        country_growth_comp = country_prev.merge(country_latest_comp, on='국가', suffixes=('_prev', '_latest'))
        country_growth_comp['성장률(%)'] = ((country_growth_comp['수출 금액_latest'] - country_growth_comp['수출 금액_prev']) / 
                                         country_growth_comp['수출 금액_prev'] * 100)
        country_growth_comp = country_growth_comp.sort_values('성장률(%)', ascending=True)
        
        top_growth = 10
        growth_display = pd.concat([
            country_growth_comp.head(top_growth),
            country_growth_comp.tail(top_growth)
        ]).sort_values('성장률(%)')
        
        growth_display['색상'] = growth_display['성장률(%)'].apply(
            lambda x: 'rgba(102, 126, 234, 0.8)' if x > 0 else 'rgba(245, 87, 108, 0.8)'
        )
        
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(
            y=growth_display['국가'],
            x=growth_display['성장률(%)'],
            orientation='h',
            marker=dict(
                color=growth_display['색상'],
                line=dict(color='rgba(100, 100, 100, 0.5)', width=1),
                cornerradius=6
            ),
            text=growth_display['성장률(%)'].apply(lambda x: f'{x:+.1f}%'),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>성장률: %{customdata:+.1f}%<extra></extra>',
            customdata=growth_display['성장률(%)'],
            showlegend=False
        ))
        
        fig6.add_vline(x=0, line_dash='dash', line_color='gray', opacity=0.5)
        
        fig6.update_layout(
            title=f'{prev_year}년 대비 {latest_year}년 국가별 수출 성장률 (상위/하위)',
            xaxis_title='성장률 (%)',
            yaxis_title='국가',
            height=500,
            plot_bgcolor='rgba(240, 240, 245, 0.5)',
            paper_bgcolor='white',
            margin=dict(l=100, b=50),
            font=dict(size=11)
        )
        fig6.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.2)')
        st.plotly_chart(fig6, use_container_width=True)

except FileNotFoundError:
    st.error(f"❌ 파일을 찾을 수 없습니다: {data_path}")
    st.info("📝 GitHub에서 'trade2022-2024.csv'를 같은 디렉토리에 놓으세요.")
