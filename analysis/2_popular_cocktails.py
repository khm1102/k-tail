#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2. 인기 칵테일 분석
K-tail 칵테일 바의 인기 칵테일 순위와 특성을 분석합니다.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_data():
    """주문 데이터와 칵테일 정보를 로딩합니다."""
    # 주문 데이터 로딩
    orders = []
    with open('data/orders.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line and not line.startswith('--'):
            parts = line.split(',')
            if len(parts) >= 3:
                timestamp = parts[0]
                cocktail_name = parts[1]
                quantity = int(parts[2])
                
                orders.append({
                    'timestamp': timestamp,
                    'cocktail_name': cocktail_name,
                    'quantity': quantity
                })
        i += 1
    
    orders_df = pd.DataFrame(orders)
    
    # 칵테일 정보 로딩
    cocktails_df = pd.read_csv('data/cocktails.csv')
    
    return orders_df, cocktails_df

def analyze_popular_cocktails(orders_df, cocktails_df):
    """인기 칵테일을 분석합니다."""
    # 칵테일별 통계
    cocktail_stats = orders_df.groupby('cocktail_name').agg({
        'quantity': 'sum',
        'cocktail_name': 'count'
    }).rename(columns={'cocktail_name': 'order_frequency'})
    
    # 칵테일 정보와 매핑 (중복 제거)
    cocktails_df_unique = cocktails_df.drop_duplicates(subset=['Cocktail Name'], keep='first')
    cocktail_info = cocktails_df_unique.set_index('Cocktail Name').to_dict('index')
    
    # 가격 정보 추가
    def get_price(cocktail_name):
        if cocktail_name in cocktail_info:
            price_str = cocktail_info[cocktail_name].get(' Price ', '$0.00')
            if pd.isna(price_str) or price_str == '':
                return 0.0
            # 숫자가 아닌 문자 제거하고 float 변환
            try:
                return float(str(price_str).replace('$', '').replace(',', '').strip())
            except (ValueError, AttributeError):
                return 0.0
        return 0.0
    
    cocktail_stats['unit_price'] = cocktail_stats.index.map(get_price)
    cocktail_stats['total_revenue'] = cocktail_stats['quantity'] * cocktail_stats['unit_price']
    
    # 가격대 분류
    def price_category(price):
        if price <= 10:
            return '저가 ($0-10)'
        elif price <= 15:
            return '중가 ($10-15)'
        else:
            return '고가 ($15+)'
    
    cocktail_stats['price_category'] = cocktail_stats['unit_price'].apply(price_category)
    
    return cocktail_stats, cocktail_info

def create_visualizations(cocktail_stats, show_plots=True):
    """인기 칵테일 분석 시각화를 생성합니다."""
    fig, axes = plt.subplots(2, 2, figsize=(24, 20))
    fig.suptitle('인기 칵테일 분석', fontsize=18, fontweight='bold', y=0.97)
    
    # 1. 판매량 TOP 10
    top_quantity = cocktail_stats.nlargest(10, 'quantity')
    axes[0,0].barh(range(len(top_quantity)), top_quantity['quantity'], color='lightcoral')
    axes[0,0].set_yticks(range(len(top_quantity)))
    axes[0,0].set_yticklabels([name[:25] + '...' if len(name) > 25 else name 
                              for name in top_quantity.index], fontsize=10)
    axes[0,0].set_title('TOP 10 칵테일 (판매량 기준)')
    axes[0,0].set_xlabel('판매량')
    axes[0,0].invert_yaxis()
    
    # 2. 매출 TOP 10
    top_revenue = cocktail_stats.nlargest(10, 'total_revenue')
    axes[0,1].barh(range(len(top_revenue)), top_revenue['total_revenue'], color='gold')
    axes[0,1].set_yticks(range(len(top_revenue)))
    axes[0,1].set_yticklabels([name[:25] + '...' if len(name) > 25 else name 
                              for name in top_revenue.index], fontsize=10)
    axes[0,1].set_title('TOP 10 칵테일 (매출 기준)')
    axes[0,1].set_xlabel('매출 ($)')
    axes[0,1].invert_yaxis()
    
    # 3. 주문 빈도 TOP 10
    top_frequency = cocktail_stats.nlargest(10, 'order_frequency')
    axes[1,0].barh(range(len(top_frequency)), top_frequency['order_frequency'], color='lightblue')
    axes[1,0].set_yticks(range(len(top_frequency)))
    axes[1,0].set_yticklabels([name[:25] + '...' if len(name) > 25 else name 
                              for name in top_frequency.index], fontsize=10)
    axes[1,0].set_title('TOP 10 칵테일 (주문 빈도)')
    axes[1,0].set_xlabel('주문 횟수')
    axes[1,0].invert_yaxis()
    
    # 4. 가격대별 인기도
    price_popularity = cocktail_stats.groupby('price_category').agg({
        'quantity': 'sum',
        'total_revenue': 'sum'
    })
    
    axes[1,1].pie(price_popularity['quantity'].values, 
                  labels=price_popularity.index, 
                  autopct='%1.1f%%',
                  colors=['lightgreen', 'orange', 'pink'])
    axes[1,1].set_title('가격대별 판매량 비율')
    
    plt.subplots_adjust(left=0.15, right=0.95, top=0.92, bottom=0.08, hspace=0.5, wspace=0.4)
    
    if show_plots:
        plt.show()
    
    return fig

def analyze_cocktail_performance(cocktail_stats):
    """칵테일 성과를 세부 분석합니다."""
    # 성과 지표 계산
    cocktail_stats['avg_order_size'] = cocktail_stats['quantity'] / cocktail_stats['order_frequency']
    cocktail_stats['revenue_per_order'] = cocktail_stats['total_revenue'] / cocktail_stats['order_frequency']
    
    # 파레토 분석 (80-20 법칙)
    total_quantity = cocktail_stats['quantity'].sum()
    cocktail_stats_sorted = cocktail_stats.sort_values('quantity', ascending=False)
    cocktail_stats_sorted['cumulative_quantity'] = cocktail_stats_sorted['quantity'].cumsum()
    cocktail_stats_sorted['cumulative_percentage'] = (cocktail_stats_sorted['cumulative_quantity'] / total_quantity) * 100
    
    # 80% 매출을 차지하는 칵테일 수
    top_80_percent = cocktail_stats_sorted[cocktail_stats_sorted['cumulative_percentage'] <= 80]
    
    return cocktail_stats_sorted, top_80_percent

def generate_report(cocktail_stats, cocktail_stats_sorted, top_80_percent):
    """인기 칵테일 분석 리포트를 생성합니다."""
    print("=" * 60)
    print("인기 칵테일 분석 리포트")
    print("=" * 60)
    
    print(f"\n전체 칵테일 현황:")
    print(f"   총 칵테일 종류: {len(cocktail_stats)}개")
    print(f"   총 판매량: {cocktail_stats['quantity'].sum():,}잔")
    print(f"   총 매출: ${cocktail_stats['total_revenue'].sum():,.2f}")
    print(f"   평균 단가: ${cocktail_stats['unit_price'].mean():.2f}")
    
    print(f"\nTOP 5 인기 칵테일 (판매량 기준):")
    top_5 = cocktail_stats.nlargest(5, 'quantity')
    for i, (name, stats) in enumerate(top_5.iterrows(), 1):
        print(f"   {i}. {name}")
        print(f"      판매량: {stats['quantity']}잔")
        print(f"      주문횟수: {stats['order_frequency']}회")
        print(f"      총 매출: ${stats['total_revenue']:,.2f}")
        print(f"      평균 주문크기: {stats['avg_order_size']:.1f}잔/주문")
        print()
    
    print(f"\nTOP 5 매출 기여 칵테일:")
    top_revenue_5 = cocktail_stats.nlargest(5, 'total_revenue')
    for i, (name, stats) in enumerate(top_revenue_5.iterrows(), 1):
        contribution = (stats['total_revenue'] / cocktail_stats['total_revenue'].sum()) * 100
        print(f"   {i}. {name}: ${stats['total_revenue']:,.2f} ({contribution:.1f}%)")
    
    print(f"\n파레토 분석 (80-20 법칙):")
    pareto_ratio = (len(top_80_percent) / len(cocktail_stats)) * 100
    print(f"   상위 {len(top_80_percent)}개 칵테일({pareto_ratio:.1f}%)이 전체 판매량의 80%를 차지")
    
    print(f"\n가격대별 분석:")
    price_analysis = cocktail_stats.groupby('price_category').agg({
        'quantity': ['sum', 'mean'],
        'total_revenue': 'sum',
        'order_frequency': 'sum'
    }).round(2)
    
    for category in price_analysis.index:
        quantity_sum = price_analysis.loc[category, ('quantity', 'sum')]
        quantity_mean = price_analysis.loc[category, ('quantity', 'mean')]
        revenue = price_analysis.loc[category, ('total_revenue', 'sum')]
        orders = price_analysis.loc[category, ('order_frequency', 'sum')]
        
        print(f"   {category}:")
        print(f"     총 판매량: {quantity_sum}잔")
        print(f"     평균 판매량: {quantity_mean:.1f}잔")
        print(f"     총 매출: ${revenue:,.2f}")
        print(f"     주문 건수: {orders}건")
        print()
    
    print(f"\n운영 제안:")
    best_seller = cocktail_stats['quantity'].idxmax()
    worst_seller = cocktail_stats['quantity'].idxmin()
    
    print(f"   - 베스트셀러 '{best_seller}' 레시피 표준화 및 품질 관리 강화")
    print(f"   - 저조한 메뉴 '{worst_seller}' 개선 또는 단종 검토")
    print(f"   - 상위 {len(top_80_percent)}개 핵심 메뉴 중심의 재고 관리")
    
    # 고수익 메뉴 추천
    high_revenue_per_order = cocktail_stats[cocktail_stats['revenue_per_order'] > cocktail_stats['revenue_per_order'].mean()]
    if not high_revenue_per_order.empty:
        print(f"   - 고수익 메뉴 프로모션: {', '.join(high_revenue_per_order.head(3).index)}")

def run_popular_cocktails_analysis(show_plots=True, return_fig=False):
    """인기 칵테일 분석을 실행하는 메인 함수 (GUI에서 호출)"""
    print("인기 칵테일 분석을 시작합니다...")
    
    # 데이터 로딩
    try:
        orders_df, cocktails_df = load_data()
        print(f"데이터 로딩 완료: 주문 {len(orders_df)}건, 칵테일 메뉴 {len(cocktails_df)}개")
    except FileNotFoundError as e:
        print(f"ERROR: 데이터 파일을 찾을 수 없습니다: {e}")
        return None
    
    # 분석 실행
    cocktail_stats, cocktail_info = analyze_popular_cocktails(orders_df, cocktails_df)
    cocktail_stats_sorted, top_80_percent = analyze_cocktail_performance(cocktail_stats)
    
    # 시각화 생성
    fig = create_visualizations(cocktail_stats, show_plots=show_plots)
    
    # 리포트 생성
    generate_report(cocktail_stats, cocktail_stats_sorted, top_80_percent)
    
    print("\n인기 칵테일 분석이 완료되었습니다.")
    
    if return_fig:
        return fig
    else:
        return {'cocktail_stats': cocktail_stats, 'top_80_percent': top_80_percent}

def main():
    """메인 실행 함수"""
    run_popular_cocktails_analysis()

if __name__ == "__main__":
    main()
