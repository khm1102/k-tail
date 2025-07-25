"""
5. 재료별 사용 빈도 분석
K-tail 칵테일 바의 재료별 사용 빈도와 분포를 분석하고 시각화합니다.
GUI에서 호출되어 그래프를 생성합니다.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class IngredientFrequencyAnalyzer:
    def __init__(self):
        self.orders_df = None
        self.cocktails_df = None
        self.cocktail_info = {}
        self.ingredient_usage = {}
        self.frequency_stats = {}
        
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
            
            # 칵테일 메뉴 데이터 로딩
            self.cocktails_df = pd.read_csv(cocktails_path)
            cocktails_df_unique = self.cocktails_df.drop_duplicates(subset=['Cocktail Name'], keep='first')
            self.cocktail_info = cocktails_df_unique.set_index('Cocktail Name').to_dict('index')
            
            print(f"주문 데이터: {len(self.orders_df)}건")
            print(f"칵테일 메뉴: {len(self.cocktails_df)}개")
            return True
            
        except Exception as e:
            print(f"데이터 로딩 실패: {e}")
            return False
    
    def calculate_ingredient_frequency(self):
        """재료별 사용 빈도를 계산합니다."""
        self.ingredient_usage = {}
        
        for _, order in self.orders_df.iterrows():
            cocktail_name = order['cocktail_name']
            quantity = order['quantity']
            
            # 해당 칵테일의 재료 찾기
            if cocktail_name in self.cocktail_info:
                ingredients_str = self.cocktail_info[cocktail_name].get('Ingredients', '')
                if ingredients_str:
                    ingredients = [ing.strip().split('(')[0].strip() 
                                 for ing in ingredients_str.split(',')]
                    
                    for ingredient in ingredients:
                        if ingredient:
                            self.ingredient_usage[ingredient] = self.ingredient_usage.get(ingredient, 0) + quantity
    
    def analyze_frequency_distribution(self):
        """사용 빈도 분포를 분석합니다."""
        if not self.ingredient_usage:
            self.calculate_ingredient_frequency()
        
        usage_values = list(self.ingredient_usage.values())
        
        self.frequency_stats = {
            'total_ingredients': len(self.ingredient_usage),
            'total_usage': sum(usage_values),
            'mean_usage': np.mean(usage_values),
            'median_usage': np.median(usage_values),
            'std_usage': np.std(usage_values),
            'min_usage': min(usage_values),
            'max_usage': max(usage_values),
            'q25': np.percentile(usage_values, 25),
            'q75': np.percentile(usage_values, 75),
            'skewness': stats.skew(usage_values),
            'kurtosis': stats.kurtosis(usage_values)
        }
        
        return self.frequency_stats
    
    def categorize_by_frequency(self):
        """빈도에 따라 재료를 카테고리별로 분류합니다."""
        if not self.frequency_stats:
            self.analyze_frequency_distribution()
        
        categories = {
            'Very High (Top 10%)': [],
            'High (Top 25%)': [],
            'Medium (25-75%)': [],
            'Low (Bottom 25%)': [],
            'Very Low (Bottom 10%)': []
        }
        
        sorted_ingredients = sorted(self.ingredient_usage.items(), key=lambda x: x[1], reverse=True)
        total_count = len(sorted_ingredients)
        
        for i, (ingredient, usage) in enumerate(sorted_ingredients):
            percentile = (i / total_count) * 100
            
            if percentile < 10:
                categories['Very High (Top 10%)'].append((ingredient, usage))
            elif percentile < 25:
                categories['High (Top 25%)'].append((ingredient, usage))
            elif percentile < 75:
                categories['Medium (25-75%)'].append((ingredient, usage))
            elif percentile < 90:
                categories['Low (Bottom 25%)'].append((ingredient, usage))
            else:
                categories['Very Low (Bottom 10%)'].append((ingredient, usage))
        
        return categories
    
    def calculate_concentration_metrics(self):
        """재료 사용 집중도 지표를 계산합니다."""
        sorted_usage = sorted(self.ingredient_usage.values(), reverse=True)
        total_usage = sum(sorted_usage)
        
        # 지니 계수 계산
        n = len(sorted_usage)
        cumsum = np.cumsum(sorted_usage)
        gini = (n + 1 - 2 * sum((n + 1 - i) * usage for i, usage in enumerate(sorted_usage, 1))) / (n * total_usage)
        
        # 상위 N% 집중도
        concentration = {
            'top_10_percent': sum(sorted_usage[:max(1, n//10)]) / total_usage * 100,
            'top_20_percent': sum(sorted_usage[:max(1, n//5)]) / total_usage * 100,
            'top_50_percent': sum(sorted_usage[:max(1, n//2)]) / total_usage * 100,
            'gini_coefficient': gini,
            'herfindahl_index': sum((usage/total_usage)**2 for usage in sorted_usage)
        }
        
        return concentration
    
    def create_visualizations(self, show_plots=True):
        """재료별 사용 빈도 분석 시각화를 생성합니다."""
        if not self.ingredient_usage:
            self.calculate_ingredient_frequency()
        
        self.analyze_frequency_distribution()
        categories = self.categorize_by_frequency()
        concentration = self.calculate_concentration_metrics()
        
        fig, axes = plt.subplots(2, 3, figsize=(20, 14))
        fig.suptitle('K-tail 재료별 사용 빈도 분석', fontsize=16, fontweight='bold', y=0.98)
        
        usage_values = list(self.ingredient_usage.values())
        
        # 1. 사용 빈도 히스토그램
        axes[0,0].hist(usage_values, bins=30, color='skyblue', alpha=0.7, edgecolor='black')
        axes[0,0].axvline(self.frequency_stats['mean_usage'], color='red', linestyle='--', 
                         linewidth=2, label=f"평균: {self.frequency_stats['mean_usage']:.1f}")
        axes[0,0].axvline(self.frequency_stats['median_usage'], color='green', linestyle='--', 
                         linewidth=2, label=f"중앙값: {self.frequency_stats['median_usage']:.1f}")
        axes[0,0].set_title('재료 사용 빈도 분포', fontweight='bold')
        axes[0,0].set_xlabel('사용 횟수')
        axes[0,0].set_ylabel('재료 개수')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        
        # 2. 박스플롯
        axes[0,1].boxplot(usage_values, vert=True, patch_artist=True,
                         boxprops=dict(facecolor='lightcoral', alpha=0.7),
                         medianprops=dict(color='red', linewidth=2))
        axes[0,1].set_title('재료 사용 빈도 박스플롯', fontweight='bold')
        axes[0,1].set_ylabel('사용 횟수')
        axes[0,1].grid(True, alpha=0.3)
        
        # 통계 정보 텍스트 추가
        stats_text = f"""
