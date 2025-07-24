"""
칵테일 추천 서비스 (DB 기반)
사용자의 입력(칵테일 이름 또는 맛/재료)을 기반으로 칵테일을 추천하는 서비스
"""

import re
import sqlite3
import sys
import os
from os import remove
from typing import List, Dict, Tuple
from difflib import SequenceMatcher

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.db.conn import db_connect
from src.db.cocktail import cocktail_select, coctail_insert, cockail_create


class CocktailService:
    def __init__(self):
        """
        칵테일 서비스 초기화 (DB 기반)
        """
        self.conn = db_connect()
        self.cursor = self.conn.cursor()
        cockail_create()  # 이미 정의된 테이블 생성 함수 사용

    def get_all_cocktails(self) -> List[Dict]:
        """모든 칵테일을 반환합니다."""
        rows = cocktail_select()  # 이미 정의된 함수 사용

        cocktails = []
        for row in rows:
            cocktail = {
                'name': row[0],
                'ingredients': row[1],
                'garnish': row[2] if row[2] else 'N/A',
                'glassware': row[3] if row[3] else 'N/A',
                'preparation': row[4] if row[4] else 'N/A',
                'price': f"${row[5]:.2f}" if row[5] else 'N/A',
                'note': row[6] if row[6] else 'N/A'
            }
            cocktails.append(cocktail)

        return cocktails

    def _clean_ingredients(self, ingredients: str) -> str:
        """재료 문자열을 정리합니다."""
        if not ingredients:
            return ""

        # 불필요한 기호와 수량 제거, 소문자 변환
        cleaned = re.sub(r'\d+\.?\d*\s*(oz|ml|dash|drops?|cup|tsp|tbsp)', '', ingredients.lower())
        cleaned = re.sub(r'[,\n\r\*\-\+\(\)]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def find_cocktail_by_name(self, name: str) -> Dict:
        """칵테일 이름으로 정확한 칵테일을 찾습니다."""
        # 정확한 이름 매칭 (대소문자 무시)
        query = "SELECT * FROM Cocktail WHERE LOWER(name) = LOWER(?)"
        self.cursor.execute(query, (name.strip(),))
        row = self.cursor.fetchone()

        if row:
            return self._format_cocktail_info(row)

        # 부분 매칭
        query = "SELECT * FROM Cocktail WHERE LOWER(name) LIKE LOWER(?)"
        self.cursor.execute(query, (f"%{name.strip()}%",))
        row = self.cursor.fetchone()

        if row:
            return self._format_cocktail_info(row)

        return {}

    def recommend_by_taste_ingredients(self, user_input: str, top_n: int = 5) -> List[Dict]:
        """
        사용자가 입력한 맛/재료를 기반으로 칵테일을 추천합니다.

        Args:
            user_input: 사용자가 입력한 맛/재료 설명 (예: "gin tonic lime lemon pitch Mezcal")
            top_n: 추천할 칵테일 개수

        Returns:
            추천 칵테일 리스트 (유사도 점수 및 매칭 키워드 포함)
        """
        # 모든 칵테일 가져오기
        rows = cocktail_select()  # 이미 정의된 함수 사용

        if not rows:
            return []

        user_input_cleaned = self._clean_ingredients(user_input)
        user_keywords = set(user_input_cleaned.split())

        recommendations = []

        for row in rows:
            if not row[0] or not row[1]:  # name 또는 ingredients가 없으면 건너뛰기
                continue

            # 재료 기반 유사도 계산
            cocktail_ingredients_cleaned = self._clean_ingredients(row[1])
            cocktail_keywords = set(cocktail_ingredients_cleaned.split())

            # 공통 키워드 개수 기반 점수
            common_keywords = user_keywords.intersection(cocktail_keywords)
            keyword_score = len(common_keywords) / max(len(user_keywords), 1)

            # 문자열 유사도 (SequenceMatcher 사용)
            text_similarity = SequenceMatcher(
                None,
                user_input_cleaned,
                cocktail_ingredients_cleaned
            ).ratio()

            # 최종 점수 (키워드 점수에 더 높은 가중치)
            final_score = (keyword_score * 0.7) + (text_similarity * 0.3)

            if final_score > 0.1:  # 최소 임계값
                cocktail_info = self._format_cocktail_info(row)
                cocktail_info['similarity_score'] = round(final_score, 3)
                cocktail_info['matching_keywords'] = list(common_keywords)
                recommendations.append(cocktail_info)

        # 점수 순으로 정렬하여 상위 n개 반환
        recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
        return recommendations[:top_n]

    def _format_cocktail_info(self, row) -> Dict:
        """칵테일 정보를 딕셔너리로 포맷팅합니다."""
        return {
            'name': row[0],
            'ingredients': row[1],
            'garnish': row[2] if row[2] else 'N/A',
            'glassware': row[3] if row[3] else 'N/A',
            'preparation': row[4] if row[4] else 'N/A',
            'price': f"${row[5]:.2f}" if row[5] else 'N/A',
            'note': row[6] if row[6] else 'N/A'
        }

    def search_cocktails_fuzzy(self, query: str, threshold: float = 0.6) -> List[Dict]:
        """
        칵테일 이름을 퍼지 검색합니다.

        Args:
            query: 검색할 칵테일 이름
            threshold: 유사도 임계값

        Returns:
            유사한 칵테일 리스트
        """
        query_lower = query.lower().strip()

        # 모든 칵테일 가져오기
        rows = cocktail_select()  # 이미 정의된 함수 사용

        fuzzy_matches = []

        for row in rows:
            if not row[0]:  # name이 없으면 건너뛰기
                continue

            similarity = SequenceMatcher(
                None,
                query_lower,
                row[0].lower()
            ).ratio()

            if similarity >= threshold:
                cocktail_info = self._format_cocktail_info(row)
                cocktail_info['name_similarity'] = round(similarity, 3)
                fuzzy_matches.append(cocktail_info)

        # 유사도 순으로 정렬
        fuzzy_matches.sort(key=lambda x: x['name_similarity'], reverse=True)
        return fuzzy_matches

    def get_cocktail_statistics(self) -> Dict:
        """데이터베이스 통계 정보를 반환합니다."""
        stats = {}

        # 전체 칵테일 수
        self.cursor.execute("SELECT COUNT(*) FROM Cocktail")
        stats['total_cocktails'] = self.cursor.fetchone()[0]

        # 고유 칵테일 수 (실제로는 name이 PRIMARY KEY이므로 total과 같음)
        self.cursor.execute("SELECT COUNT(DISTINCT name) FROM Cocktail")
        stats['unique_cocktails'] = self.cursor.fetchone()[0]

        # 재료가 있는 칵테일 수
        self.cursor.execute("SELECT COUNT(*) FROM Cocktail WHERE ingredients IS NOT NULL AND ingredients != ''")
        stats['has_ingredients'] = self.cursor.fetchone()[0]

        # 가니쉬가 있는 칵테일 수
        self.cursor.execute("SELECT COUNT(*) FROM Cocktail WHERE garnish IS NOT NULL AND garnish != ''")
        stats['has_garnish'] = self.cursor.fetchone()[0]

        # 글라스웨어가 있는 칵테일 수
        self.cursor.execute("SELECT COUNT(*) FROM Cocktail WHERE glassware IS NOT NULL AND glassware != ''")
        stats['has_glassware'] = self.cursor.fetchone()[0]

        # 준비방법이 있는 칵테일 수
        self.cursor.execute("SELECT COUNT(*) FROM Cocktail WHERE preparation IS NOT NULL AND preparation != ''")
        stats['has_preparation'] = self.cursor.fetchone()[0]

        return stats

    def find_cocktails_by_price_range(self, min_price: float = 0, max_price: float = 1000) -> List[Dict]:
        """
        가격 범위로 칵테일을 찾습니다.

        Args:
            min_price: 최소 가격
            max_price: 최대 가격

        Returns:
            가격 범위 내 칵테일 리스트
        """
        query = """
        SELECT * FROM Cocktail 
        WHERE price >= ? AND price <= ? 
        ORDER BY price
        """

        self.cursor.execute(query, (min_price, max_price))
        rows = self.cursor.fetchall()

        cocktails = []
        for row in rows:
            cocktail_info = self._format_cocktail_info(row)
            cocktails.append(cocktail_info)

        return cocktails

    def get_price_statistics(self) -> Dict:
        """가격 통계 정보를 반환합니다."""
        stats = {}

        # 평균 가격
        self.cursor.execute("SELECT AVG(price) FROM Cocktail WHERE price IS NOT NULL")
        avg_price = self.cursor.fetchone()[0]
        stats['average_price'] = round(avg_price, 2) if avg_price else 0

        # 최소/최대 가격
        self.cursor.execute("SELECT MIN(price), MAX(price) FROM Cocktail WHERE price IS NOT NULL")
        min_price, max_price = self.cursor.fetchone()
        stats['min_price'] = round(min_price, 2) if min_price else 0
        stats['max_price'] = round(max_price, 2) if max_price else 0

        return stats

    def add_cocktail(self, name: str, ingredients: str, garnish: str = None,
                    glassware: str = None, preparation: str = None,
                    price: float = 0.0, note: str = None) -> bool:
        """
        새로운 칵테일을 추가합니다.
        """
        try:
            return coctail_insert(name, ingredients, garnish, glassware, preparation, price, note)
        except sqlite3.IntegrityError:
            # 이미 존재하는 칵테일 이름
            return False
        except Exception as e:
            print(f"Error adding cocktail: {e}")
            return False

    def __del__(self):
        """소멸자에서 DB 연결 닫기"""
        if hasattr(self, 'conn'):
            self.conn.close()


def ingredient_search_demo():
    """재료 기반 검색 데모 함수"""
    service = CocktailService()

    print("칵테일 재료 기반 검색 서비스")
    print("=" * 50)
    print("재료나 맛을 입력하세요 (예: gin tonic lime, whiskey bourbon bitters)")
    print("종료하려면 'quit' 또는 'exit'를 입력하세요")
    print("=" * 50)

    while True:
        # 사용자 입력 받기
        search_query = input("\n검색어를 입력하세요: ").strip()

        # 종료 조건
        if search_query.lower() in ['quit', 'exit', '종료', 'q']:
            print("프로그램을 종료합니다.")
            break

        # 빈 입력 처리
        if not search_query:
            print("검색어를 입력해주세요.")
            continue

        print(f"\n검색어: {search_query}")
        print("-" * 50)

        # 유사도 기반 칵테일 추천
        # recommend_by_taste_ingredients 메서드는 다음과 같은 구조의 리스트를 반환:
        # [
        #     {
        #         'name': '칵테일 이름 (str)',
        #         'ingredients': '재료 목록 (str)',
        #         'garnish': '가니쉬 정보 (str) 또는 "N/A"',
        #         'glassware': '글라스웨어 정보 (str) 또는 "N/A"',
        #         'preparation': '제조 방법 (str) 또는 "N/A"',
        #         'price': '가격 정보 (str, 예: "$12.50") 또는 "N/A"',
        #         'note': '추가 메모 (str) 또는 "N/A"',
        #         'similarity_score': '유사도 점수 (float, 0.0~1.0)',
        #         'matching_keywords': '매칭된 키워드 리스트 (list of str)'
        #     },
        #     ... (최대 top_n개, 여기서는 5개)
        # ]
        # 반환되는 리스트는 similarity_score 기준으로 내림차순 정렬됨
        recommendations = service.recommend_by_taste_ingredients(search_query, top_n=5)

        if not recommendations:
            print("해당 재료로 추천할 칵테일이 없습니다.")
            continue

        print(recommendations)

        for i, cocktail in enumerate(recommendations, 1):
            print(f"{i}. 일치도가 {i}번으로 높은 칵테일 출력(유사도: {cocktail['similarity_score']})")
            print(f"   칵테일명: {cocktail['name']}")
            print(f"   재료: {cocktail['ingredients'][:80]}{'...' if len(cocktail['ingredients']) > 80 else ''}")
            print(f"   일치 검색어: {' '.join(cocktail['matching_keywords'])}")
            print(f"   가격: {cocktail['price']}")
            if i < len(recommendations):
                print()

        print("\n" + "=" * 50)


if __name__ == "__main__":
    ingredient_search_demo()
