"""
간단한 주문 시스템
GUI에서 칵테일 이름을 받아서 CSV에 저장
"""

import csv
import sys
import os
from datetime import datetime
from typing import Optional, Dict

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.db.conn import db_connect


class OrderService:
    def __init__(self):
        self.conn = db_connect()
        self.cursor = self.conn.cursor()
        
        # data 폴더 경로 설정
        data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            "data"
        )
        
        # data 폴더가 없으면 생성
        os.makedirs(data_dir, exist_ok=True)
        
        self.orders_csv_path = os.path.join(data_dir, "orders.csv")

    def find_cocktail_ingredients(self, cocktail_name: str) -> Optional[str]:
        """칵테일 이름으로 재료를 찾습니다."""
        query = "SELECT ingredients FROM Cocktail WHERE LOWER(name) = LOWER(?)"
        self.cursor.execute(query, (cocktail_name.strip(),))
        row = self.cursor.fetchone()
        
        if row and row[0]:
            return row[0]
        return None

    def find_cocktail_preparation(self, cocktail_name: str) -> Optional[str]:
        """칵테일 이름으로 레시피를 찾습니다."""
        query = "SELECT preparation FROM Cocktail WHERE LOWER(name) = LOWER(?)"
        self.cursor.execute(query, (cocktail_name.strip(),))
        row = self.cursor.fetchone()
        if row and row[0]:
            return row[0]
        return None

    def save_order(self, cocktail_name: str, quantity: int = 1):
        """주문을 CSV에 저장합니다."""
        ingredients = self.find_cocktail_ingredients(cocktail_name)
        
        if not ingredients:
            return
        
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # CSV에 저장
        with open(self.orders_csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # 주문 정보
            writer.writerow([order_date, cocktail_name, quantity])
            
            ingredient_list = [ing.strip() for ing in ingredients.split(',')]
            for ingredient in ingredient_list:
                if ingredient:
                    writer.writerow([f"-- {ingredient}"])

    def process_gui_order(self, cocktail_name: str, quantity: int = 1, request: str = "", order_time: str = None) -> bool:
        """
        GUI에서 호출할 주문 처리 함수
        Args:
            cocktail_name: GUI에서 받아온 칵테일 이름
            quantity: 주문 수량 (기본값: 1)
            request: 사용자가 입력한 요청사항 (기본값: "")
            order_time: 주문 시간(타임스탬프), 없으면 현재 시간
        Returns:
            주문 처리 성공 여부
        """
        ingredients = self.find_cocktail_ingredients(cocktail_name)
        preparation = self.find_cocktail_preparation(cocktail_name)
        if not ingredients:
            return False
        order_date = order_time if order_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.orders_csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for _ in range(quantity):
                writer.writerow([
                    order_date,
                    cocktail_name,
                    ingredients,
                    preparation if preparation else "",
                    request if request else ""
                ])
        return True

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()


def demo():
    """임시로 The Happy Place 주문 처리"""
    order_service = OrderService()
    order_service.save_order("The Happy Place", 1)


# GUI 개발자가 사용할 함수
def place_order_from_gui(cocktail_name: str, quantity: int = 1) -> bool:
    """
    GUI에서 호출할 주문 함수
    
    Args:
        cocktail_name: 주문할 칵테일 이름
        quantity: 주문 수량
        
    Returns:
        주문 성공 여부
    """
    order_service = OrderService()
    return order_service.process_gui_order(cocktail_name, quantity)


if __name__ == "__main__":
    # 임시 데모
    demo()
