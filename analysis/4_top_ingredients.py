"""
4. 가장 많이 사용된 재료 TOP 10 분석
K-tail 칵테일 바에서 가장 많이 사용되는 재료를 분석하고 시각화합니다.
GUI에서 호출되어 그래프를 생성합니다.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class TopIngredientsAnalyzer:
    def __init__(self):
        self.orders_df = None
        self.cocktails_df = None
        self.cocktail_info = {}
        self.ingredient_usage = {}
        self.menu_ingredients = {}
        
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
    
    def extract_ingredients_from_menu(self):
        """칵테일 메뉴에서 재료 정보를 추출합니다."""
        self.menu_ingredients = {}
        
        for _, cocktail in self.cocktails_df.iterrows():
            ingredients_str = cocktail.get('Ingredients', '')
            if pd.isna(ingredients_str) or not ingredients_str:
                continue
            
            # 재료 파싱 (쉼표로 구분)
            ingredients = [ing.strip() for ing in ingredients_str.split(',')]
            
            for ingredient in ingredients:
                if ingredient:
                    # 재료명 정리 (수량 정보 제거)
                    clean_ingredient = ingredient.split('(')[0].strip()
                    if clean_ingredient:
                        self.menu_ingredients[clean_ingredient] = self.menu_ingredients.get(clean_ingredient, 0) + 1
    
    def calculate_actual_usage(self):
        """실제 주문 데이터 기반으로 재료 사용량을 계산합니다."""
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
    
    def get_top_ingredients(self, top_n=10):
        """TOP N 재료를 반환합니다."""
        # 실제 사용량 기준
        top_usage = dict(sorted(self.ingredient_usage.items(), 
                               key=lambda x: x[1], reverse=True)[:top_n])
        
        # 메뉴 포함 기준
        top_menu = dict(sorted(self.menu_ingredients.items(), 
                              key=lambda x: x[1], reverse=True)[:top_n])
        
        return top_usage, top_menu
    
    def analyze_ingredient_categories(self):
        """재료를 카테고리별로 분류합니다."""
        categories = {
            'Spirits': ['Gin', 'Vodka', 'Rum', 'Whiskey', 'Tequila', 'Mezcal', 'Bourbon', 'Brandy'],
            'Liqueurs': ['Liqueur', 'Aperitivo', 'Amaretto', 'Cointreau', 'Triple Sec', 'Vermouth'],
            'Juices': ['Juice', 'Lemon', 'Lime', 'Orange', 'Cranberry', 'Pineapple'],
            'Mixers': ['Syrup', 'Bitters', 'Soda', 'Tonic', 'Ginger', 'Club Soda'],
            'Garnish': ['Mint', 'Cherry', 'Olive', 'Twist', 'Salt', 'Sugar'],
            'Others': []
        }
        
        category_usage = {cat: 0 for cat in categories.keys()}
        ingredient_classification = {}
        
        for ingredient, usage in self.ingredient_usage.items():
            categorized = False
            for category, keywords in categories.items():
                if any(keyword.lower() in ingredient.lower() for keyword in keywords):
                    category_usage[category] += usage
                    ingredient_classification[ingredient] = category
                    categorized = True
                    break
            if not categorized:
                category_usage['Others'] += usage
                ingredient_classification[ingredient] = 'Others'
        
        return category_usage, ingredient_classification
    
    def create_visualizations(self, show_plots=True):
        """TOP 10 재료 분석 시각화를 생성합니다."""
        if not self.ingredient_usage:
            self.extract_ingredients_from_menu()
            self.calculate_actual_usage()
        
        top_usage, top_menu = self.get_top_ingredients(10)
        category_usage, ingredient_classification = self.analyze_ingredient_categories()
        
        fig, axes = plt.subplots(2, 2, figsize=(24, 20))
        fig.suptitle('K-tail TOP 10 재료 사용 분석', fontsize=18, fontweight='bold', y=0.97)
        
        # 1. TOP 10 가장 많이 사용된 재료 (실제 주문 기준)
        if top_usage:
            ingredients = list(top_usage.keys())[:10]
            usage_counts = list(top_usage.values())[:10]
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(ingredients)))
            bars = axes[0,0].barh(range(len(ingredients)), usage_counts, color=colors)
            axes[0,0].set_yticks(range(len(ingredients)))
            axes[0,0].set_yticklabels([ing[:25] + '...' if len(ing) > 25 else ing 
                                      for ing in ingredients], fontsize=10)
            axes[0,0].set_title('TOP 10 재료 (실제 사용량 기준)', fontweight='bold')
            axes[0,0].set_xlabel('총 사용 횟수')
            axes[0,0].invert_yaxis()
            
            # 값 표시
            for i, bar in enumerate(bars):
                width = bar.get_width()
                axes[0,0].text(width + max(usage_counts)*0.01, bar.get_y() + bar.get_height()/2,
                              f'{int(width)}', ha='left', va='center', fontweight='bold')
        
        # 2. TOP 10 메뉴에 가장 많이 포함된 재료
        if top_menu:
            menu_ingredients_list = list(top_menu.keys())[:10]
            menu_counts = list(top_menu.values())[:10]
            
            axes[0,1].bar(range(len(menu_ingredients_list)), menu_counts, 
                         color='lightcoral', alpha=0.8)
            axes[0,1].set_xticks(range(len(menu_ingredients_list)))
            axes[0,1].set_xticklabels([ing[:10] + '...' if len(ing) > 10 else ing 
                                      for ing in menu_ingredients_list], rotation=45)
            axes[0,1].set_title('TOP 10 재료 (메뉴 포함 빈도)', fontweight='bold')
            axes[0,1].set_ylabel('포함 메뉴 수')
            
            # 값 표시
            for i, count in enumerate(menu_counts):
                axes[0,1].text(i, count + max(menu_counts)*0.01, str(count), 
                              ha='center', va='bottom', fontweight='bold')
        
        # 3. 재료 카테고리별 사용량
        if category_usage:
            categories = list(category_usage.keys())
            usage_by_category = list(category_usage.values())
            
            # 0이 아닌 카테고리만 표시
            non_zero_cats = [(cat, usage) for cat, usage in zip(categories, usage_by_category) if usage > 0]
            if non_zero_cats:
                categories, usage_by_category = zip(*non_zero_cats)
                
                colors = plt.cm.Pastel1(np.linspace(0, 1, len(categories)))
                wedges, texts, autotexts = axes[1,0].pie(usage_by_category, labels=categories, 
                                                        autopct='%1.1f%%', colors=colors, startangle=90)
                axes[1,0].set_title('재료 카테고리별 사용 분포', fontweight='bold')
                
                # 텍스트 스타일링
                for autotext in autotexts:
                    autotext.set_color('black')
                    autotext.set_fontweight('bold')
        
        # 4. 재료별 사용 빈도 분포
        if self.ingredient_usage:
            usage_values = list(self.ingredient_usage.values())
            axes[1,1].hist(usage_values, bins=20, color='lightyellow', 
                          edgecolor='black', alpha=0.8)
            axes[1,1].axvline(np.mean(usage_values), color='red', linestyle='--', 
                             linewidth=2, label=f'평균: {np.mean(usage_values):.1f}')
            axes[1,1].axvline(np.median(usage_values), color='green', linestyle='--', 
                             linewidth=2, label=f'중앙값: {np.median(usage_values):.1f}')
            axes[1,1].set_title('재료별 사용 빈도 분포', fontweight='bold')
            axes[1,1].set_xlabel('사용 횟수')
            axes[1,1].set_ylabel('재료 개수')
            axes[1,1].legend()
            axes[1,1].grid(True, alpha=0.3)
        
        plt.subplots_adjust(left=0.15, right=0.95, top=0.92, bottom=0.08, hspace=0.5, wspace=0.4)
        
        if show_plots:
            plt.show()
        
        return fig
    
    def generate_report(self):
        """TOP 10 재료 분석 리포트를 생성합니다."""
        if not self.ingredient_usage:
            self.extract_ingredients_from_menu()
            self.calculate_actual_usage()
        
        top_usage, top_menu = self.get_top_ingredients(10)
        category_usage, ingredient_classification = self.analyze_ingredient_categories()
        
        total_usage = sum(self.ingredient_usage.values())
        total_ingredients = len(self.ingredient_usage)
        
        report = f"""
