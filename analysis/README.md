# K-tail 칵테일 바 분석 모듈

이 폴더에는 K-tail 칵테일 바의 판매 데이터를 분석하기 위한 **8개의 독립적인 분석 스크립트**가 포함되어 있습니다.
각 스크립트는 GUI에서 체크박스로 선택하여 실행할 수 있으며, 독립적으로도 실행 가능합니다.

## 분석 스크립트 목록

### 1 시간대별 판매량 트렌드 분석 (`1_hourly_sales_trend.py`)
- **목적**: 시간대별 판매 패턴과 트렌드를 분석
- **생성 그래프**: 5개 (시간대별 판매량, 누적 판매량, 피크타임 강조, 주문 분포, 효율성)
- **주요 기능**:
  - 시간대별 총 판매량 분석
  - 피크 타임 식별 (상위 25% 기준)
  - 주문 건수 및 평균 주문 크기 분석
  - 운영 최적화 제안

### 2 인기 칵테일 분석 (`2_popular_cocktails.py`)
- **목적**: 가장 인기 있는 칵테일과 성과 분석
- **생성 그래프**: 6개 (TOP 10 판매량, TOP 10 매출, 파레토, 성과 지표, 분포, 집중도)
- **주요 기능**:
  - 판매량 기준 TOP 10 칵테일
  - 매출 기준 TOP 10 칵테일
  - 파레토 분석 (80-20 법칙)
  - 칵테일별 성과 지표

### 3 피크 타임 분석 (`3_peak_time_analysis.py`)
- **목적**: 매출이 집중되는 피크 시간대 분석
- **생성 그래프**: 6개 (매출 트렌드, 피크타임 강조, 비교 분석, 효율성, 분포, 집중도)
- **주요 기능**:
  - 피크 시간대 식별 및 강조
  - 시간대별 효율성 분석
  - 피크타임 vs 비피크타임 비교
  - 인력 배치 최적화 제안

### 4 최다 사용 재료 TOP 10 (`4_top_ingredients.py`)
- **목적**: 가장 많이 사용되는 재료들 분석
- **생성 그래프**: 4개 (사용량 TOP 10, 빈도 TOP 10, 카테고리 분포, 비교 분석)
- **주요 기능**:
  - 실제 사용량 기준 TOP 10 재료
  - 메뉴 포함 빈도 기준 TOP 10 재료
  - 재료 카테고리별 분포
  - 재료 관리 최적화 제안

### 5 재료별 사용 빈도 (`5_ingredient_frequency.py`)
- **목적**: 재료의 사용 빈도와 분포 분석
- **생성 그래프**: 6개 (빈도 분포, 박스플롯, 파레토, 집중도, 카테고리, 통계)
- **주요 기능**:
  - 사용 빈도 분포 히스토그램
  - 박스플롯을 통한 이상치 분석
  - 파레토 차트 (집중도 분석)
  - 지니계수 및 허핀달 지수

### 6 계절별 재료 트렌드 (`6_seasonal_trends.py`)
- **목적**: 계절에 따른 재료 사용 패턴 분석
- **생성 그래프**: 6개 (계절별 사용량, 히트맵, 트렌드, 인기 재료, 계절성, 패턴)
- **주요 기능**:
  - 계절별 재료 사용량 히트맵
  - 계절별 특화 재료 식별
  - 재료별 계절성 지수
  - 월별 재료 다양성 트렌드

### 7 가격대별 선호도 (`7_price_preferences.py`)
- **목적**: 고객의 가격대별 선호도 분석
- **생성 그래프**: 6개 (가격대별 분포, 시간대별 선호도, 계절별 선호도, 민감도, 탄력성, 트렌드)
- **주요 기능**:
  - 가격대별 판매량 및 매출
  - 시간대별/계절별 가격 선호도
  - 가격 민감도 분석
  - 가격 탄력성 지표

### 8 종합 매출 분석 (`8_sales_analysis.py`)
- **목적**: 전체적인 매출 성과와 지표 분석
- **생성 그래프**: 8개 + KPI 요약 (일별 트렌드, 요일별 매출, 시간대별 매출, TOP 10 칵테일, 가격대별 기여도, 월별 매출, 주문 크기, 상관관계)
- **주요 기능**:
  - 핵심 매출 지표 (KPI) 대시보드
  - 일별/요일별/월별 매출 트렌드
  - TOP 10 매출 기여 칵테일
  - 비즈니스 인사이트 및 추천사항

---

## 🔧 사용 방법

### 1. 독립 실행
각 스크립트는 독립적으로 실행할 수 있습니다:
```bash
cd /path/to/k-tail/analysis
python 1_hourly_sales_trend.py
```

### 2. GUI에서 호출
각 스크립트는 GUI에서 호출할 수 있는 함수를 제공합니다:

```python
# 예시: 시간대별 분석
from analysis.hourly_sales_trend import run_hourly_sales_analysis

# 그래프 표시하고 결과 반환
result = run_hourly_sales_analysis(show_plots=True, return_fig=False)

# 그래프 숨기고 Figure 객체 반환 (GUI 임베딩용)
fig = run_hourly_sales_analysis(show_plots=False, return_fig=True)
```

