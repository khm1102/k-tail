"""
3. 피크 타임 분석
K-tail 칵테일 바의 피크 타임을 분석하고 시각화합니다.
GUI에서 호출되어 그래프를 생성합니다.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 공통 유틸리티 함수 임포트
try:
    from utils import get_data_path, check_data_files, load_orders_data
except ImportError:
    # utils 모듈이 없는 경우 기본 경로 함수 정의
    def get_data_path(filename):
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        return os.path.join(project_root, 'data', filename)

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class PeakTimeAnalyzer:
    def __init__(self):
        self.orders_df = None
        self.hourly_stats = None
        self.peak_hours = []
        
    def load_data(self, file_path=None):
        """주문 데이터를 로딩하고 전처리합니다."""
        try:
            # utils의 공통 함수 사용
            self.orders_df = load_orders_data(file_path)
            if self.orders_df is None:
                return False
                
            self.orders_df['timestamp'] = pd.to_datetime(self.orders_df['timestamp'])
            self.orders_df['hour'] = self.orders_df['timestamp'].dt.hour
            self.orders_df['day_of_week'] = self.orders_df['timestamp'].dt.day_name()
            
            print(f"주문 데이터 로딩 완료: {len(self.orders_df)}건")
            return True
            
        except Exception as e:
            print(f"데이터 로딩 실패: {e}")
            return False
    
    def analyze_peak_times(self):
        """피크 타임을 분석합니다."""
        if self.orders_df is None:
            print("데이터가 로딩되지 않았습니다.")
            return None
        
        # 시간대별 통계
        self.hourly_stats = self.orders_df.groupby('hour').agg({
            'quantity': ['sum', 'mean', 'count'],
            'cocktail_name': 'count'
        }).round(2)
        
        self.hourly_stats.columns = ['total_quantity', 'avg_quantity', 'order_count', 'total_orders']
        
        # 피크 시간 식별 (상위 25% 기준)
        threshold = self.hourly_stats['total_quantity'].quantile(0.75)
        self.peak_hours = self.hourly_stats[
            self.hourly_stats['total_quantity'] >= threshold
        ].index.tolist()
        
        return self.hourly_stats
    
    def identify_patterns(self):
        """시간대별 패턴을 식별합니다."""
        patterns = {
            'peak_hours': self.peak_hours,
            'busiest_hour': self.hourly_stats['total_quantity'].idxmax(),
            'quietest_hour': self.hourly_stats['total_quantity'].idxmin(),
            'avg_orders_per_hour': self.hourly_stats['total_orders'].mean(),
            'max_orders_hour': self.hourly_stats['total_orders'].max(),
            'peak_period_sales': self.hourly_stats.loc[self.peak_hours]['total_quantity'].sum()
        }
        
        return patterns
    
    def create_visualizations(self, show_plots=True):
        """피크 타임 분석 시각화를 생성합니다."""
        if self.hourly_stats is None:
            self.analyze_peak_times()
        
        fig, axes = plt.subplots(2, 2, figsize=(24, 20))
        fig.suptitle('K-tail 피크 타임 분석', fontsize=18, fontweight='bold', y=0.97)
        
        # 1. 시간대별 총 판매량 (피크타임 강조)
        colors = ['red' if h in self.peak_hours else 'skyblue' for h in self.hourly_stats.index]
        bars = axes[0,0].bar(self.hourly_stats.index, self.hourly_stats['total_quantity'], 
                            color=colors, alpha=0.8)
        axes[0,0].set_title('시간대별 총 판매량 (피크타임 강조)', fontweight='bold')
        axes[0,0].set_xlabel('시간')
        axes[0,0].set_ylabel('총 판매량')
        axes[0,0].grid(True, alpha=0.3)
        
        # 피크타임 텍스트 표시
        for i, bar in enumerate(bars):
            if self.hourly_stats.index[i] in self.peak_hours:
                height = bar.get_height()
                axes[0,0].text(bar.get_x() + bar.get_width()/2., height + 1,
                              'PEAK', ha='center', va='bottom', fontweight='bold', color='red')
        
        # 2. 시간대별 주문 건수
        axes[0,1].plot(self.hourly_stats.index, self.hourly_stats['total_orders'], 
                      marker='o', linewidth=3, markersize=8, color='green')
        axes[0,1].fill_between(self.hourly_stats.index, self.hourly_stats['total_orders'], 
                              alpha=0.3, color='green')
        axes[0,1].set_title('시간대별 주문 건수 트렌드', fontweight='bold')
        axes[0,1].set_xlabel('시간')
        axes[0,1].set_ylabel('주문 건수')
        axes[0,1].grid(True, alpha=0.3)
        
        # 3. 피크타임 vs 비피크타임 비교
        peak_data = self.hourly_stats.loc[self.peak_hours].sum()
        non_peak_hours = [h for h in self.hourly_stats.index if h not in self.peak_hours]
        non_peak_data = self.hourly_stats.loc[non_peak_hours].sum()
        
        comparison_data = {
            '판매량': [peak_data['total_quantity'], non_peak_data['total_quantity']],
            '주문건수': [peak_data['total_orders'], non_peak_data['total_orders']]
        }
        
        x = np.arange(len(comparison_data))
        width = 0.35
        
        bars1 = axes[1,0].bar(x - width/2, comparison_data['판매량'], width, 
                             label='판매량', color='orange', alpha=0.8)
        bars2 = axes[1,0].bar(x + width/2, comparison_data['주문건수'], width, 
                             label='주문건수', color='purple', alpha=0.8)
        
        axes[1,0].set_title('피크타임 vs 비피크타임 비교', fontweight='bold')
        axes[1,0].set_ylabel('수량')
        axes[1,0].set_xticks(x)
        axes[1,0].set_xticklabels(['피크타임', '비피크타임'])
        axes[1,0].legend()
        axes[1,0].grid(True, alpha=0.3)
        
        # 4. 시간대별 효율성 (평균 주문당 판매량)
        efficiency = self.hourly_stats['total_quantity'] / self.hourly_stats['total_orders']
        efficiency = efficiency.fillna(0)
        
        axes[1,1].bar(self.hourly_stats.index, efficiency, 
                     color=['gold' if eff > efficiency.mean() else 'lightblue' for eff in efficiency])
        axes[1,1].axhline(y=efficiency.mean(), color='red', linestyle='--', 
                         label=f'평균: {efficiency.mean():.1f}')
        axes[1,1].set_title('시간대별 주문 효율성 (주문당 평균 판매량)', fontweight='bold')
        axes[1,1].set_xlabel('시간')
        axes[1,1].set_ylabel('주문당 평균 판매량')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        
        plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.08, hspace=0.5, wspace=0.4)
        
        if show_plots:
            plt.show()
        
        return fig
    
    def generate_report(self):
        """피크 타임 분석 리포트를 생성합니다."""
        if self.hourly_stats is None:
            self.analyze_peak_times()
        
        patterns = self.identify_patterns()
        total_sales = self.hourly_stats['total_quantity'].sum()
        peak_sales = patterns['peak_period_sales']
        peak_ratio = (peak_sales / total_sales) * 100
        
        report = f"""