K-tail TOP 10 재료 사용 분석 리포트
{'='*50}

전체 재료 사용 현황:
• 총 사용된 재료 종류: {total_ingredients}개
• 총 재료 사용 횟수: {total_usage:,}회
• 평균 재료당 사용: {total_usage/total_ingredients:.1f}회

TOP 10 가장 많이 사용된 재료 (실제 주문 기준):
"""
        
        for i, (ingredient, usage) in enumerate(list(top_usage.items())[:10], 1):
            percentage = (usage / total_usage) * 100
            category = ingredient_classification.get(ingredient, 'Others')
            report += f"{i:2d}. {ingredient}: {usage:,}회 ({percentage:.1f}%) [{category}]\n"
        
        report += f"\nTOP 10 메뉴에 가장 많이 포함된 재료:\n"
        
        for i, (ingredient, count) in enumerate(list(top_menu.items())[:10], 1):
            report += f"{i:2d}. {ingredient}: {count}개 메뉴에 포함\n"
        
        report += f"\n재료 카테고리별 사용 현황:\n"
        
        for category, usage in sorted(category_usage.items(), key=lambda x: x[1], reverse=True):
            if usage > 0:
                percentage = (usage / total_usage) * 100
                report += f"• {category}: {usage:,}회 ({percentage:.1f}%)\n"
        
        # 파레토 분석
        top_5_usage = sum(list(top_usage.values())[:5])
        top_5_percentage = (top_5_usage / total_usage) * 100
        
        report += f"""
재료 운영 인사이트:
• TOP 5 재료가 전체 사용량의 {top_5_percentage:.1f}% 차지 (파레토 법칙)
• 핵심 재료 집중 관리: {', '.join(list(top_usage.keys())[:5])}
• 재고 최적화 대상: 상위 10개 재료 위주 관리
• 카테고리별 밸런스: {max(category_usage, key=category_usage.get)} 재료가 주력
"""
        
        return report

def run_top_ingredients_analysis(show_plots=True, return_fig=False):
    """TOP 10 재료 분석을 실행하는 메인 함수 (GUI에서 호출)"""
    analyzer = TopIngredientsAnalyzer()
    
    # 데이터 로딩
    if not analyzer.load_data():
        return None
    
    # 분석 실행
    analyzer.extract_ingredients_from_menu()
    analyzer.calculate_actual_usage()
    
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
    print("TOP 10 재료 사용 분석을 시작합니다...")
    analyzer = run_top_ingredients_analysis()
    
    if analyzer:
        print("TOP 10 재료 분석이 완료되었습니다!")
        
        # 추가 인사이트
        top_usage, top_menu = analyzer.get_top_ingredients(5)
        if top_usage:
            top_ingredient = list(top_usage.keys())[0]
            top_count = list(top_usage.values())[0]
            print(f"\n핵심 발견사항:")
            print(f"• 가장 많이 사용된 재료: {top_ingredient} ({top_count}회)")
            print(f"• 재료 관리 우선순위: TOP 5 재료 집중 관리")
    else:
        print("ERROR: 분석 실행 중 오류가 발생했습니다.")
