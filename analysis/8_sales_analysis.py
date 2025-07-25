"""
8. 종합 매출 분석
K-tail 칵테일 바의 종합적인 매출 성과와 비즈니스 지표를 분석하고 시각화합니다.
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

class SalesAnalyzer:
    def __init__(self):
        self.orders_df = None
        self.cocktails_df = None
        self.cocktail_info = {}
        self.sales_metrics = {}
        self.performance_indicators = {}
        
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
            self.orders_df['date'] = self.orders_df['timestamp'].dt.date
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
            print(f"분석 기간: {self.orders_df['date'].min()} ~ {self.orders_df['date'].max()}")
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
            return '저가'
        elif price <= 15:
            return '중가'
        else:
            return '고가'
    
    def calculate_basic_metrics(self):
        """기본 매출 지표를 계산합니다."""
        total_orders = len(self.orders_df)
        total_quantity = self.orders_df['quantity'].sum()
        total_revenue = self.orders_df['total_price'].sum()
        unique_cocktails_sold = self.orders_df['cocktail_name'].nunique()
        unique_days = self.orders_df['date'].nunique()
        
        self.sales_metrics = {
            'total_orders': total_orders,
            'total_quantity': total_quantity,
            'total_revenue': total_revenue,
            'avg_order_value': total_revenue / total_orders if total_orders > 0 else 0,
            'avg_items_per_order': total_quantity / total_orders if total_orders > 0 else 0,
            'unique_cocktails_sold': unique_cocktails_sold,
            'avg_daily_revenue': total_revenue / unique_days if unique_days > 0 else 0,
            'avg_daily_orders': total_orders / unique_days if unique_days > 0 else 0,
            'avg_daily_quantity': total_quantity / unique_days if unique_days > 0 else 0,
            'operating_days': unique_days
        }
        
        return self.sales_metrics
    
    def analyze_sales_trends(self):
        """매출 트렌드를 분석합니다."""
        # 일별 매출 트렌드
        daily_sales = self.orders_df.groupby('date').agg({
            'total_price': 'sum',
            'quantity': 'sum',
            'cocktail_name': 'count'
        }).rename(columns={'cocktail_name': 'order_count'})
        
        # 요일별 매출
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_sales = self.orders_df.groupby('day_of_week').agg({
            'total_price': 'sum',
            'quantity': 'sum',
            'cocktail_name': 'count'
        }).rename(columns={'cocktail_name': 'order_count'})
        weekday_sales = weekday_sales.reindex(weekday_order, fill_value=0)
        
        # 시간대별 매출
        hourly_sales = self.orders_df.groupby('hour').agg({
            'total_price': 'sum',
            'quantity': 'sum',
            'cocktail_name': 'count'
        }).rename(columns={'cocktail_name': 'order_count'})
        
        # 월별 매출 (데이터가 여러 달에 걸쳐 있는 경우)
        monthly_sales = self.orders_df.groupby('month').agg({
            'total_price': 'sum',
            'quantity': 'sum',
            'cocktail_name': 'count'
        }).rename(columns={'cocktail_name': 'order_count'})
        
        return {
            'daily_sales': daily_sales,
            'weekday_sales': weekday_sales,
            'hourly_sales': hourly_sales,
            'monthly_sales': monthly_sales
        }
    
    def calculate_performance_indicators(self):
        """성과 지표를 계산합니다."""
        sales_trends = self.analyze_sales_trends()
        
        # 매출 성장률 (일별 데이터가 충분한 경우)
        daily_sales = sales_trends['daily_sales']
        if len(daily_sales) > 1:
            daily_sales['revenue_growth'] = daily_sales['total_price'].pct_change() * 100
            avg_growth_rate = daily_sales['revenue_growth'].mean()
        else:
            avg_growth_rate = 0
        
        # TOP 성과 지표
        top_cocktails_revenue = self.orders_df.groupby('cocktail_name')['total_price'].sum().nlargest(10)
        top_cocktails_quantity = self.orders_df.groupby('cocktail_name')['quantity'].sum().nlargest(10)
        
        # 가격대별 성과
        price_performance = self.orders_df.groupby('price_category').agg({
            'total_price': 'sum',
            'quantity': 'sum',
            'cocktail_name': 'count'
        }).rename(columns={'cocktail_name': 'order_count'})
        
        # 피크 타임 식별
        hourly_revenue = sales_trends['hourly_sales']['total_price']
        peak_hours = hourly_revenue.nlargest(3).index.tolist()
        
        # 최고 성과일
        if len(daily_sales) > 1:
            best_day = daily_sales['total_price'].idxmax()
            best_day_revenue = daily_sales['total_price'].max()
        else:
            best_day = daily_sales.index[0]
            best_day_revenue = daily_sales['total_price'].iloc[0]
        
        self.performance_indicators = {
            'avg_growth_rate': avg_growth_rate,
            'top_cocktails_revenue': top_cocktails_revenue,
            'top_cocktails_quantity': top_cocktails_quantity,
            'price_performance': price_performance,
            'peak_hours': peak_hours,
            'best_day': best_day,
            'best_day_revenue': best_day_revenue,
            'revenue_volatility': daily_sales['total_price'].std() if len(daily_sales) > 1 else 0,
            'sales_trends': sales_trends
        }
        
        return self.performance_indicators
    
    def analyze_customer_behavior(self):
        """고객 행동 패턴을 분석합니다."""
        # 주문 크기 분포
        order_sizes = self.orders_df['quantity'].value_counts().sort_index()
        
        # 가격 선호도
        price_distribution = self.orders_df['unit_price'].describe()
        
        # 시간대별 고객 패턴
        hourly_customer_behavior = self.orders_df.groupby('hour').agg({
            'quantity': ['mean', 'std'],
            'total_price': ['mean', 'std'],
            'cocktail_name': 'count'
        })
        
        return {
            'order_sizes': order_sizes,
            'price_distribution': price_distribution,
            'hourly_behavior': hourly_customer_behavior
        }
    
    def create_visualizations(self, show_plots=True):
        """종합 매출 분석 시각화를 생성합니다."""
        if not self.sales_metrics:
            self.calculate_basic_metrics()
            self.calculate_performance_indicators()
        
        customer_behavior = self.analyze_customer_behavior()
        sales_trends = self.performance_indicators['sales_trends']
        
        fig, axes = plt.subplots(3, 3, figsize=(20, 18))
        fig.suptitle('K-tail 종합 매출 분석 대시보드', fontsize=18, fontweight='bold')
        
        # 1. 일별 매출 트렌드
        daily_sales = sales_trends['daily_sales']
        if len(daily_sales) > 1:
            # 날짜를 문자열로 변환하여 x축에 표시
            date_labels = [str(date) for date in daily_sales.index]
            x_positions = range(len(daily_sales))
            
            axes[0,0].plot(x_positions, daily_sales['total_price'], 
                          marker='o', linewidth=3, markersize=6, color='green')
            axes[0,0].fill_between(x_positions, daily_sales['total_price'], 
                                  alpha=0.3, color='green')
            
            # x축 라벨 설정 (최대 10개만 표시)
            if len(date_labels) <= 10:
                axes[0,0].set_xticks(x_positions)
                axes[0,0].set_xticklabels(date_labels, rotation=45, ha='right')
            else:
                # 너무 많으면 일부만 표시
                step = len(date_labels) // 8
                tick_positions = x_positions[::step]
                tick_labels = date_labels[::step]
                axes[0,0].set_xticks(tick_positions)
                axes[0,0].set_xticklabels(tick_labels, rotation=45, ha='right')
        else:
            axes[0,0].bar(['Today'], [daily_sales['total_price'].iloc[0]], color='green')
        
        axes[0,0].set_title('일별 매출 트렌드', fontweight='bold')
        axes[0,0].set_ylabel('매출 ($)')
        axes[0,0].grid(True, alpha=0.3)
        
        # 2. 요일별 매출
        weekday_sales = sales_trends['weekday_sales']
        korean_weekdays = ['월', '화', '수', '목', '금', '토', '일']
        
        bars = axes[0,1].bar(range(len(weekday_sales)), weekday_sales['total_price'], 
                            color='lightblue', alpha=0.8)
        axes[0,1].set_xticks(range(len(weekday_sales)))
        axes[0,1].set_xticklabels(korean_weekdays)
        axes[0,1].set_title('요일별 매출', fontweight='bold')
        axes[0,1].set_ylabel('매출 ($)')
        
        # 최고 매출 요일 강조
        max_idx = weekday_sales['total_price'].argmax()
        bars[max_idx].set_color('red')
        bars[max_idx].set_alpha(1.0)
        
        # 3. 시간대별 매출 (피크타임 강조)
        hourly_sales = sales_trends['hourly_sales']
        peak_hours = self.performance_indicators['peak_hours']
        
        colors = ['red' if h in peak_hours else 'orange' for h in hourly_sales.index]
        axes[0,2].bar(hourly_sales.index, hourly_sales['total_price'], 
                     color=colors, alpha=0.8)
        axes[0,2].set_title('시간대별 매출 (피크타임 강조)', fontweight='bold')
        axes[0,2].set_xlabel('시간')
        axes[0,2].set_ylabel('매출 ($)')
        axes[0,2].grid(True, alpha=0.3)
        
        # 4. TOP 10 매출 기여 칵테일
        top_revenue = self.performance_indicators['top_cocktails_revenue'][:10]
        y_pos = range(len(top_revenue))
        
        bars = axes[1,0].barh(y_pos, top_revenue.values, color='gold', alpha=0.8)
        axes[1,0].set_yticks(y_pos)
        axes[1,0].set_yticklabels([name[:15] + '...' if len(name) > 15 else name 
                                  for name in top_revenue.index])
        axes[1,0].set_title('TOP 10 매출 기여 칵테일', fontweight='bold')
        axes[1,0].set_xlabel('매출 ($)')
        axes[1,0].invert_yaxis()
        
        # 5. 가격대별 매출 기여도
        price_performance = self.performance_indicators['price_performance']
        
        wedges, texts, autotexts = axes[1,1].pie(price_performance['total_price'], 
                                                labels=price_performance.index,
                                                autopct='%1.1f%%', 
                                                colors=['lightgreen', 'orange', 'lightcoral'],
                                                startangle=90)
        axes[1,1].set_title('가격대별 매출 기여도', fontweight='bold')
        
        # 6. 월별 매출 (데이터가 여러 달에 걸쳐 있는 경우)
        monthly_sales = sales_trends['monthly_sales']
        if len(monthly_sales) > 1:
            month_names = ['1월', '2월', '3월', '4월', '5월', '6월', 
                          '7월', '8월', '9월', '10월', '11월', '12월']
            month_labels = [month_names[m-1] for m in monthly_sales.index]
            axes[1,2].bar(month_labels, monthly_sales['total_price'], 
                         color='lightgreen', alpha=0.8)
        else:
            current_month = monthly_sales.index[0]
            month_name = ['1월', '2월', '3월', '4월', '5월', '6월', 
                         '7월', '8월', '9월', '10월', '11월', '12월'][current_month-1]
            axes[1,2].bar([month_name], [monthly_sales['total_price'].iloc[0]], 
                         color='lightgreen')
        
        axes[1,2].set_title('월별 매출', fontweight='bold')
        axes[1,2].set_ylabel('매출 ($)')
        axes[1,2].tick_params(axis='x', rotation=0)
        
        # 7. 주문 크기 분포
        order_sizes = customer_behavior['order_sizes']
        axes[2,0].bar(order_sizes.index, order_sizes.values, 
                     color='lightcyan', alpha=0.8, edgecolor='black')
        axes[2,0].set_title('주문 크기 분포', fontweight='bold')
        axes[2,0].set_xlabel('주문량 (잔)')
        axes[2,0].set_ylabel('주문 횟수')
        axes[2,0].grid(True, alpha=0.3)
        
        # 8. 매출 vs 판매량 상관관계
        cocktail_metrics = self.orders_df.groupby('cocktail_name').agg({
            'total_price': 'sum',
            'quantity': 'sum'
        })
        
        axes[2,1].scatter(cocktail_metrics['quantity'], cocktail_metrics['total_price'], 
                         alpha=0.6, color='purple', s=50)
        axes[2,1].set_title('칵테일별 판매량 vs 매출', fontweight='bold')
        axes[2,1].set_xlabel('총 판매량')
        axes[2,1].set_ylabel('총 매출 ($)')
        axes[2,1].grid(True, alpha=0.3)
        
        # 추세선 추가
        if len(cocktail_metrics) > 1:
            z = np.polyfit(cocktail_metrics['quantity'], cocktail_metrics['total_price'], 1)
            p = np.poly1d(z)
            axes[2,1].plot(cocktail_metrics['quantity'], p(cocktail_metrics['quantity']), 
                          "r--", alpha=0.8, linewidth=2)
        
        # 9. 성과 지표 요약 (텍스트)
        axes[2,2].axis('off')
         
        kpi_text = f"""KPI 요약

