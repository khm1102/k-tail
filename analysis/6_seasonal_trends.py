"""
6. 계절별 재료 트렌드 분석
K-tail 칵테일 바의 계절별 재료 사용 패턴과 트렌드를 분석하고 시각화합니다.
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

class SeasonalIngredientAnalyzer:
    def __init__(self):
        self.orders_df = None
        self.cocktails_df = None
        self.cocktail_info = {}
        self.seasonal_ingredients = {}
        self.seasonal_patterns = {}
        
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
            
            # 계절 정보 추가
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
            
            print(f"주문 데이터: {len(self.orders_df)}건")
            print(f"칵테일 메뉴: {len(self.cocktails_df)}개")
            print(f"분석 기간: {self.orders_df['timestamp'].min()} ~ {self.orders_df['timestamp'].max()}")
            return True
            
        except Exception as e:
            print(f"데이터 로딩 실패: {e}")
            return False
    
    def analyze_seasonal_ingredients(self):
        """계절별 재료 사용 패턴을 분석합니다."""
        self.seasonal_ingredients = {}
        
        for season in ['봄', '여름', '가을', '겨울']:
            seasonal_orders = self.orders_df[self.orders_df['season'] == season]
            season_ingredient_usage = {}
            
            for _, order in seasonal_orders.iterrows():
                cocktail_name = order['cocktail_name']
                quantity = order['quantity']
                
                if cocktail_name in self.cocktail_info:
                    ingredients_str = self.cocktail_info[cocktail_name].get('Ingredients', '')
                    if ingredients_str:
                        ingredients = [ing.strip().split('(')[0].strip() 
                                     for ing in ingredients_str.split(',')]
                        
                        for ingredient in ingredients:
                            if ingredient:
                                season_ingredient_usage[ingredient] = season_ingredient_usage.get(ingredient, 0) + quantity
            
            self.seasonal_ingredients[season] = season_ingredient_usage
    
    def identify_seasonal_patterns(self):
        """계절별 패턴을 식별합니다."""
        if not self.seasonal_ingredients:
            self.analyze_seasonal_ingredients()
        
        # 전체 재료 목록
        all_ingredients = set()
        for season_ingredients in self.seasonal_ingredients.values():
            all_ingredients.update(season_ingredients.keys())
        
        # 계절별 특성 분석
        self.seasonal_patterns = {}
        
        for season, ingredients in self.seasonal_ingredients.items():
            total_usage = sum(ingredients.values()) if ingredients else 0
            top_ingredients = dict(sorted(ingredients.items(), key=lambda x: x[1], reverse=True)[:10])
            
            # 계절별 특화 재료 (다른 계절 대비 높은 비율)
            seasonal_specialty = {}
            for ingredient, usage in ingredients.items():
                total_ingredient_usage = sum(
                    other_season.get(ingredient, 0) 
                    for other_season in self.seasonal_ingredients.values()
                )
                if total_ingredient_usage > 0:
                    seasonal_ratio = usage / total_ingredient_usage
                    if seasonal_ratio > 0.4:  # 40% 이상이면 계절 특화
                        seasonal_specialty[ingredient] = seasonal_ratio
            
            self.seasonal_patterns[season] = {
                'total_usage': total_usage,
                'top_ingredients': top_ingredients,
                'seasonal_specialty': dict(sorted(seasonal_specialty.items(), 
                                                key=lambda x: x[1], reverse=True)[:5]),
                'ingredient_count': len(ingredients),
                'avg_usage_per_ingredient': total_usage / len(ingredients) if ingredients else 0
            }
        
        return self.seasonal_patterns
    
    def analyze_ingredient_seasonality(self):
        """개별 재료의 계절성을 분석합니다."""
        all_ingredients = set()
        for season_ingredients in self.seasonal_ingredients.values():
            all_ingredients.update(season_ingredients.keys())
        
        ingredient_seasonality = {}
        
        for ingredient in all_ingredients:
            seasonal_usage = {}
            for season in ['봄', '여름', '가을', '겨울']:
                usage = self.seasonal_ingredients[season].get(ingredient, 0)
                seasonal_usage[season] = usage
            
            total_usage = sum(seasonal_usage.values())
            if total_usage > 0:
                # 계절별 비율 계산
                seasonal_ratios = {season: usage/total_usage for season, usage in seasonal_usage.items()}
                
                # 가장 높은 계절과 비율
                peak_season = max(seasonal_ratios, key=seasonal_ratios.get)
                peak_ratio = seasonal_ratios[peak_season]
                
                # 계절성 지수 (표준편차 기반)
                seasonality_index = np.std(list(seasonal_ratios.values()))
                
                ingredient_seasonality[ingredient] = {
                    'seasonal_usage': seasonal_usage,
                    'seasonal_ratios': seasonal_ratios,
                    'peak_season': peak_season,
                    'peak_ratio': peak_ratio,
                    'seasonality_index': seasonality_index,
                    'total_usage': total_usage
                }
        
        return ingredient_seasonality
    
    def create_visualizations(self, show_plots=True):
        """계절별 재료 트렌드 시각화를 생성합니다."""
        if not self.seasonal_ingredients:
            self.analyze_seasonal_ingredients()
        
        self.identify_seasonal_patterns()
        ingredient_seasonality = self.analyze_ingredient_seasonality()
        
        fig, axes = plt.subplots(3, 2, figsize=(22, 26))
        fig.suptitle('K-tail 계절별 재료 트렌드 분석', fontsize=16, fontweight='bold', y=0.98)
        
        # 1. 계절별 총 재료 사용량
        seasonal_totals = {season: sum(ingredients.values()) 
                          for season, ingredients in self.seasonal_ingredients.items()}
        
        colors = {'봄': 'lightgreen', '여름': 'orange', '가을': 'brown', '겨울': 'lightblue'}
        bars = axes[0,0].bar(seasonal_totals.keys(), seasonal_totals.values(), 
                            color=[colors[season] for season in seasonal_totals.keys()], alpha=0.8)
        axes[0,0].set_title('계절별 총 재료 사용량', fontweight='bold')
        axes[0,0].set_ylabel('총 사용량')
        
        # 값 표시
        for bar, value in zip(bars, seasonal_totals.values()):
            axes[0,0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(seasonal_totals.values())*0.01,
                          f'{int(value)}', ha='center', va='bottom', fontweight='bold')
        
        # 2. 계절별 재료 사용량 히트맵
        # TOP 15 재료만 선택
        all_ingredient_usage = {}
        for season_ingredients in self.seasonal_ingredients.values():
            for ingredient, usage in season_ingredients.items():
                all_ingredient_usage[ingredient] = all_ingredient_usage.get(ingredient, 0) + usage
        
        top_ingredients = sorted(all_ingredient_usage.items(), key=lambda x: x[1], reverse=True)[:15]
        top_ingredient_names = [ing[0] for ing in top_ingredients]
        
        heatmap_data = []
        season_order = ['봄', '여름', '가을', '겨울']
        for season in season_order:
            row = []
            for ingredient in top_ingredient_names:
                usage = self.seasonal_ingredients[season].get(ingredient, 0)
                row.append(usage)
            heatmap_data.append(row)
        
        if heatmap_data and top_ingredient_names:
            sns.heatmap(heatmap_data, 
                        xticklabels=[ing[:10] + '...' if len(ing) > 10 else ing for ing in top_ingredient_names],
                        yticklabels=season_order,
                        annot=True, fmt='d', cmap='YlOrRd', ax=axes[0,1], cbar_kws={'label': '사용량'})
            axes[0,1].set_title('계절별 TOP 15 재료 사용량 히트맵', fontweight='bold')
            axes[0,1].set_xlabel('재료')
            axes[0,1].set_ylabel('계절')
        
        # 3. 계절별 특화 재료 (레이더 차트 대신 바 차트)
        seasonal_specialties = {}
        for season, patterns in self.seasonal_patterns.items():
            if patterns['seasonal_specialty']:
                top_specialty = list(patterns['seasonal_specialty'].items())[:3]
                seasonal_specialties[season] = top_specialty
        
        if seasonal_specialties:
            x_pos = np.arange(len(seasonal_specialties))
            width = 0.2
            
            for i, season in enumerate(seasonal_specialties.keys()):
                if seasonal_specialties[season]:
                    ingredient_names = [item[0][:8] + '..' if len(item[0]) > 8 else item[0] 
                                      for item in seasonal_specialties[season]]
                    ratios = [item[1] * 100 for item in seasonal_specialties[season]]
                    
                    for j, (name, ratio) in enumerate(zip(ingredient_names, ratios)):
                        axes[1,0].bar(i + j*width, ratio, width, 
                                     label=f'{season}-{name}' if i == 0 else "", 
                                     color=colors[season], alpha=0.7)
            
            axes[1,0].set_title('계절별 특화 재료 (계절 집중도)', fontweight='bold')
            axes[1,0].set_xlabel('계절')
            axes[1,0].set_ylabel('계절 집중도 (%)')
            axes[1,0].set_xticks(x_pos + width)
            axes[1,0].set_xticklabels(seasonal_specialties.keys())
        
        # 4. 재료별 계절성 지수
        high_seasonality = {ing: data['seasonality_index'] 
                           for ing, data in ingredient_seasonality.items() 
                           if data['total_usage'] > 10}  # 충분한 사용량이 있는 재료만
        
        if high_seasonality:
            top_seasonal = dict(sorted(high_seasonality.items(), key=lambda x: x[1], reverse=True)[:10])
            
            ingredient_names = [ing[:12] + '...' if len(ing) > 12 else ing for ing in top_seasonal.keys()]
            seasonality_scores = list(top_seasonal.values())
            
            bars = axes[1,1].barh(range(len(ingredient_names)), seasonality_scores, 
                                 color='mediumpurple', alpha=0.8)
            axes[1,1].set_yticks(range(len(ingredient_names)))
            axes[1,1].set_yticklabels(ingredient_names)
            axes[1,1].set_title('재료별 계절성 지수 (TOP 10)', fontweight='bold')
            axes[1,1].set_xlabel('계절성 지수 (높을수록 계절적 특성 강함)')
            axes[1,1].invert_yaxis()
        
        # 5. 월별 재료 다양성 트렌드
        monthly_diversity = self.orders_df.groupby('month').apply(
            lambda x: len(set(ingredient 
                            for _, order in x.iterrows() 
                            for ingredient in self._get_ingredients(order['cocktail_name'])))
        )
        
        axes[2,0].plot(monthly_diversity.index, monthly_diversity.values, 
                      marker='o', linewidth=3, markersize=8, color='green')
        axes[2,0].fill_between(monthly_diversity.index, monthly_diversity.values, 
                              alpha=0.3, color='green')
        axes[2,0].set_title('월별 재료 다양성 트렌드', fontweight='bold')
        axes[2,0].set_xlabel('월')
        axes[2,0].set_ylabel('사용된 재료 종류 수')
        axes[2,0].grid(True, alpha=0.3)
        axes[2,0].set_xticks(range(1, 13))
        
        # 6. 계절별 재료 카테고리 분포
        ingredient_categories = {
            'Spirits': ['Gin', 'Vodka', 'Rum', 'Whiskey', 'Tequila', 'Mezcal', 'Bourbon'],
            'Liqueurs': ['Liqueur', 'Aperitivo', 'Amaretto', 'Cointreau'],
            'Citrus': ['Lemon', 'Lime', 'Orange'],
            'Others': []
        }
        
        seasonal_category_data = {}
        for season in ['봄', '여름', '가을', '겨울']:
            category_usage = {cat: 0 for cat in ingredient_categories.keys()}
            
            for ingredient, usage in self.seasonal_ingredients[season].items():
                categorized = False
                for category, keywords in ingredient_categories.items():
                    if any(keyword.lower() in ingredient.lower() for keyword in keywords):
                        category_usage[category] += usage
                        categorized = True
                        break
                if not categorized:
                    category_usage['Others'] += usage
            
            seasonal_category_data[season] = category_usage
        
        # 스택 바 차트
        categories = list(ingredient_categories.keys())
        seasons = ['봄', '여름', '가을', '겨울']
        
        bottom = np.zeros(len(seasons))
        colors_cat = plt.cm.Set3(np.linspace(0, 1, len(categories)))
        
        for i, category in enumerate(categories):
            values = [seasonal_category_data[season][category] for season in seasons]
            axes[2,1].bar(seasons, values, bottom=bottom, label=category, 
                         color=colors_cat[i], alpha=0.8)
            bottom += values
        
        axes[2,1].set_title('계절별 재료 카테고리 분포', fontweight='bold')
        axes[2,1].set_ylabel('사용량')
        axes[2,1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout(pad=4.0)
        plt.subplots_adjust(hspace=0.7, wspace=0.5, top=0.92, bottom=0.08)
        
        if show_plots:
            plt.show()
        
        return fig
    
    def _get_ingredients(self, cocktail_name):
        """칵테일명으로부터 재료 리스트를 반환합니다."""
        if cocktail_name in self.cocktail_info:
            ingredients_str = self.cocktail_info[cocktail_name].get('Ingredients', '')
            if ingredients_str:
                return [ing.strip().split('(')[0].strip() 
                       for ing in ingredients_str.split(',') if ing.strip()]
        return []
    
    def generate_report(self):
        """계절별 재료 트렌드 분석 리포트를 생성합니다."""
        if not self.seasonal_patterns:
            self.identify_seasonal_patterns()
        
        ingredient_seasonality = self.analyze_ingredient_seasonality()
        
        # 가장 계절성이 강한 재료들
        high_seasonality = {ing: data for ing, data in ingredient_seasonality.items() 
                           if data['seasonality_index'] > 0.3 and data['total_usage'] > 5}
        
        report = f"""
