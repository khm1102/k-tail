"""
Analysis Module Main Controller
GUI에서 각 분석 모듈을 호출하기 위한 통합 컨트롤러입니다.
"""

import sys
import os
import importlib

# 현재 디렉토리를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

class AnalysisController:
    """분석 모듈들을 관리하는 컨트롤러 클래스"""
    
    def __init__(self):
        self.analysis_modules = {
            '시간대별 판매량 트렌드': {
                'module': '1_hourly_sales_trend',
                'function': 'run_hourly_sales_analysis',
                'description': '시간대별 판매 패턴과 트렌드를 분석합니다.'
            },
            '인기 칵테일 분석': {
                'module': '2_popular_cocktails',
                'function': 'run_popular_cocktails_analysis',
                'description': '가장 인기 있는 칵테일과 성과를 분석합니다.'
            },
            '피크 타임 분석': {
                'module': '3_peak_time_analysis',
                'function': 'run_peak_time_analysis',
                'description': '매출이 집중되는 피크 시간대를 분석합니다.'
            },
            '최다 사용 재료 TOP 10': {
                'module': '4_top_ingredients',
                'function': 'run_top_ingredients_analysis',
                'description': '가장 많이 사용되는 재료들을 분석합니다.'
            },
            '재료별 사용 빈도': {
                'module': '5_ingredient_frequency',
                'function': 'run_ingredient_frequency_analysis',
                'description': '재료의 사용 빈도와 분포를 분석합니다.'
            },
            '계절별 재료 트렌드': {
                'module': '6_seasonal_trends',
                'function': 'run_seasonal_ingredient_analysis',
                'description': '계절에 따른 재료 사용 패턴을 분석합니다.'
            },
            '가격대별 선호도': {
                'module': '7_price_preferences',
                'function': 'run_price_preference_analysis',
                'description': '고객의 가격대별 선호도를 분석합니다.'
            },
            '종합 매출 분석': {
                'module': '8_sales_analysis',
                'function': 'run_sales_analysis',
                'description': '전체적인 매출 성과와 지표를 분석합니다.'
            }
        }
    
    def get_available_analyses(self):
        """사용 가능한 분석 목록을 반환합니다."""
        return list(self.analysis_modules.keys())
    
    def get_analysis_description(self, analysis_name):
        """특정 분석의 설명을 반환합니다."""
        return self.analysis_modules.get(analysis_name, {}).get('description', '설명 없음')
    
    def _import_analysis_function(self, analysis_name):
        """분석 함수를 동적으로 임포트합니다."""
        if analysis_name not in self.analysis_modules:
            return None
        
        module_info = self.analysis_modules[analysis_name]
        module_name = module_info['module']
        function_name = module_info['function']
        
        try:
            # 동적으로 모듈 임포트
            module = importlib.import_module(module_name)
            return getattr(module, function_name)
        except (ImportError, AttributeError) as e:
            print(f"ERROR: 모듈 {module_name} 임포트 실패: {e}")
            return None
    
    def run_analysis(self, analysis_name, show_plots=True, return_fig=False):
        """
        지정된 분석을 실행합니다.
        
        Args:
            analysis_name (str): 실행할 분석 이름
            show_plots (bool): 그래프를 화면에 표시할지 여부
            return_fig (bool): Figure 객체를 반환할지 여부
        
        Returns:
            분석 결과 또는 Figure 객체
        """
        if analysis_name not in self.analysis_modules:
            print(f"ERROR: 알 수 없는 분석: {analysis_name}")
            print(f"사용 가능한 분석: {', '.join(self.get_available_analyses())}")
            return None
        
        try:
            analysis_func = self._import_analysis_function(analysis_name)
            if analysis_func is None:
                return None
            
            print(f"{analysis_name} 분석을 시작합니다...")
            
            result = analysis_func(show_plots=show_plots, return_fig=return_fig)
            
            if result is not None:
                print(f"{analysis_name} 분석이 완료되었습니다!")
            else:
                print(f"ERROR: {analysis_name} 분석 중 오류가 발생했습니다.")
            
            return result
            
        except Exception as e:
            print(f"ERROR: {analysis_name} 분석 실행 중 오류: {e}")
            return None
    
    def run_multiple_analyses(self, analysis_names, show_plots=True, return_figs=False):
        """
        여러 분석을 순차적으로 실행합니다.
        
        Args:
            analysis_names (list): 실행할 분석 이름들의 리스트
            show_plots (bool): 그래프를 화면에 표시할지 여부
            return_figs (bool): Figure 객체들을 반환할지 여부
        
        Returns:
            분석 결과들의 딕셔너리
        """
        results = {}
        
        for analysis_name in analysis_names:
            result = self.run_analysis(analysis_name, show_plots=show_plots, return_fig=return_figs)
            results[analysis_name] = result
            print(f"{'='*50}")
        
        return results
    
    def run_all_analyses(self, show_plots=True, return_figs=False):
        """모든 분석을 실행합니다."""
        print("모든 분석을 실행합니다...")
        print(f"{'='*50}")
        
        all_analyses = self.get_available_analyses()
        return self.run_multiple_analyses(all_analyses, show_plots=show_plots, return_figs=return_figs)

def main():
    """메인 함수 - 테스트용"""
    controller = AnalysisController()
    
    print("K-tail 칵테일 바 분석 시스템")
    print("="*50)
    
    # 사용 가능한 분석 목록 표시
    analyses = controller.get_available_analyses()
    print("사용 가능한 분석:")
    for i, analysis in enumerate(analyses, 1):
        description = controller.get_analysis_description(analysis)
        print(f"{i}. {analysis}: {description}")
    
    print("\n모든 분석을 실행하시겠습니까? (y/n): ", end="")
    choice = input().lower()
    
    if choice == 'y':
        controller.run_all_analyses()
    else:
        print("특정 분석을 실행하려면 해당 .py 파일을 직접 실행하세요.")

if __name__ == "__main__":
    main()