총매출: ${self.sales_metrics['total_revenue']:,.0f}
주문건수: {self.sales_metrics['total_orders']:,}건
판매량: {self.sales_metrics['total_quantity']:,}잔

평균주문: ${self.sales_metrics['avg_order_value']:.1f}
주문당: {self.sales_metrics['avg_items_per_order']:.1f}잔

일평균매출: ${self.sales_metrics['avg_daily_revenue']:,.0f}
일평균주문: {self.sales_metrics['avg_daily_orders']:.1f}건

운영일: {self.sales_metrics['operating_days']}일
메뉴: {self.sales_metrics['unique_cocktails_sold']}개

피크: {', '.join([f'{h}시' for h in self.performance_indicators['peak_hours']])}

변동성: ${self.performance_indicators['revenue_volatility']:.0f}"""
        
        axes[2,2].text(0.01, 0.99, kpi_text, transform=axes[2,2].transAxes, 
                      fontsize=8, verticalalignment='top', horizontalalignment='left',
                      bbox=dict(boxstyle="round,pad=0.1", facecolor="lightgray", alpha=0.8))
        
        plt.tight_layout(pad=4.0)
        plt.subplots_adjust(hspace=0.6, wspace=0.5, top=0.92, bottom=0.08)
        
        if show_plots:
            plt.show()
        
        return fig
    
    def generate_report(self):
        """종합 매출 분석 리포트를 생성합니다."""
        if not self.sales_metrics:
            self.calculate_basic_metrics()
            self.calculate_performance_indicators()
        
        sales_trends = self.performance_indicators['sales_trends']
        customer_behavior = self.analyze_customer_behavior()
        
        report = f"""