Q1: {self.frequency_stats['q25']:.1f}
Q2(중앙값): {self.frequency_stats['median_usage']:.1f}
Q3: {self.frequency_stats['q75']:.1f}
IQR: {self.frequency_stats['q75'] - self.frequency_stats['q25']:.1f}
"""
        axes[0,1].text(1.1, max(usage_values)*0.7, stats_text, 
                      bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat"))
        
        # 3. 빈도 카테고리별 분포
        category_counts = {cat: len(items) for cat, items in categories.items()}
        colors = ['red', 'orange', 'yellow', 'lightblue', 'lightgray']
        
        wedges, texts, autotexts = axes[0,2].pie(category_counts.values(), 
                                                labels=category_counts.keys(),
                                                autopct='%1.1f%%', colors=colors, startangle=90)
        axes[0,2].set_title('빈도별 재료 분포', fontweight='bold')
        
        # 4. 누적 분포 (파레토 차트)
        sorted_ingredients = sorted(self.ingredient_usage.items(), key=lambda x: x[1], reverse=True)
        cumulative_usage = np.cumsum([usage for _, usage in sorted_ingredients])
        cumulative_percent = (cumulative_usage / cumulative_usage[-1]) * 100
        
        x_pos = range(1, len(sorted_ingredients) + 1)
        axes[1,0].bar(x_pos, [usage for _, usage in sorted_ingredients], 
                     color='lightblue', alpha=0.7, label='개별 사용량')
        
        ax_twin = axes[1,0].twinx()
        ax_twin.plot(x_pos, cumulative_percent, color='red', marker='o', 
                    linewidth=2, markersize=2, label='누적 비율')
        ax_twin.axhline(y=80, color='green', linestyle='--', label='80% 라인')
        
        axes[1,0].set_title('재료 사용량 파레토 차트', fontweight='bold')
        axes[1,0].set_xlabel('재료 순위')
        axes[1,0].set_ylabel('사용 횟수')
        ax_twin.set_ylabel('누적 비율 (%)')
        axes[1,0].legend(loc='upper left')
        ax_twin.legend(loc='upper right')
        
        # 5. 상위 재료별 상세 빈도
        top_15 = sorted_ingredients[:15]
        ingredients_names = [ing[:15] + '...' if len(ing) > 15 else ing for ing, _ in top_15]
        usage_counts = [usage for _, usage in top_15]
        
        y_pos = range(len(ingredients_names))
        bars = axes[1,1].barh(y_pos, usage_counts, color=plt.cm.viridis(np.linspace(0, 1, len(usage_counts))))
        axes[1,1].set_yticks(y_pos)
        axes[1,1].set_yticklabels(ingredients_names)
        axes[1,1].set_title('TOP 15 재료 사용 빈도', fontweight='bold')
        axes[1,1].set_xlabel('사용 횟수')
        axes[1,1].invert_yaxis()
        
        # 값 표시
        for i, bar in enumerate(bars):
            width = bar.get_width()
            axes[1,1].text(width + max(usage_counts)*0.01, bar.get_y() + bar.get_height()/2,
                          f'{int(width)}', ha='left', va='center', fontsize=8)
        
        # 6. 집중도 지표 시각화
        concentration_data = {
            'TOP 10%': concentration['top_10_percent'],
            'TOP 20%': concentration['top_20_percent'], 
            'TOP 50%': concentration['top_50_percent']
        }
        
        bars = axes[1,2].bar(concentration_data.keys(), concentration_data.values(), 
                            color=['red', 'orange', 'yellow'], alpha=0.8)
        axes[1,2].set_title('재료 사용 집중도', fontweight='bold')
        axes[1,2].set_ylabel('전체 사용량 대비 비율 (%)')
        
        # 값 표시
        for bar, value in zip(bars, concentration_data.values()):
            axes[1,2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                          f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # 지니계수 텍스트 추가
        axes[1,2].text(0.5, max(concentration_data.values())*0.5, 
                      f'지니계수: {concentration["gini_coefficient"]:.3f}\n(0=완전균등, 1=완전불균등)',
                      ha='center', va='center', transform=axes[1,2].transAxes,
                      bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        plt.tight_layout(pad=3.0)
        plt.subplots_adjust(hspace=0.4, wspace=0.6)

        if show_plots:
            plt.show()
        
        return fig
    
    def generate_report(self):
        """재료별 사용 빈도 분석 리포트를 생성합니다."""
        if not self.frequency_stats:
            self.analyze_frequency_distribution()
        
        categories = self.categorize_by_frequency()
        concentration = self.calculate_concentration_metrics()
        
        report = f"""