K-tail 계절별 재료 트렌드 분석 리포트
{'='*50}

계절별 재료 사용 현황:
"""
        
        for season, patterns in self.seasonal_patterns.items():
            season_name_only = {'봄': '봄', '여름': '여름', '가을': '가을', '겨울': '겨울'}
            report += f"\n{season_name_only[season]} {season}:\n"
            report += f"  • 총 사용량: {patterns['total_usage']:,}회\n"
            report += f"  • 재료 종류: {patterns['ingredient_count']}개\n"
            report += f"  • 평균 사용량: {patterns['avg_usage_per_ingredient']:.1f}회/재료\n"
            
            if patterns['top_ingredients']:
                top_3 = list(patterns['top_ingredients'].items())[:3]
                report += f"  • TOP 3 재료: {', '.join([f'{ing}({usage}회)' for ing, usage in top_3])}\n"
            
            if patterns['seasonal_specialty']:
                specialty = list(patterns['seasonal_specialty'].items())[:2]
                report += f"  • 특화 재료: {', '.join([f'{ing}({ratio:.1%})' for ing, ratio in specialty])}\n"
        
        report += f"\n계절성이 강한 재료 TOP 5:\n"
        
        if high_seasonality:
            top_seasonal = sorted(high_seasonality.items(), 
                                key=lambda x: x[1]['seasonality_index'], reverse=True)[:5]
            
            for i, (ingredient, data) in enumerate(top_seasonal, 1):
                peak_season = data['peak_season']
                peak_ratio = data['peak_ratio']
                seasonality = data['seasonality_index']
                
                report += f"{i}. {ingredient}: {peak_season} 집중 ({peak_ratio:.1%}, 계절성지수: {seasonality:.2f})\n"
        
        # 계절별 특성 분석
        seasonal_totals = {season: patterns['total_usage'] 
                          for season, patterns in self.seasonal_patterns.items()}
        peak_season = max(seasonal_totals, key=seasonal_totals.get)
        quiet_season = min(seasonal_totals, key=seasonal_totals.get)
        
        # 계절간 격차 계산 (0으로 나누기 방지)
        if seasonal_totals[quiet_season] > 0:
            seasonal_gap = (seasonal_totals[peak_season]/seasonal_totals[quiet_season]-1)*100
        else:
            seasonal_gap = float('inf') if seasonal_totals[peak_season] > 0 else 0
        
        report += f"""