K-tail 종합 매출 분석 리포트
{'='*50}

핵심 매출 지표:
• 총 매출: ${self.sales_metrics['total_revenue']:,.2f}
• 총 주문 건수: {self.sales_metrics['total_orders']:,}건
• 총 판매량: {self.sales_metrics['total_quantity']:,}잔
• 평균 주문 금액 (AOV): ${self.sales_metrics['avg_order_value']:.2f}
• 주문당 평균 아이템 수: {self.sales_metrics['avg_items_per_order']:.1f}잔
• 판매된 칵테일 종류: {self.sales_metrics['unique_cocktails_sold']}개

운영 성과:
• 운영 일수: {self.sales_metrics['operating_days']}일
• 일평균 매출: ${self.sales_metrics['avg_daily_revenue']:,.2f}
• 일평균 주문: {self.sales_metrics['avg_daily_orders']:.1f}건
• 일평균 판매량: {self.sales_metrics['avg_daily_quantity']:.1f}잔
"""
        
        # 성장률 (데이터가 충분한 경우)
        if self.performance_indicators['avg_growth_rate'] != 0:
            growth_trend = "증가" if self.performance_indicators['avg_growth_rate'] > 0 else "감소"
            report += f"• 일평균 매출 성장률: {self.performance_indicators['avg_growth_rate']:.1f}% ({growth_trend})\n"
        
        # 요일별 성과
        weekday_sales = sales_trends['weekday_sales']
        best_weekday = weekday_sales['total_price'].idxmax()
        worst_weekday = weekday_sales['total_price'].idxmin()
        
        weekday_korean = {
            'Monday': '월요일', 'Tuesday': '화요일', 'Wednesday': '수요일', 
            'Thursday': '목요일', 'Friday': '금요일', 'Saturday': '토요일', 'Sunday': '일요일'
        }
        
        report += f"""