K-tail 재료별 사용 빈도 분석 리포트
{'='*50}

기본 통계:
• 총 재료 종류: {self.frequency_stats['total_ingredients']}개
• 총 사용 횟수: {self.frequency_stats['total_usage']:,}회
• 평균 사용 횟수: {self.frequency_stats['mean_usage']:.1f}회
• 중앙값: {self.frequency_stats['median_usage']:.1f}회
• 표준편차: {self.frequency_stats['std_usage']:.1f}
• 최소/최대: {self.frequency_stats['min_usage']}/{self.frequency_stats['max_usage']}회

분포 특성:
• Q1 (25%): {self.frequency_stats['q25']:.1f}회
• Q3 (75%): {self.frequency_stats['q75']:.1f}회
• IQR: {self.frequency_stats['q75'] - self.frequency_stats['q25']:.1f}회
• 왜도(Skewness): {self.frequency_stats['skewness']:.2f}
• 첨도(Kurtosis): {self.frequency_stats['kurtosis']:.2f}

빈도별 재료 분류:
"""
        
        for category, items in categories.items():
            if items:
                report += f"\n{category}: {len(items)}개\n"
                for ingredient, usage in items[:3]:  # 상위 3개만 표시
                    report += f"  • {ingredient}: {usage}회\n"
                if len(items) > 3:
                    report += f"  • ... 외 {len(items)-3}개\n"
        
        report += f"""
