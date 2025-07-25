"""
7. 가격대별 선호도 분석
K-tail 칵테일 바의 가격대별 고객 선호도와 패턴을 분석하고 시각화합니다.
GUI에서 호출되어 그래프를 생성합니다.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class PricePreferenceAnalyzer:
    def __init__(self):
        self.orders_df = None
        self.cocktails_df = None
        self.cocktail_info = {}
        self.price_analysis = {}
        self.hourly_price_pref = None
        self.seasonal_price_pref = None
        
    def load_data(self, orders_path='data/orders.csv', cocktails_path='data/cocktails.csv'):
        """주문 데이터와 칵테일 메뉴 데이터를 로딩합니다."""
        try:
            # 주문 데이터 로딩
            orders = []
            with open(orders_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('--'):
                    parts = line.split(',')
                    if len(parts) >= 3:
                        orders.append({
                            'timestamp': parts[0],
                            'cocktail_name': parts[1],
                            'quantity': int(parts[2])
                        })
            
            self.orders_df = pd.DataFrame(orders)
            self.orders_df['timestamp'] = pd.to_datetime(self.orders_df['timestamp'])
            
            # 시간 관련 정보 추가
            self.orders_df['hour'] = self.orders_df['timestamp'].dt.hour
            self.orders_df['day_of_week'] = self.orders_df['timestamp'].dt.day_name()
            self.orders_df['month'] = self.orders_df['timestamp'].dt.month
            self.orders_df['season'] = self.orders_df['month'].map({
                12: '겨울', 1: '겨울', 2: '겨울',
                3: '봄', 4: '봄', 5: '봄',
                6: '여름', 7: '여름', 8: '여름',
                9: '가을', 10: '가을', 11: '가을'
            })
            
            # 칵테일 메뉴 데이터 로딩
            self.cocktails_df = pd.read_csv(cocktails_path)
            cocktails_df_unique = self.cocktails_df.drop_duplicates(subset=['Cocktail Name'], keep='first')
            self.cocktail_info = cocktails_df_unique.set_index('Cocktail Name').to_dict('index')
            
            # 가격 정보 추가
            self.orders_df['unit_price'] = self.orders_df['cocktail_name'].apply(self._get_price)
            self.orders_df['total_price'] = self.orders_df['unit_price'] * self.orders_df['quantity']
            
            # 가격대 분류
            self.orders_df['price_category'] = self.orders_df['unit_price'].apply(self._price_category)
            
            print(f"주문 데이터: {len(self.orders_df)}건")
            print(f"칵테일 메뉴: {len(self.cocktails_df)}개")
            print(f"가격 범위: ${self.orders_df['unit_price'].min():.2f} ~ ${self.orders_df['unit_price'].max():.2f}")
            return True
            
        except Exception as e:
            print(f"데이터 로딩 실패: {e}")
            return False
    
    def _get_price(self, cocktail_name):
        """칵테일 이름으로 가격을 조회합니다."""
        if cocktail_name in self.cocktail_info:
            price_str = self.cocktail_info[cocktail_name].get(' Price ', '$0.00')
            if pd.isna(price_str) or price_str == '':
                return 0.0
            try:
                return float(str(price_str).replace('$', '').replace(',', '').strip())
            except (ValueError, AttributeError):
                return 0.0
        return 0.0
    
    def _price_category(self, price):
        """가격을 카테고리로 분류합니다."""
        if price <= 10:
            return '저가 ($0-10)'
        elif price <= 15:
            return '중가 ($10-15)'
        else:
            return '고가 ($15+)'
    
    def analyze_price_preferences(self):
        """가격대별 선호도를 분석합니다."""
        self.price_analysis = self.orders_df.groupby('price_category').agg({
            'quantity': 'sum',
            'total_price': 'sum',
            'cocktail_name': 'count',
            'unit_price': 'mean'
        }).rename(columns={'cocktail_name': 'order_count'})
        
        # 시간대별 가격 선호도
        self.hourly_price_pref = self.orders_df.groupby(['hour', 'price_category'])['quantity'].sum().unstack(fill_value=0)
        
        # 계절별 가격 선호도
        self.seasonal_price_pref = self.orders_df.groupby(['season', 'price_category'])['quantity'].sum().unstack(fill_value=0)
        
        # 요일별 가격 선호도
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.weekday_price_pref = self.orders_df.groupby(['day_of_week', 'price_category'])['quantity'].sum().unstack(fill_value=0)
        self.weekday_price_pref = self.weekday_price_pref.reindex(weekday_order, fill_value=0)
        
        return self.price_analysis
    
    def analyze_price_sensitivity(self):
        """가격 민감도를 분석합니다."""
        # 가격대별 주문 패턴
        price_stats = {}
        
        for category in self.price_analysis.index:
            category_data = self.orders_df[self.orders_df['price_category'] == category]
            
            price_stats[category] = {
                'avg_order_size': category_data['quantity'].mean(),
                'avg_frequency': len(category_data) / len(self.orders_df['cocktail_name'].unique()),
                'price_range': (category_data['unit_price'].min(), category_data['unit_price'].max()),
                'customer_retention': len(category_data) / len(self.orders_df),  # 간접 지표
                'peak_hours': category_data.groupby('hour')['quantity'].sum().idxmax(),
                'peak_season': category_data.groupby('season')['quantity'].sum().idxmax()
            }
        
        return price_stats
    
    def calculate_elasticity_metrics(self):
        """가격 탄력성 관련 지표를 계산합니다."""
        # 가격대별 수요 곡선 근사
        price_points = []
        quantity_points = []
        
        for category, stats in self.price_analysis.iterrows():
            avg_price = stats['unit_price']
            total_quantity = stats['quantity']
            price_points.append(avg_price)
            quantity_points.append(total_quantity)
        
        # 가격-수량 상관관계
        price_quantity_corr = np.corrcoef(price_points, quantity_points)[0, 1]
        
        # 파레토 분석 (가격대별 매출 기여도)
        total_revenue = self.price_analysis['total_price'].sum()
        revenue_contribution = {}
        cumulative_revenue = 0
        
        sorted_by_revenue = self.price_analysis.sort_values('total_price', ascending=False)
        for category, stats in sorted_by_revenue.iterrows():
            contribution = (stats['total_price'] / total_revenue) * 100
            cumulative_revenue += contribution
            revenue_contribution[category] = {
                'contribution': contribution,
                'cumulative': cumulative_revenue
            }
        
        return {
            'price_quantity_correlation': price_quantity_corr,
            'revenue_contribution': revenue_contribution,
            'price_dispersion': np.std(price_points),
            'demand_concentration': max(quantity_points) / sum(quantity_points)
        }
    
    def create_visualizations(self, show_plots=True):
        """가격대별 선호도 분석 시각화를 생성합니다."""
        if self.price_analysis is None:
            self.analyze_price_preferences()
        
        price_stats = self.analyze_price_sensitivity()
        elasticity_metrics = self.calculate_elasticity_metrics()
        
        fig, axes = plt.subplots(3, 2, figsize=(18, 20))
        fig.suptitle('K-tail 가격대별 선호도 분석', fontsize=16, fontweight='bold', y=0.98)
        
        # 1. 가격대별 판매량 및 매출
        x = range(len(self.price_analysis))
        width = 0.35
        
        bars1 = axes[0,0].bar([i - width/2 for i in x], self.price_analysis['quantity'], 
                             width, label='판매량', color='skyblue', alpha=0.8)
        ax_twin = axes[0,0].twinx()
        bars2 = ax_twin.bar([i + width/2 for i in x], self.price_analysis['total_price'], 
                           width, label='매출', color='lightcoral', alpha=0.8)
        
        axes[0,0].set_xlabel('가격대')
        axes[0,0].set_ylabel('판매량', color='blue')
        ax_twin.set_ylabel('매출 ($)', color='red')
        axes[0,0].set_title('가격대별 판매량 & 매출', fontweight='bold')
        axes[0,0].set_xticks(x)
        axes[0,0].set_xticklabels(self.price_analysis.index, rotation=0)
        axes[0,0].legend(loc='upper left')
        ax_twin.legend(loc='upper right')
        
        # 값 표시
        for bar in bars1:
            height = bar.get_height()
            axes[0,0].text(bar.get_x() + bar.get_width()/2., height + max(self.price_analysis['quantity'])*0.01,
                          f'{int(height)}', ha='center', va='bottom', fontsize=9)
        
        # 2. 시간대별 가격대 선호도
        if not self.hourly_price_pref.empty:
            self.hourly_price_pref.plot(kind='bar', stacked=True, ax=axes[0,1], 
                                       color=['lightgreen', 'orange', 'lightcoral'])
            axes[0,1].set_title('시간대별 가격대 선호도', fontweight='bold')
            axes[0,1].set_xlabel('시간')
            axes[0,1].set_ylabel('판매량')
            axes[0,1].legend(title='가격대', bbox_to_anchor=(1.05, 1), loc='upper left')
            axes[0,1].tick_params(axis='x', rotation=0)
        
        # 3. 계절별 가격대 선호도
        if not self.seasonal_price_pref.empty:
            self.seasonal_price_pref.plot(kind='bar', ax=axes[1,0], 
                                         color=['lightgreen', 'orange', 'lightcoral'])
            axes[1,0].set_title('계절별 가격대 선호도', fontweight='bold')
            axes[1,0].set_xlabel('계절')
            axes[1,0].set_ylabel('판매량')
            axes[1,0].legend(title='가격대')
            axes[1,0].tick_params(axis='x', rotation=0)
        
        # 4. 가격 분포 히스토그램
        axes[1,1].hist(self.orders_df['unit_price'], bins=20, color='lightyellow', 
                      edgecolor='black', alpha=0.7)
        axes[1,1].axvline(self.orders_df['unit_price'].mean(), color='red', 
                         linestyle='--', linewidth=2, label=f'평균: ${self.orders_df["unit_price"].mean():.2f}')
        axes[1,1].axvline(self.orders_df['unit_price'].median(), color='green', 
                         linestyle='--', linewidth=2, label=f'중앙값: ${self.orders_df["unit_price"].median():.2f}')
        axes[1,1].set_title('판매된 칵테일 가격 분포', fontweight='bold')
        axes[1,1].set_xlabel('가격 ($)')
        axes[1,1].set_ylabel('판매 횟수')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        
        # 5. 가격대별 평균 주문 크기
        categories = list(price_stats.keys())
        avg_order_sizes = [stats['avg_order_size'] for stats in price_stats.values()]
        
        bars = axes[2,0].bar(categories, avg_order_sizes, 
                            color=['green', 'orange', 'red'], alpha=0.8)
        axes[2,0].set_title('가격대별 평균 주문 크기', fontweight='bold')
        axes[2,0].set_ylabel('평균 주문량 (잔)')
        axes[2,0].tick_params(axis='x', rotation=0)
        
        # 값 표시
        for bar, value in zip(bars, avg_order_sizes):
            axes[2,0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_order_sizes)*0.01,
                          f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # 6. 매출 기여도 파이 차트
        revenue_data = self.price_analysis['total_price']
        colors = ['lightgreen', 'orange', 'lightcoral']
        
        wedges, texts, autotexts = axes[2,1].pie(revenue_data.values, labels=revenue_data.index, 
                                                autopct='%1.1f%%', colors=colors, startangle=90)
        axes[2,1].set_title('가격대별 매출 기여도', fontweight='bold')
        
        # 텍스트 스타일링
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
        
        plt.tight_layout(pad=4.0)
        plt.subplots_adjust(hspace=0.5, wspace=0.3, top=0.93)
        
        if show_plots:
            plt.show()
        
        return fig
    
    def generate_report(self):
        """가격대별 선호도 분석 리포트를 생성합니다."""
        if self.price_analysis is None:
            self.analyze_price_preferences()
        
        price_stats = self.analyze_price_sensitivity()
        elasticity_metrics = self.calculate_elasticity_metrics()
        
        total_quantity = self.price_analysis['quantity'].sum()
        total_revenue = self.price_analysis['total_price'].sum()
        
        report = f"""