요일별 매출 현황:
• 최고 매출 요일: {weekday_korean.get(best_weekday, best_weekday)} (${weekday_sales.loc[best_weekday, 'total_price']:,.2f})
• 최저 매출 요일: {weekday_korean.get(worst_weekday, worst_weekday)} (${weekday_sales.loc[worst_weekday, 'total_price']:,.2f})
"""
        
        # TOP 성과 칵테일
        top_revenue = self.performance_indicators['top_cocktails_revenue']
        top_quantity = self.performance_indicators['top_cocktails_quantity']
        
        report += f"\nTOP 5 매출 기여 칵테일:\n"
        for i, (cocktail, revenue) in enumerate(list(top_revenue.items())[:5], 1):
            contribution = (revenue / self.sales_metrics['total_revenue']) * 100
            report += f"{i}. {cocktail}: ${revenue:,.2f} ({contribution:.1f}%)\n"
        
        report += f"\nTOP 5 판매량 칵테일:\n"
        for i, (cocktail, quantity) in enumerate(list(top_quantity.items())[:5], 1):
            contribution = (quantity / self.sales_metrics['total_quantity']) * 100
            report += f"{i}. {cocktail}: {quantity}잔 ({contribution:.1f}%)\n"
        
        # 가격대별 성과
        price_performance = self.performance_indicators['price_performance']
        report += f"\n가격대별 성과:\n"
        
        for category, stats in price_performance.iterrows():
            revenue_pct = (stats['total_price'] / self.sales_metrics['total_revenue']) * 100
            quantity_pct = (stats['quantity'] / self.sales_metrics['total_quantity']) * 100
            report += f"• {category}: 매출 {revenue_pct:.1f}%, 판매량 {quantity_pct:.1f}%\n"
        
        # 피크 타임 분석
        peak_hours = self.performance_indicators['peak_hours']
        hourly_revenue = sales_trends['hourly_sales']['total_price']
        peak_revenue = sum(hourly_revenue[hour] for hour in peak_hours)
        peak_contribution = (peak_revenue / self.sales_metrics['total_revenue']) * 100
        
        report += f"""