집중도 분석:
• TOP 10% 재료가 전체 사용량의 {concentration['top_10_percent']:.1f}% 차지
• TOP 20% 재료가 전체 사용량의 {concentration['top_20_percent']:.1f}% 차지
• TOP 50% 재료가 전체 사용량의 {concentration['top_50_percent']:.1f}% 차지
• 지니 계수: {concentration['gini_coefficient']:.3f} (불균등 정도)
• 허핀달 지수: {concentration['herfindahl_index']:.3f} (시장 집중도)

운영 인사이트:
"""
        
        # 분포 특성에 따른 인사이트
        if self.frequency_stats['skewness'] > 1:
            report += "• 사용량이 매우 치우쳐 있음 - 소수 재료에 집중된 운영\n"
        elif self.frequency_stats['skewness'] > 0.5:
            report += "• 사용량이 다소 치우쳐 있음 - 핵심 재료 중심 운영\n"
        else:
            report += "• 사용량이 비교적 균등함 - 다양한 재료 활용\n"
        
        if concentration['top_20_percent'] > 80:
            report += "• 파레토 법칙 적용: 상위 20% 재료 집중 관리 필요\n"
        
        if concentration['gini_coefficient'] > 0.7:
            report += "• 높은 집중도: 핵심 재료 재고 관리 최우선\n"
        elif concentration['gini_coefficient'] > 0.5:
            report += "• 중간 집중도: 균형잡힌 재고 관리 전략 필요\n"
        else:
            report += "• 낮은 집중도: 모든 재료 균등한 관리 필요\n"
        
        report += f"• 재고 최적화: 상위 {min(10, len(self.ingredient_usage))}개 재료 우선 관리\n"
        report += "• 메뉴 개발: 저사용 재료 활용 신메뉴 고려\n"
        
        return report

def run_ingredient_frequency_analysis(show_plots=True, return_fig=False):
    """재료별 사용 빈도 분석을 실행하는 메인 함수 (GUI에서 호출)"""
    analyzer = IngredientFrequencyAnalyzer()
    
    # 데이터 로딩
    if not analyzer.load_data():
        return None
    
    # 분석 실행
    analyzer.calculate_ingredient_frequency()
    analyzer.analyze_frequency_distribution()
    
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
    print("재료별 사용 빈도 분석을 시작합니다...")
    analyzer = run_ingredient_frequency_analysis()
    
    if analyzer:
        print("재료별 사용 빈도 분석이 완료되었습니다!")
        
        # 추가 인사이트
        concentration = analyzer.calculate_concentration_metrics()
        print(f"\n핵심 발견사항:")
        print(f"• 재료 집중도: TOP 20%가 {concentration['top_20_percent']:.1f}% 차지")
        print(f"• 지니계수: {concentration['gini_coefficient']:.3f} (집중도 지표)")
        print(f"• 재료 다양성: {analyzer.frequency_stats['total_ingredients']}개 재료 사용")
    else:
        print("ERROR: 분석 실행 중 오류가 발생했습니다.")