K-tail 가격대별 선호도 분석 리포트
{'='*50}

가격대별 판매 현황:
"""
        
        for category, stats in self.price_analysis.iterrows():
            quantity_pct = (stats['quantity'] / total_quantity) * 100
            revenue_pct = (stats['total_price'] / total_revenue) * 100
            avg_order_size = stats['quantity'] / stats['order_count']
            
            report += f"\n{category}:\n"
            report += f"  • 판매량: {stats['quantity']}잔 ({quantity_pct:.1f}%)\n"
            report += f"  • 매출: ${stats['total_price']:,.2f} ({revenue_pct:.1f}%)\n"
            report += f"  • 주문 건수: {stats['order_count']}건\n"
            report += f"  • 평균 가격: ${stats['unit_price']:.2f}\n"
            report += f"  • 평균 주문량: {avg_order_size:.1f}잔/주문\n"
        
        report += f"\n시간대별 가격 선호 패턴:\n"
        
        for category in self.price_analysis.index:
            peak_hour = price_stats[category]['peak_hours']
            peak_season = price_stats[category]['peak_season']
            report += f"• {category}: {peak_hour}시 피크, {peak_season} 선호\n"
        
        # 가격 탄력성 분석
        price_corr = elasticity_metrics['price_quantity_correlation']
        report += f"""
