"""
Analysis 모듈을 위한 공통 유틸리티 함수들
"""

import os
import pandas as pd

def get_data_path(filename):
    """
    프로젝트 루트에서 데이터 파일의 절대 경로를 반환합니다.
    analysis 폴더에서 실행될 때 상위 폴더의 data 디렉토리를 찾습니다.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)  # analysis 폴더의 상위 폴더
    return os.path.join(project_root, 'data', filename)

def check_data_files():
    """필요한 데이터 파일들이 존재하는지 확인합니다."""
    orders_path = get_data_path('orders.csv')
    cocktails_path = get_data_path('cocktails.csv')
    
    if not os.path.exists(orders_path):
        print(f"ERROR: {orders_path} 파일을 찾을 수 없습니다.")
        return False
    
    if not os.path.exists(cocktails_path):
        print(f"ERROR: {cocktails_path} 파일을 찾을 수 없습니다.")
        return False
    
    return True

def load_orders_data(file_path=None):
    """
    주문 데이터를 로딩합니다.
    새로운 형식의 주문 요구사항을 제외하고 데이터를 파싱합니다.
    """
    if file_path is None:
        file_path = get_data_path('orders.csv')
    
    try:
        orders = []
        with open(file_path, 'r', encoding='utf-8') as f:
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
                    
                    # 다음 줄들을 확인하여 주문 요구사항이 있는지 체크
                    # 재료 리스트를 건너뛰고 주문 요구사항도 건너뛰기
                    i += 1
                    while i < len(lines):
                        next_line = lines[i].strip()
                        if next_line.startswith('--'):
                            # 재료 라인 건너뛰기
                            i += 1
                        elif next_line and not next_line.startswith('--') and ',' in next_line and len(next_line.split(',')) >= 3:
                            # 다음 주문 라인이면 루프를 빠져나가기
                            break
                        elif next_line:
                            # 주문 요구사항 라인 건너뛰기
                            i += 1
                        else:
                            # 빈 라인 건너뛰기
                            i += 1
                    continue
            i += 1
        
        return pd.DataFrame(orders)
    except FileNotFoundError:
        print(f"ERROR: {file_path} 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"ERROR: 데이터 로딩 실패: {e}")
        return None

def load_cocktails_data(file_path=None):
    """칵테일 메뉴 데이터를 로딩합니다."""
    if file_path is None:
        file_path = get_data_path('cocktails.csv')
    
    try:
        return pd.read_csv(file_path).drop_duplicates(subset=['Cocktail Name'])
    except FileNotFoundError:
        print(f"ERROR: {file_path} 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"ERROR: 칵테일 데이터 로딩 실패: {e}")
        return None

# GUI에서 사용할 수 있는 분석 함수들의 매핑
ANALYSIS_FUNCTIONS = {
    '시간대별 판매량 트렌드': '1_hourly_sales_trend.run_hourly_sales_analysis',
    '인기 칵테일 분석': '2_popular_cocktails.run_popular_cocktails_analysis',
    '피크 타임 분석': '3_peak_time_analysis.run_peak_time_analysis',
    '최다 사용 재료 TOP 10': '4_top_ingredients.run_top_ingredients_analysis',
    '재료별 사용 빈도': '5_ingredient_frequency.run_ingredient_frequency_analysis',
    '계절별 재료 트렌드': '6_seasonal_trends.run_seasonal_ingredient_analysis',
    '가격대별 선호도': '7_price_preferences.run_price_preference_analysis',
    '종합 매출 분석': '8_sales_analysis.run_sales_analysis'
}