### 3. 모든 함수 목록
- `run_hourly_sales_analysis()` - 1번 스크립트
- `run_popular_cocktails_analysis()` - 2번 스크립트
- `run_peak_time_analysis()` - 3번 스크립트
- `run_ingredient_analysis()` - 4번 스크립트
- `run_ingredient_frequency_analysis()` - 5번 스크립트
- `run_seasonal_trends_analysis()` - 6번 스크립트
- `run_price_preferences_analysis()` - 7번 스크립트
- `run_sales_analysis()` - 8번 스크립트

---

## 📁 폴더 구조

```
analysis/
├── __init__.py                    # 패키지 초기화
├── utils.py                       # 공통 유틸리티 함수
├── README.md                      # 이 파일
├── 1_hourly_sales_trend.py        # 시간대별 분석
├── 2_popular_cocktails.py         # 인기 칵테일 분석
├── 3_peak_time_analysis.py        # 피크 타임 분석
├── 4_top_ingredients.py           # 최다 사용 재료
├── 5_ingredient_frequency.py      # 재료 사용 빈도
├── 6_seasonal_trends.py           # 계절별 트렌드
├── 7_price_preferences.py         # 가격대별 선호도
└── 8_sales_analysis.py            # 종합 매출 분석
```

---

## 📊 총 생성 그래프 수

| 스크립트 | 그래프 수 | 유형 |
|---------|----------|------|
| 1번 | 5개 | 선 그래프, 막대 그래프, 박스플롯 |
| 2번 | 6개 | 막대 그래프, 파이차트, 산점도 |
| 3번 | 6개 | 선 그래프, 막대 그래프, 히트맵 |
| 4번 | 4개 | 막대 그래프, 파이차트 |
| 5번 | 6개 | 히스토그램, 박스플롯, 파레토 차트 |
| 6번 | 6개 | 히트맵, 선 그래프, 막대 그래프 |
| 7번 | 6개 | 막대 그래프, 히트맵, 선 그래프 |
| 8번 | 9개 | 종합 대시보드 (8개 그래프 + KPI) |
| **총합** | **48개** | **다양한 시각화 유형** |

---

## 🚀 특징

- **모듈화**: 각 분석이 독립적으로 실행 가능
- **GUI 연동**: 체크박스 선택으로 원하는 분석만 실행
- **전문적 출력**: 이모티콘 없는 깔끔한 비즈니스 리포트
- **최적화된 레이아웃**: 그래프 겹침 없는 깔끔한 시각화
- **한글 지원**: 완전한 한글 폰트 지원
- **실시간 분석**: 최신 데이터를 반영한 동적 분석

### 3. 통합 컨트롤러 사용
```python
from analysis import AnalysisController

controller = AnalysisController()

# 사용 가능한 분석 목록
analyses = controller.get_available_analyses()

# 특정 분석 실행
result = controller.run_analysis('시간대별 판매량 트렌드')

# 여러 분석 실행
results = controller.run_multiple_analyses([
    '시간대별 판매량 트렌드',
    '인기 칵테일 분석'
])
```

## 데이터 요구사항

### 필수 데이터 파일
- `data/orders.csv`: 주문 이력 데이터
- `data/cocktails.csv`: 칵테일 메뉴 정보

### orders.csv 형식
```
timestamp,cocktail_name,quantity
2024-01-01 18:30:00,Old Fashioned,2
2024-01-01 19:15:00,Margarita,1
```

### cocktails.csv 형식
```
name,price,ingredients
Old Fashioned,$12.00,"Bourbon, Sugar, Bitters, Orange twist"
Margarita,$10.00,"Tequila, Lime juice, Triple sec, Salt rim"
```

## 출력 결과

각 분석 스크립트는 다음을 생성합니다:
1. **콘솔 리포트**: 상세한 분석 결과와 비즈니스 인사이트
2. **시각화**: matplotlib을 사용한 차트와 그래프
3. **데이터 반환**: Python 객체로 분석 결과 반환

## GUI 통합 가이드

### 체크박스 기반 분석 선택
```python
# GUI에서 선택된 분석들 실행
selected_analyses = [
    '시간대별 판매량 트렌드',
    '인기 칵테일 분석',
    '피크 타임 분석'
]

controller = AnalysisController()
for analysis in selected_analyses:
    fig = controller.run_analysis(analysis, show_plots=False, return_fig=True)
    # GUI에 fig 임베딩
```

### 에러 처리
모든 분석 함수는 에러 처리를 포함하고 있으며, 데이터 파일이 없거나 손상된 경우 적절한 에러 메시지를 반환합니다.

## 요구사항

- Python 3.7+
- pandas
- matplotlib
- seaborn
- numpy
- scipy (일부 분석용)

## 확장성

새로운 분석을 추가하려면:
1. 새 파일 생성 (예: `9_new_analysis.py`)
2. `run_new_analysis(show_plots=True, return_fig=False)` 함수 구현
3. `__init__.py`의 `AnalysisController`에 추가

## 주의사항

- 모든 경로는 프로젝트 루트 기준으로 설정되어 있습니다
- 폰트 관련 경고는 한글 표시와 관련된 것으로 분석에는 영향을 주지 않습니다
- GUI에서 사용할 때는 `show_plots=False, return_fig=True`로 설정하여 Figure 객체를 받아 임베딩하세요