계절별 트렌드 인사이트:
• 최고 성수기: {peak_season} ({seasonal_totals[peak_season]:,}회 사용)
• 최저 비수기: {quiet_season} ({seasonal_totals[quiet_season]:,}회 사용)
• 계절간 격차: {seasonal_gap:.1f}% {'(매우 큰 차이)' if seasonal_gap == float('inf') else ''}

비즈니스 추천사항:
• 계절별 메뉴 개발: 각 계절 특화 재료 활용한 시즌 메뉴
• 재고 관리: 계절성 강한 재료는 사전 수요 예측 필요
• 마케팅 전략: {peak_season} 성수기 대비 특별 프로모션
• 원가 관리: 계절별 재료 가격 변동 고려한 메뉴 가격 조정
• 신메뉴 타이밍: 계절 전환기 신메뉴 출시 효과적
"""
        
        return report

def run_seasonal_ingredient_analysis(show_plots=True, return_fig=False):
    """계절별 재료 트렌드 분석을 실행하는 메인 함수 (GUI에서 호출)"""
    analyzer = SeasonalIngredientAnalyzer()
    
    # 데이터 로딩
    if not analyzer.load_data():
        return None
    
    # 분석 실행
    analyzer.analyze_seasonal_ingredients()
    analyzer.identify_seasonal_patterns()
    
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
    print("계절별 재료 트렌드 분석을 시작합니다...")
    analyzer = run_seasonal_ingredient_analysis()
    
    if analyzer:
        print("계절별 재료 트렌드 분석이 완료되었습니다!")
        
        # 추가 인사이트
        seasonal_totals = {season: sum(ingredients.values()) 
                          for season, ingredients in analyzer.seasonal_ingredients.items()}
        peak_season = max(seasonal_totals, key=seasonal_totals.get)
        
        print(f"\n핵심 발견사항:")
        print(f"• 최고 성수기: {peak_season}")
        print(f"• 계절별 재료 사용 패턴 뚜렷함")
        print(f"• 계절별 맞춤 메뉴 전략 필요")
    else:
        print("ERROR: 분석 실행 중 오류가 발생했습니다.")