피크 타임 성과:
• 피크 시간대: {', '.join([f'{h}시' for h in peak_hours])}
• 피크 타임 매출: ${peak_revenue:,.2f} ({peak_contribution:.1f}%)
• 최고 매출 시간: {hourly_revenue.idxmax()}시 (${hourly_revenue.max():,.2f})
"""
        
        # 고객 행동 인사이트
        avg_order_size = customer_behavior['order_sizes'].index.to_series().multiply(
            customer_behavior['order_sizes'].values
        ).sum() / customer_behavior['order_sizes'].sum()
        
        most_common_order = customer_behavior['order_sizes'].idxmax()
        
        report += f"""
고객 행동 분석:
• 평균 주문 크기: {avg_order_size:.1f}잔
• 가장 일반적인 주문: {most_common_order}잔
• 평균 칵테일 가격: ${customer_behavior['price_distribution']['mean']:.2f}
• 가격 범위: ${customer_behavior['price_distribution']['min']:.2f} ~ ${customer_behavior['price_distribution']['max']:.2f}
"""
        
        # 비즈니스 인사이트 및 추천사항
        revenue_volatility = self.performance_indicators['revenue_volatility']
        
        report += f"""
핵심 비즈니스 인사이트:
• 매출 안정성: {'높음' if revenue_volatility < 100 else '보통' if revenue_volatility < 200 else '낮음'} (변동성: ${revenue_volatility:.2f})
• 운영 효율성: 피크타임({', '.join([f'{h}시' for h in peak_hours])})에 매출 집중
• 메뉴 다양성: {self.sales_metrics['unique_cocktails_sold']}개 메뉴 중 TOP 5가 주요 매출원
• 가격 전략: {price_performance['total_price'].idxmax()} 가격대가 매출 주도

추천 전략:
• 피크타임 최적화: {', '.join([f'{h}시' for h in peak_hours])} 인력 집중 배치
• 메뉴 집중화: TOP 5 칵테일 프로모션 및 개선
• 비피크타임 활성화: {worst_weekday} 특별 할인 이벤트
• 신메뉴 개발: 성공 메뉴 패턴 분석 기반 신제품 출시
• 가격 최적화: {price_performance['total_price'].idxmax()} 가격대 메뉴 확대
"""
        
        return report

def run_sales_analysis(show_plots=True, return_fig=False):
    """종합 매출 분석을 실행하는 메인 함수 (GUI에서 호출)"""
    analyzer = SalesAnalyzer()
    
    # 데이터 로딩
    if not analyzer.load_data():
        return None
    
    # 분석 실행
    analyzer.calculate_basic_metrics()
    analyzer.calculate_performance_indicators()
    
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
    print("종합 매출 분석을 시작합니다...")
    analyzer = run_sales_analysis()
    
    if analyzer:
        print("종합 매출 분석이 완료되었습니다!")
        
        # 추가 인사이트
        print(f"\n핵심 발견사항:")
        print(f"• 총 매출: ${analyzer.sales_metrics['total_revenue']:,.2f}")
        print(f"• 평균 주문 금액: ${analyzer.sales_metrics['avg_order_value']:.2f}")
        print(f"• 피크 타임: {', '.join([f'{h}시' for h in analyzer.performance_indicators['peak_hours']])}")
        print(f"• 운영 최적화 포인트 식별됨")
    else:
        print("ERROR: 분석 실행 중 오류가 발생했습니다.")