가격 민감도 분석:
• 가격-수량 상관관계: {price_corr:.3f} ({'역상관' if price_corr < -0.3 else '약한 관계' if abs(price_corr) < 0.3 else '정상관'})
• 수요 집중도: {elasticity_metrics['demand_concentration']:.1%}
• 가격 분산도: ${elasticity_metrics['price_dispersion']:.2f}

매출 기여도 분석:
"""
        
        for category, contribution in elasticity_metrics['revenue_contribution'].items():
            report += f"• {category}: {contribution['contribution']:.1f}% (누적 {contribution['cumulative']:.1f}%)\n"
        
        # 비즈니스 인사이트
        most_popular = self.price_analysis['quantity'].idxmax()
        highest_revenue = self.price_analysis['total_price'].idxmax()
        # 평균 단가가 가장 높은 가격대
        avg_price_per_unit = self.price_analysis['total_price'] / self.price_analysis['quantity']
        best_margin = avg_price_per_unit.idxmax()
        
        report += f"""
핵심 비즈니스 인사이트:
• 가장 인기 가격대: {most_popular}
• 최고 매출 가격대: {highest_revenue}
• 최고 단가 효율: {best_margin}
• 가격 전략: {'프리미엄 전략 유효' if price_corr > 0 else '가격 경쟁력 중요' if price_corr < -0.3 else '가격 중립적'}