K-tail 피크 타임 분석 리포트
{'='*50}

피크 타임 식별:
• 피크 시간대: {', '.join([f'{h}시' for h in patterns['peak_hours']])}
• 최고 판매 시간: {patterns['busiest_hour']}시
• 최저 판매 시간: {patterns['quietest_hour']}시

피크 타임 성과:
• 피크 타임 판매량: {peak_sales}잔 ({peak_ratio:.1f}%)
• 시간당 평균 주문: {patterns['avg_orders_per_hour']:.1f}건
• 최대 시간당 주문: {patterns['max_orders_hour']}건

⏰ 시간대별 상세 분석:
"""
        
        for hour, stats in self.hourly_stats.iterrows():
            status = "PEAK" if hour in self.peak_hours else "Normal"
            report += f"• {hour:2d}시: {stats['total_quantity']:3.0f}잔 ({stats['total_orders']:2.0f}건) {status}\n"
        
        report += f"""
비즈니스 인사이트:
• 피크타임에 전체 매출의 {peak_ratio:.1f}%가 집중됨
• 피크타임 대비 인력 배치 필요: {', '.join([f'{h}시' for h in patterns['peak_hours']])}
• 비피크타임 매출 증대 전략 필요
• 최적 운영 시간대 활용 방안 수립 권장
"""
        
        return report

def run_peak_time_analysis(show_plots=True, return_fig=False):
    """피크 타임 분석을 실행하는 메인 함수 (GUI에서 호출)"""
    analyzer = PeakTimeAnalyzer()
    
    # 데이터 로딩
    if not analyzer.load_data():
        return None
    
    # 분석 실행
    analyzer.analyze_peak_times()
    
    # 시각화 생성
    fig = analyzer.create_visualizations(show_plots=show_plots)
    
    # 리포트 생성 및 출력
    report = analyzer.generate_report()
    print(report)
    
    if return_fig:
        return fig
    
    return analyzer

if __name__ == "__main__":
    # 독립 실행 시 분석 수행
    print("피크 타임 분석을 시작합니다...")
    analyzer = run_peak_time_analysis()
    
    if analyzer:
        print("피크 타임 분석이 완료되었습니다!")
        
        # 추가 인사이트
        patterns = analyzer.identify_patterns()
        print(f"\n핵심 발견사항:")
        print(f"• 가장 바쁜 시간: {patterns['busiest_hour']}시")
        print(f"• 피크 시간대: {len(patterns['peak_hours'])}개 시간대")
        print(f"• 운영 효율성 최적화 시간: {patterns['peak_hours']}")
    else:
        print("ERROR: 분석 실행 중 오류가 발생했습니다.")
