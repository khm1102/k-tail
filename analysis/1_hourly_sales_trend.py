#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1. 시간대별 판매량 트렌드 분석
K-tail 칵테일 바의 시간대별 판매 패턴을 분석합니다.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 공통 유틸리티 함수 임포트
try:
    from utils import get_data_path, check_data_files, load_orders_data
except ImportError:
    # utils 모듈이 없는 경우 기본 경로 함수 정의
    def get_data_path(filename):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        return os.path.join(project_root, 'data', filename)
    
    def check_data_files():
        return True
    
    def load_orders_data(file_path=None):
        """기본 주문 데이터 로딩 함수 (utils가 없을 때만 사용)"""
        if file_path is None:
            file_path = get_data_path('orders.csv')
        return pd.read_csv(file_path)

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def analyze_hourly_trends(orders_df):
    """시간대별 판매 트렌드를 분석합니다."""
    # 시간 데이터 변환
    orders_df['timestamp'] = pd.to_datetime(orders_df['timestamp'])
    orders_df['hour'] = orders_df['timestamp'].dt.hour
    
    # 시간대별 집계
    hourly_sales = orders_df.groupby('hour').agg({
        'quantity': 'sum',
        'cocktail_name': 'count'
    }).rename(columns={'cocktail_name': 'order_count'})
    
    # 피크 타임 식별
    peak_hours = hourly_sales.nlargest(3, 'quantity').index.tolist()
    
    return hourly_sales, peak_hours

def create_visualizations(hourly_sales, peak_hours, show_plots=True):
    """시간대별 분석 시각화를 생성합니다."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('시간대별 판매량 트렌드 분석', fontsize=16, fontweight='bold')
    
    # 1. 시간대별 판매량
    axes[0,0].bar(hourly_sales.index, hourly_sales['quantity'], 
                  color=['red' if h in peak_hours else 'skyblue' for h in hourly_sales.index])
    axes[0,0].set_title('시간대별 총 판매량')
    axes[0,0].set_xlabel('시간')
    axes[0,0].set_ylabel('판매량')
    axes[0,0].grid(True, alpha=0.3)
    
    # 2. 시간대별 주문 건수
    axes[0,1].plot(hourly_sales.index, hourly_sales['order_count'], 
                   marker='o', linewidth=2, markersize=6, color='green')
    axes[0,1].set_title('시간대별 주문 건수')
    axes[0,1].set_xlabel('시간')
    axes[0,1].set_ylabel('주문 건수')
    axes[0,1].grid(True, alpha=0.3)
    
    # 3. 평균 주문 크기
    avg_order_size = hourly_sales['quantity'] / hourly_sales['order_count']
    axes[1,0].bar(hourly_sales.index, avg_order_size, color='orange')
    axes[1,0].set_title('시간대별 평균 주문 크기')
    axes[1,0].set_xlabel('시간')
    axes[1,0].set_ylabel('평균 주문 크기 (잔/주문)')
    axes[1,0].grid(True, alpha=0.3)
    
    # 4. 피크타임 vs 일반시간 비교
    peak_data = [
        hourly_sales.loc[peak_hours]['quantity'].sum(),
        hourly_sales.drop(peak_hours)['quantity'].sum()
    ]
    labels = ['피크타임\n(상위 3시간)', '일반시간']
    colors = ['red', 'lightblue']
    
    axes[1,1].pie(peak_data, labels=labels, colors=colors, autopct='%1.1f%%')
    axes[1,1].set_title('피크타임 vs 일반시간 판매 비율')
    
    plt.tight_layout()
    
    # 그래프 표시
    if show_plots:
        plt.show()
    
    return fig

def generate_report(hourly_sales, peak_hours):
    """분석 리포트를 생성합니다."""
    print("=" * 60)
    print("시간대별 판매량 트렌드 분석 리포트")
    print("=" * 60)
    
    print(f"\n전체 판매 현황:")
    print(f"   총 판매량: {hourly_sales['quantity'].sum():,}잔")
    print(f"   총 주문 건수: {hourly_sales['order_count'].sum():,}건")
    print(f"   평균 주문 크기: {hourly_sales['quantity'].sum() / hourly_sales['order_count'].sum():.1f}잔/주문")
    
    print(f"\n피크 타임 분석:")
    print(f"   피크 시간대: {peak_hours}시")
    peak_sales = hourly_sales.loc[peak_hours]['quantity'].sum()
    total_sales = hourly_sales['quantity'].sum()
    peak_ratio = (peak_sales / total_sales) * 100
    print(f"   피크타임 판매량: {peak_sales:,}잔 ({peak_ratio:.1f}%)")
    
    print(f"\n시간대별 상세 통계:")
    print(hourly_sales.round(2))
    
    # 시간대별 특성 분석
    print(f"\n시간대별 특성:")
    busiest_hour = hourly_sales['quantity'].idxmax()
    quietest_hour = hourly_sales['quantity'].idxmin()
    
    print(f"   가장 바쁜 시간: {busiest_hour}시 ({hourly_sales.loc[busiest_hour, 'quantity']}잔)")
    print(f"   가장 한가한 시간: {quietest_hour}시 ({hourly_sales.loc[quietest_hour, 'quantity']}잔)")
    
    # 운영 시간 추천
    print(f"\n운영 최적화 제안:")
    print(f"   - 피크타임({peak_hours}시) 추가 인력 배치 권장")
    print(f"   - 한가한 시간대({quietest_hour}시) 청소/준비 작업 적합")
    
    if busiest_hour in [20, 21, 22]:
        print(f"   - 저녁 시간대 집중 → 해피아워 이벤트 고려")
    elif busiest_hour in [14, 15, 16]:
        print(f"   - 오후 시간대 집중 → 런치 칵테일 메뉴 확대")

def main():
    """메인 실행 함수"""
    print("시간대별 판매량 트렌드 분석을 시작합니다...")
    
    # 데이터 파일 확인
    if not check_data_files():
        return
    
    # 데이터 로딩
    orders_df = load_orders_data()
    if orders_df is None:
        return
    
    print(f"주문 데이터 로딩 완료: {len(orders_df)}건")
    
    # 분석 실행
    hourly_sales, peak_hours = analyze_hourly_trends(orders_df)
    
    # 시각화 생성
    create_visualizations(hourly_sales, peak_hours)
    
    # 리포트 생성
    generate_report(hourly_sales, peak_hours)
    
    print("\n시간대별 판매량 트렌드 분석이 완료되었습니다.")

def run_hourly_sales_analysis(show_plots=True, return_fig=False):
    """GUI에서 호출할 수 있는 시간대별 판매량 트렌드 분석 함수"""
    print("시간대별 판매량 트렌드 분석을 시작합니다...")
    
    # 데이터 파일 확인
    if not check_data_files():
        return None
    
    # 데이터 로딩
    orders_df = load_orders_data()
    if orders_df is None:
        return None
    
    print(f"주문 데이터 로딩 완료: {len(orders_df)}건")
    
    # 분석 실행
    hourly_sales, peak_hours = analyze_hourly_trends(orders_df)
    
    # 시각화 생성
    fig = create_visualizations(hourly_sales, peak_hours, show_plots=show_plots)
    
    # 리포트 생성
    generate_report(hourly_sales, peak_hours)
    
    print("\n시간대별 판매량 트렌드 분석이 완료되었습니다.")
    
    if return_fig:
        return fig
    else:
        return {'hourly_sales': hourly_sales, 'peak_hours': peak_hours}

if __name__ == "__main__":
    main()