추천 전략:
"""
        
        # 가격대별 추천 전략
        if most_popular == highest_revenue:
            report += "• 현재 가격 정책이 최적화되어 있음\n"
        else:
            report += f"• {highest_revenue} 가격대 확대 및 {most_popular} 가격대 유지 필요\n"
        
        if elasticity_metrics['demand_concentration'] > 0.5:
            report += "• 특정 가격대 집중도 높음 - 다양한 가격대 메뉴 확대 고려\n"
        
        # 시간대별 전략
        peak_hours_by_price = {}
        for category, stats in price_stats.items():
            hour = stats['peak_hours']
            if hour not in peak_hours_by_price:
                peak_hours_by_price[hour] = []
            peak_hours_by_price[hour].append(category)
        
        report += f"• 시간대별 가격 전략: 특정 시간대에 맞는 가격대 프로모션\n"
        report += f"• 계절별 메뉴 전략: 계절에 따른 가격대별 메뉴 구성 조정\n"
        
        return report

def run_price_preference_analysis(show_plots=True, return_fig=False):
    """가격대별 선호도 분석을 실행하는 메인 함수 (GUI에서 호출)"""
    analyzer = PricePreferenceAnalyzer()
    
    # 데이터 로딩
    if not analyzer.load_data():
        return None
    
    # 분석 실행
    analyzer.analyze_price_preferences()
    
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
    print("가격대별 선호도 분석을 시작합니다...")
    analyzer = run_price_preference_analysis()
    
    if analyzer:
        print("가격대별 선호도 분석이 완료되었습니다!")
        
        # 추가 인사이트
        most_popular = analyzer.price_analysis['quantity'].idxmax()
        highest_revenue = analyzer.price_analysis['total_price'].idxmax()
        
        print(f"\n핵심 발견사항:")
        print(f"• 가장 인기 가격대: {most_popular}")
        print(f"• 최고 매출 가격대: {highest_revenue}")
        print(f"• 가격 전략 최적화 필요")
    else:
        print("ERROR: 분석 실행 중 오류가 발생했습니다.")
