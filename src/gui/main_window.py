import customtkinter as ctk
import sys, os
import random

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.services.cocktail_service import CocktailService
from src.services.order_service import OrderService

# 테마 및 색상 정의
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# 색상 및 패딩 상수
BG_COLOR     = "#1f1f1f"
CARD_COLOR   = "#2a2a2f"
ACCENT_COLOR = "#4e8cff"
TEXT_COLOR   = "#e0e0e0"
PADDING      = 16
ERROR_COLOR  = "#d9534f"
SUCCESS_COLOR = "#4ecf8c"
WARNING_COLOR = "#ffb84e"

# 전역 변수들
cocktail_service = None
ALL_MENUS = []

def initialize_services():
    """서비스 초기화 함수"""
    global cocktail_service, ALL_MENUS
    try:
        cocktail_service = CocktailService()
        ALL_MENUS = cocktail_service.get_all_cocktails()
        return True
    except Exception as e:
        print(f"서비스 초기화 오류: {e}")
        return False

# 가격 문자열을 float(달러 단위)로 변환하는 함수
def parse_price(price_str):
    try:
        # "$12.00" -> 12.00
        return float(price_str.replace("$", "").replace(",", ""))
    except Exception:
        return 0.0

# --- UI 컴포넌트 클래스 ---

class Toast(ctk.CTkToplevel):
    def __init__(self, parent, message, duration=2000):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.configure(bg=BG_COLOR)
        font = ctk.CTkFont(size=14, weight="bold")
        w, h = 320, 48
        parent.update_idletasks()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = px + (pw - w) // 2
        y = py + ph - h - 48
        self.geometry(f"{w}x{h}+{x}+{y}")

        frame = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=12, border_width=0)
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.98, relheight=0.92)

        lbl = ctk.CTkLabel(
            frame,
            text=message,
            font=font,
            fg_color="transparent",
            text_color=ACCENT_COLOR,
            anchor="center",
            wraplength=w-40,
            justify="center"
        )
        lbl.pack(expand=True, fill="both", padx=12, pady=6)

        self.attributes("-alpha", 0.0)
        self._fade_in(0)

        self.after(duration, self._fade_out)

    def _fade_in(self, step):
        alpha = min(1.0, step / 8)
        self.attributes("-alpha", alpha)
        if alpha < 1.0:
            self.after(20, self._fade_in, step + 1)

    def _fade_out(self):
        self._fade_out_step(8)

    def _fade_out_step(self, step):
        alpha = max(0.0, step / 8)
        self.attributes("-alpha", alpha)
        if alpha > 0.0:
            self.after(20, self._fade_out_step, step - 1)
        else:
            self.destroy()

# Tooltip 클래스: 전체메뉴에서 Ingredients(재료) 툴팁으로 사용
class Tooltip:
    def __init__(self, widget, ingredients_text):
        self.widget = widget
        self.ingredients_text = ingredients_text
        self.tipwindow = None

    def show(self, x, y):
        if self.tipwindow or not self.ingredients_text:
            return
        self.tipwindow = tw = ctk.CTkToplevel(self.widget)
        tw.overrideredirect(True)
        tw.attributes('-topmost', True)
        tw.geometry(f"+{x}+{y}")

        # 툴팁 내부: 아이콘(더 크게) + 텍스트(더 크게)
        frame = ctk.CTkFrame(
            tw,
            fg_color=CARD_COLOR,
            corner_radius=8,
            border_width=0
        )
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        # 아이콘 더 크게 (기존 22 → 28)
        icon_lbl = ctk.CTkLabel(
            frame,
            text="ⓘ",
            font=ctk.CTkFont(size=28, weight="bold"),
            fg_color="transparent",
            text_color=ACCENT_COLOR,
            anchor="w",
            width=40
        )
        icon_lbl.pack(side="left", padx=(10, 6), pady=10)

        # "Ingredients : ..." 형식으로 표시
        desc_text = f"Ingredients : {self.ingredients_text}"

        # 텍스트 크기 조절 (기존 13 → 15)
        text_lbl = ctk.CTkLabel(
            frame,
            text=desc_text,
            fg_color="transparent",
            text_color=TEXT_COLOR,
            corner_radius=0,
            font=ctk.CTkFont(size=15, weight="bold"),
            wraplength=260,
            anchor="w",
            justify="left"
        )
        text_lbl.pack(side="left", padx=(0, 16), pady=10)

    def hide(self):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

class MenuCard(ctk.CTkFrame):
    def __init__(self, parent, item, fonts, detail_callback=None, cart_callback=None, show_detail_btn=True, show_cart_btn=False, fixed_width=180, fixed_height=160):
        super().__init__(parent, fg_color=CARD_COLOR, corner_radius=8, border_width=1, border_color="#333333")
        self.item = item
        self.fonts = fonts
        self.detail_callback = detail_callback
        self.cart_callback = cart_callback
        self.configure(width=fixed_width, height=fixed_height)
        self.grid_propagate(False)
        ctk.CTkLabel(self, text=item['name'], font=fonts['item'], text_color=TEXT_COLOR).pack(pady=(12, 4))
        ctk.CTkLabel(self, text=item['price'], font=fonts['small'], text_color=ACCENT_COLOR).pack(pady=(0, 8))
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 12))
        if show_detail_btn:
            ctk.CTkButton(
                btn_frame,
                text="장바구니 담기",
                width=100,
                font=fonts['small'],
                fg_color=ACCENT_COLOR,
                corner_radius=6,
                command=lambda: self.cart_callback(item, 1) if self.cart_callback else None
            ).pack(side="left", padx=4)
        if show_cart_btn:
            self.qty = ctk.IntVar(value=1)
            ctk.CTkButton(btn_frame, text="-", width=30, command=lambda: self.qty.set(max(1, self.qty.get()-1))).pack(side="left", padx=2)
            ctk.CTkLabel(btn_frame, textvariable=self.qty, width=30, anchor="center").pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="+", width=30, command=lambda: self.qty.set(self.qty.get()+1)).pack(side="left", padx=2)
            ctk.CTkButton(
                btn_frame,
                text="장바구니",
                fg_color=ACCENT_COLOR,
                corner_radius=6,
                command=lambda: self.cart_callback(item, self.qty.get()) if self.cart_callback else None
            ).pack(side="left", padx=4)
        # info_lbl 및 툴팁 제거

# --- 장바구니 리스트 아이템 (수정된 부분) ---
class CartListItem(ctk.CTkFrame):
    def __init__(self, parent, item, qty, fonts, on_qty_change, on_remove):
        super().__init__(parent, fg_color=CARD_COLOR, corner_radius=8, border_width=1, border_color="#333333")
        self.item = item
        self.fonts = fonts
        self.on_qty_change = on_qty_change
        self.on_remove = on_remove
        self.qty = ctk.IntVar(value=qty)

        self.columnconfigure(0, weight=3, minsize=180)
        self.columnconfigure(1, weight=1, minsize=80)
        self.columnconfigure(2, weight=2, minsize=180)
        self.columnconfigure(3, weight=1, minsize=120)  # 가격(합계) 칸 넓힘
        self.columnconfigure(4, weight=0, minsize=36)
        self.columnconfigure(5, weight=0, minsize=36)

        # 이름
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=8)
        ctk.CTkLabel(left, text=item['name'], font=fonts['item'], text_color=TEXT_COLOR, anchor="w").pack(anchor="w")

        # 단가
        unit_price = parse_price(item.get('price', '0'))

        # 합계 가격 라벨
        self.total_price_lbl = ctk.CTkLabel(self, text="", font=fonts['item'], text_color=ACCENT_COLOR, width=110, anchor="center")
        self._update_total_price(unit_price)
        self.total_price_lbl.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

        # 수량 조절
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=2, sticky="e", padx=(0, 12), pady=8)
        ctk.CTkButton(right, text="-", width=30, command=self._decrease_qty).pack(side="left", padx=2)
        ctk.CTkLabel(right, textvariable=self.qty, width=30, anchor="center").pack(side="left", padx=2)
        ctk.CTkButton(right, text="+", width=30, command=self._increase_qty).pack(side="left", padx=2)

        # 단가(작게) 표시
        self.unit_price_lbl = ctk.CTkLabel(self, text=f"(each {item.get('price', '')})", font=fonts['small'], text_color="#888888", anchor="w")
        self.unit_price_lbl.grid(row=0, column=3, sticky="w", padx=(0, 0), pady=8)

        # 삭제 버튼
        remove_btn = ctk.CTkButton(
            self,
            text="삭제",
            fg_color="#d9534f",
            text_color="#fff",
            corner_radius=6,
            width=50,
            command=self._remove_item
        )
        remove_btn.grid(row=0, column=4, sticky="e", padx=(0, 8), pady=8)

        # 수량이 바뀔 때마다 합계 가격 갱신
        self.qty.trace_add("write", lambda *args: self._update_total_price(unit_price))

    def _update_total_price(self, unit_price):
        total = unit_price * self.qty.get()
        # 달러 표기, 소수점 2자리, 1000단위 콤마
        total_str = f"${total:,.2f}"
        self.total_price_lbl.configure(text=total_str)

    def _decrease_qty(self):
        if self.qty.get() > 1:
            self.qty.set(self.qty.get() - 1)
            self.on_qty_change(self.item, self.qty.get())
        elif self.qty.get() == 1:
            # 1에서 - 누르면 삭제
            self.on_remove(self.item)

    def _increase_qty(self):
        self.qty.set(self.qty.get() + 1)
        self.on_qty_change(self.item, self.qty.get())

    def _remove_item(self):
        self.on_remove(self.item)

# --- 장바구니 탭 (수정된 부분) ---
class CartListTab(ctk.CTkFrame):
    def __init__(self, parent, fonts, cart, on_qty_change=None, on_remove=None, on_purchase=None, padding=PADDING):
        super().__init__(parent, fg_color=BG_COLOR)
        self.fonts = fonts
        self.cart = cart
        self.padding = padding
        self.on_qty_change = on_qty_change
        self.on_remove = on_remove
        self.on_purchase = on_purchase

        # 내부 스크롤 프레임
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=BG_COLOR)
        self.scroll_frame.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        # 총합 가격 라벨
        self.total_label = ctk.CTkLabel(self, text="", font=self.fonts['head'], text_color=ACCENT_COLOR, anchor="e")
        self.total_label.pack(fill="x", padx=(0, 24), pady=(8, 0), side="top", anchor="e")

        # 구매하기 버튼 프레임
        self.button_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.button_frame.pack(fill="x", side="bottom", padx=0, pady=(0, 8), anchor="se")

        self.purchase_btn = ctk.CTkButton(
            self.button_frame,
            text="구매하기",
            fg_color=ACCENT_COLOR,
            corner_radius=8,
            font=self.fonts['head'],
            width=180,
            height=44,
            command=self._on_purchase_click
        )
        self.purchase_btn.pack(side="right", padx=(0, 16), pady=(0, 0))

        self.refresh()

    def refresh(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        if not self.cart:
            ctk.CTkLabel(self.scroll_frame, text="장바구니가 비어 있습니다.", font=self.fonts['item']).pack(pady=20)
            self.purchase_btn.configure(state="disabled")
            self.total_label.configure(text="Total: $0.00")
            return
        # 메뉴 정보 매칭
        total_sum = 0.0
        for idx, (name, qty) in enumerate(self.cart.items()):
            # 메뉴 정보 찾기
            item = next((m for m in ALL_MENUS if m['name'] == name), None)
            if not item:
                # 혹시 메뉴가 삭제된 경우 등
                item = {"name": name, "desc": "", "price": ""}
            unit_price = parse_price(item.get('price', '0'))
            total_sum += unit_price * qty
            row_frame = CartListItem(
                self.scroll_frame,
                item,
                qty,
                self.fonts,
                on_qty_change=self.on_qty_change if self.on_qty_change else lambda i, q: None,
                on_remove=self.on_remove if self.on_remove else lambda i: None
            )
            row_frame.grid(row=idx, column=0, sticky="ew", padx=4, pady=4)
            self.scroll_frame.grid_rowconfigure(idx, weight=0)
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.purchase_btn.configure(state="normal")
        self.total_label.configure(text=f"Total: ${total_sum:,.2f}")

    def _on_purchase_click(self):
        if self.on_purchase:
            self.on_purchase()
        else:
            # 기본 동작: 토스트로 안내
            Toast(self, "구매 기능이 아직 구현되지 않았습니다.")

# --- 탭별 프레임 클래스 ---

class StartFrame(ctk.CTkFrame):
    def __init__(self, parent, fonts, start_callback, admin_callback=None):
        super().__init__(parent, fg_color=BG_COLOR)
        btn = ctk.CTkButton(
            self,
            text="시작하시려면 터치",
            font=fonts['head'],
            fg_color=ACCENT_COLOR,
            hover_color="#3a6fcc",
            corner_radius=8,
            width=220,
            height=50,
            command=start_callback
        )
        btn.place(relx=0.5, rely=0.5, anchor="center")

        # 관리자 모드 진입용 라벨(버튼처럼 동작)
        def on_admin_click():
            if admin_callback:
                admin_callback()
            else:
                Toast(self, "관리자 모드 진입 (예시)")

        admin_label = ctk.CTkLabel(
            self,
            text="관리자 모드",
            font=fonts['small'],
            text_color="#777777",
            cursor="hand2"
        )
        admin_label.place(relx=0.5, rely=0.5, anchor="n", y=60)  # 시작버튼 아래에 위치

        admin_label.bind("<Button-1>", lambda e: on_admin_click())

class RecommendTab(ctk.CTkFrame):
    def __init__(self, parent, fonts, cart_callback):
        super().__init__(parent, fg_color=BG_COLOR)
        self.fonts = fonts
        self.cart_callback = cart_callback
        self._build()

    def _build(self):
        all_menus = ALL_MENUS.copy()
        random.shuffle(all_menus)
        popular_menus = random.sample(all_menus, min(6, len(all_menus)))
        random.shuffle(all_menus)
        expert_menus = random.sample(all_menus, min(6, len(all_menus)))
        section_configs = [
            ("금주 인기 메뉴", popular_menus, 200),
            ("전문가 추천", expert_menus, 200),
        ]
        for idx, (title, seq, height) in enumerate(section_configs):
            ctk.CTkLabel(self, text=title, font=self.fonts['head']).pack(anchor="w", padx=PADDING, pady=(10, 4))
            pady = (0, PADDING) if idx < len(section_configs)-1 else (0, 0)
            sec = ctk.CTkScrollableFrame(self, height=height, fg_color=BG_COLOR, border_width=0)
            sec.pack(fill="x", padx=PADDING, pady=pady)
            columns = 3
            for i, item in enumerate(seq):
                row, col = divmod(i, columns)
                card = MenuCard(sec, item, self.fonts, detail_callback=None, cart_callback=self.cart_callback, show_detail_btn=True, show_cart_btn=False, fixed_width=180, fixed_height=160)
                card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            for c in range(columns):
                sec.grid_columnconfigure(c, weight=1)

# 전체메뉴 UI: 한줄 리스트 형식 (정렬 개선)
class MenuListItem(ctk.CTkFrame):
    def __init__(self, parent, item, fonts, cart_callback=None, admin_mode=False, on_edit=None, on_delete=None):
        super().__init__(parent, fg_color=CARD_COLOR, corner_radius=8, border_width=1, border_color="#333333")
        self.item = item
        self.fonts = fonts
        self.cart_callback = cart_callback
        self.admin_mode = admin_mode
        self.on_edit = on_edit
        self.on_delete = on_delete

        # grid 기반으로 정렬
        self.columnconfigure(0, weight=3, minsize=180)
        self.columnconfigure(1, weight=1, minsize=80)
        self.columnconfigure(2, weight=2, minsize=180)
        self.columnconfigure(3, weight=0, minsize=36)  # 툴팁 버튼용 (더 작게)

        # 왼쪽: 이름만
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=8)
        name_label = ctk.CTkLabel(left, text=item['name'], font=fonts['item'], text_color=TEXT_COLOR, anchor="w")
        name_label.pack(anchor="w")
        # 설명(재료)는 표시하지 않음

        # 가운데: 가격
        price_lbl = ctk.CTkLabel(self, text=item['price'], font=fonts['item'], text_color=ACCENT_COLOR, width=90, anchor="center")
        price_lbl.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

        # 오른쪽: 수량/장바구니 버튼
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=2, sticky="e", padx=(0, 12), pady=8)
        self.qty = ctk.IntVar(value=1)
        ctk.CTkButton(right, text="-", width=30, command=lambda: self.qty.set(max(1, self.qty.get()-1))).pack(side="left", padx=2)
        ctk.CTkLabel(right, textvariable=self.qty, width=30, anchor="center").pack(side="left", padx=2)
        ctk.CTkButton(right, text="+", width=30, command=lambda: self.qty.set(self.qty.get()+1)).pack(side="left", padx=2)
        ctk.CTkButton(
            right,
            text="장바구니",
            fg_color=ACCENT_COLOR,
            corner_radius=6,
            command=lambda: self.cart_callback(item, self.qty.get()) if self.cart_callback else None
        ).pack(side="left", padx=4)

        # 마지막: 툴팁 버튼 (Ingredients)
        tooltip_btn = ctk.CTkButton(
            self,
            text="ⓘ",
            width=26,   # 더 작게
            height=26,  # 더 작게
            fg_color="#444444",
            text_color="#cccccc",
            font=ctk.CTkFont(size=20, weight="bold"),  # 버튼 내 아이콘은 약간만 크게
            corner_radius=13,
            hover_color="#666666",
            command=None  # 클릭시 동작 없음, hover만
        )
        tooltip_btn.grid(row=0, column=3, sticky="e", padx=(0, 8), pady=8)

        # Tooltip 인스턴스: Ingredients(재료) 정보를 표시
        # ingredients 필드가 있으면 사용, 없으면 desc, garnish 순서로 대체
        ingredients = item.get('ingredients', '') or item.get('desc', '') or item.get('garnish', '')
        self._tooltip = Tooltip(tooltip_btn, ingredients)

        # 마우스 오버/아웃 이벤트 바인딩
        def on_enter(event):
            # 버튼의 위치를 기준으로 툴팁 위치 계산
            x = tooltip_btn.winfo_rootx() + tooltip_btn.winfo_width() + 4
            y = tooltip_btn.winfo_rooty()
            self._tooltip.show(x, y)
        def on_leave(event):
            self._tooltip.hide()
        tooltip_btn.bind("<Enter>", on_enter)
        tooltip_btn.bind("<Leave>", on_leave)

        # --- 관리자 모드: 이름 클릭시 수정/삭제 다이얼로그 ---
        if self.admin_mode:
            def on_menu_click(event):
                dialog = ctk.CTkToplevel(self)
                dialog.title("메뉴 관리")
                dialog.geometry("400x320")
                dialog.grab_set()
                dialog.configure(bg=BG_COLOR)
                dialog.resizable(False, False)

                # 상단 타이틀
                ctk.CTkLabel(
                    dialog,
                    text="메뉴 관리",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=ACCENT_COLOR
                ).pack(pady=(24, 4))

                # 메뉴 정보 상세
                info_frame = ctk.CTkFrame(dialog, fg_color=CARD_COLOR, corner_radius=10)
                info_frame.pack(fill="x", padx=24, pady=(8, 16))

                ctk.CTkLabel(
                    info_frame,
                    text=f"이름: {self.item['name']}",
                    font=self.fonts['item'],
                    text_color=TEXT_COLOR,
                    anchor="w"
                ).pack(anchor="w", padx=16, pady=(12, 2))
                ctk.CTkLabel(
                    info_frame,
                    text=f"가격: {self.item['price']}",
                    font=self.fonts['item'],
                    text_color=ACCENT_COLOR,
                    anchor="w"
                ).pack(anchor="w", padx=16, pady=2)
                ctk.CTkLabel(
                    info_frame,
                    text=f"설명: {self.item.get('desc', '')}",
                    font=self.fonts['small'],
                    text_color="#bbbbbb",
                    anchor="w",
                    wraplength=320,
                    justify="left"
                ).pack(anchor="w", padx=16, pady=(2, 12))

                # 버튼 프레임
                btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
                btn_frame.pack(pady=8)

                def do_edit():
                    dialog.destroy()
                    if self.on_edit:
                        self.on_edit(self.item)

                def do_delete():
                    # 삭제 확인 다이얼로그
                    confirm = ctk.CTkToplevel(dialog)
                    confirm.title("삭제 확인")
                    confirm.geometry("340x180")
                    confirm.grab_set()
                    confirm.configure(bg=BG_COLOR)
                    confirm.resizable(False, False)

                    ctk.CTkLabel(
                        confirm,
                        text="정말로 이 메뉴를 삭제하시겠습니까?",
                        font=ctk.CTkFont(size=15, weight="bold"),
                        text_color=ERROR_COLOR,
                        wraplength=300,
                        anchor="center",
                        justify="center"
                    ).pack(pady=(28, 8), padx=16)

                    ctk.CTkLabel(
                        confirm,
                        text=f"'{self.item['name']}'",
                        font=ctk.CTkFont(size=14),
                        text_color=ACCENT_COLOR
                    ).pack(pady=(0, 12))

                    btns = ctk.CTkFrame(confirm, fg_color="transparent")
                    btns.pack(pady=8)

                    def really_delete():
                        confirm.destroy()
                        dialog.destroy()
                        if self.on_delete:
                            self.on_delete(self.item)

                    ctk.CTkButton(
                        btns,
                        text="삭제",
                        fg_color=ERROR_COLOR,
                        text_color="#fff",
                        corner_radius=6,
                        width=100,
                        command=really_delete
                    ).pack(side="left", padx=8)
                    ctk.CTkButton(
                        btns,
                        text="취소",
                        fg_color="#444444",
                        corner_radius=6,
                        width=100,
                        command=confirm.destroy
                    ).pack(side="left", padx=8)

                ctk.CTkButton(
                    btn_frame,
                    text="수정",
                    fg_color=ACCENT_COLOR,
                    corner_radius=6,
                    width=120,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    command=do_edit
                ).pack(side="left", padx=12)
                ctk.CTkButton(
                    btn_frame,
                    text="삭제",
                    fg_color=ERROR_COLOR,
                    text_color="#fff",
                    corner_radius=6,
                    width=120,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    command=do_delete
                ).pack(side="left", padx=12)

                # 하단 닫기 버튼
                ctk.CTkButton(
                    dialog,
                    text="닫기",
                    fg_color="#444444",
                    corner_radius=6,
                    width=80,
                    font=ctk.CTkFont(size=13),
                    command=dialog.destroy
                ).pack(pady=(24, 0))

            # 이름 라벨에만 클릭 바인딩 (관리자 모드일 때만)
            name_label.bind("<Button-1>", on_menu_click)

class MenuTab(ctk.CTkFrame):
    PAGE_SIZE = 10

    def __init__(self, parent, fonts, cart_callback, admin_mode=False, on_edit=None, on_delete=None):
        super().__init__(parent, fg_color=BG_COLOR)
        self.fonts = fonts
        self.cart_callback = cart_callback
        self.admin_mode = admin_mode
        self.on_edit = on_edit
        self.on_delete = on_delete
        self._search_var = ctk.StringVar()
        # DB에서 메뉴 불러오기
        global cocktail_service
        if cocktail_service:
            self._all_menus = cocktail_service.get_all_cocktails()
        else:
            self._all_menus = []
        self._filtered_menus = self._all_menus.copy()
        self._current_page = 0
        self._build()
        self._bind_mousewheel(self)

    def _on_mousewheel(self, event):
        if hasattr(event, 'delta'):
            delta = event.delta
        elif hasattr(event, 'num'):
            delta = 120 if event.num == 4 else -120
        else:
            delta = 0
        self.sec._parent_canvas.yview_scroll(int(-1*(delta/120)), "units")

    def _bind_mousewheel(self, widget):
        widget.bind("<Enter>", self._activate_mousewheel)
        widget.bind("<Leave>", self._deactivate_mousewheel)

    def _activate_mousewheel(self, event):
        self.sec.bind("<MouseWheel>", self._on_mousewheel)
        self.sec.bind("<Button-4>", self._on_mousewheel)
        self.sec.bind("<Button-5>", self._on_mousewheel)

    def _deactivate_mousewheel(self, event):
        self.sec.unbind("<MouseWheel>")
        self.sec.unbind("<Button-4>")
        self.sec.unbind("<Button-5>")

    def _build(self):
        # 검색창 프레임 추가
        search_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        search_frame.pack(fill="x", padx=PADDING, pady=(PADDING, 0))
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self._search_var,
            placeholder_text="메뉴명으로 검색...",
            width=320
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            search_frame,
            text="검색",
            fg_color=ACCENT_COLOR,
            corner_radius=6,
            command=self._on_search
        ).pack(side="left", padx=8)

        # 엔터키로 검색 가능하게
        self.search_entry.bind("<Return>", lambda event: self._on_search())

        # 입력할 때마다 자동 검색
        self._search_var.trace_add("write", lambda *args: self._on_search())

        # 한줄 리스트 형식 UI, grid로 정렬
        self.sec = ctk.CTkScrollableFrame(self, fg_color=BG_COLOR)
        self.sec.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)

        # 페이징 컨트롤 프레임
        self.paging_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.paging_frame.pack(fill="x", padx=PADDING, pady=(0, PADDING))

        self._draw_menu_list()

    def _draw_menu_list(self):
        for w in self.sec.winfo_children():
            w.destroy()
        # 페이징 처리
        total_items = len(self._filtered_menus)
        total_pages = max(1, (total_items + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        self._current_page = max(0, min(self._current_page, total_pages - 1))
        start_idx = self._current_page * self.PAGE_SIZE
        end_idx = min(start_idx + self.PAGE_SIZE, total_items)
        page_items = self._filtered_menus[start_idx:end_idx]

        for idx, item in enumerate(page_items):
            row_frame = MenuListItem(
                self.sec,
                item,
                self.fonts,
                cart_callback=self.cart_callback,
                admin_mode=self.admin_mode,
                on_edit=self.on_edit,
                on_delete=self.on_delete
            )
            row_frame.grid(row=idx, column=0, sticky="ew", padx=4, pady=4)
            self.sec.grid_rowconfigure(idx, weight=0)
        self.sec.grid_columnconfigure(0, weight=1)

        # 페이징 컨트롤 (가운데 정렬)
        for w in self.paging_frame.winfo_children():
            w.destroy()
        paging_inner = ctk.CTkFrame(self.paging_frame, fg_color=BG_COLOR)
        paging_inner.pack(anchor="center")
        btn_prev = ctk.CTkButton(
            paging_inner,
            text="이전",
            fg_color="#444444",
            corner_radius=6,
            width=80,
            state="normal" if self._current_page > 0 else "disabled",
            command=self._go_prev_page
        )
        btn_prev.pack(side="left", padx=8, pady=4)
        page_label = ctk.CTkLabel(
            paging_inner,
            text=f"{self._current_page+1} / {total_pages}",
            font=self.fonts['item'],
            text_color=ACCENT_COLOR
        )
        page_label.pack(side="left", padx=8)
        btn_next = ctk.CTkButton(
            paging_inner,
            text="다음",
            fg_color="#444444",
            corner_radius=6,
            width=80,
            state="normal" if self._current_page < total_pages-1 else "disabled",
            command=self._go_next_page
        )
        btn_next.pack(side="left", padx=8, pady=4)

    def _go_prev_page(self):
        if self._current_page > 0:
            self._current_page -= 1
            self._draw_menu_list()

    def _go_next_page(self):
        total_items = len(self._filtered_menus)
        total_pages = max(1, (total_items + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        if self._current_page < total_pages - 1:
            self._current_page += 1
            self._draw_menu_list()

    def _on_search(self, *args):
        keyword = self._search_var.get().strip()
        if not keyword:
            self._filtered_menus = self._all_menus.copy()
        else:
            kw = keyword.lower()
            self._filtered_menus = [
                item for item in self._all_menus
                if kw in item['name'].lower()
            ]
        self._current_page = 0
        self._draw_menu_list()

    def destroy(self):
        super().destroy()

class SearchTab(ctk.CTkFrame):
    def __init__(self, parent, fonts, search_callback):
        super().__init__(parent, fg_color=BG_COLOR)
        self.fonts = fonts
        self.search_callback = search_callback
        self._build()

    def _build(self):
        sf = ctk.CTkFrame(self, fg_color=BG_COLOR)
        sf.pack(fill="x", padx=PADDING, pady=(10,0))
        self.search_entry = ctk.CTkEntry(sf, placeholder_text="검색어 입력...", width=400)
        self.search_entry.pack(side="left", expand=True)
        ctk.CTkButton(sf, text="검색", fg_color=ACCENT_COLOR, corner_radius=6, command=self.search_callback).pack(side="left", padx=8)
        self.result_list = ctk.CTkScrollableFrame(self, fg_color=BG_COLOR)
        self.result_list.pack(fill="both", expand=True, padx=PADDING, pady=(8,0))

class RequestTab(ctk.CTkFrame):
    def __init__(self, parent, fonts):
        super().__init__(parent, fg_color=BG_COLOR)
        ctk.CTkLabel(self, text="요청사항 준비 중...", font=fonts['item']).pack(pady=20)

class DetailFrame(ctk.CTkFrame):
    def __init__(self, parent, fonts, back_callback):
        super().__init__(parent, fg_color=BG_COLOR)
        self.fonts = fonts
        self.back_callback = back_callback
        self.inner = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.inner.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)

    def show_detail(self, item):
        for w in self.inner.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.inner, text=item['name'], font=self.fonts['head'], text_color=ACCENT_COLOR).pack(pady=(20,8))
        ctk.CTkLabel(self.inner, text=item['desc'], font=self.fonts['item'], text_color=TEXT_COLOR).pack(pady=5)
        ctk.CTkLabel(self.inner, text=item['price'], font=self.fonts['item'], text_color=ACCENT_COLOR).pack(pady=5)
        ctk.CTkButton(self.inner, text="뒤로", fg_color=ACCENT_COLOR, corner_radius=6, command=self.back_callback).pack(pady=20)

# --- 메인 애플리케이션 ---

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 서비스 초기화
        if not initialize_services():
            # 초기화 실패 시 기본값으로 설정
            global ALL_MENUS
            ALL_MENUS = []
            print("서비스 초기화에 실패했습니다. 기본값으로 실행합니다.")
        
        self.fonts = {
            'head': ctk.CTkFont(size=18, weight="bold"),
            'item': ctk.CTkFont(size=14),
            'small': ctk.CTkFont(size=12)
        }
        self.title("k-tail")
        self.geometry("640x840")
        self.configure(fg_color=BG_COLOR)
        self.cart = {}

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.is_admin = False  # 관리자 모드 여부

        self.start_frame  = StartFrame(self, self.fonts, self._show_main, self._show_admin)
        self.main_frame   = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.detail_frame = DetailFrame(self, self.fonts, self._show_main)

        self.tabview = ctk.CTkTabview(self.main_frame, width=600)
        self.tabview.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        self.tabs = {}
        self._setup_tabs()

        self.start_frame.pack(fill="both", expand=True)

    def _setup_tabs(self):
        # 어드민 모드일 때는 추천, 검색 탭을 안보이게 한다
        if self.is_admin:
            tab_names = ["전체메뉴", "장바구니", "요청사항"]
        else:
            tab_names = ["인기", "전체메뉴", "추천", "장바구니", "요청사항"]
        for name in tab_names:
            self.tabview.add(name)
        # 기본 선택 탭
        if self.is_admin:
            self.tabview.set("전체메뉴")
        else:
            self.tabview.set("인기")
        # 탭별 프레임 생성
        if not self.is_admin:
            self.tabs["인기"] = RecommendTab(self.tabview.tab("인기"), self.fonts, self._add_to_cart)
            self.tabs["인기"].pack(fill="both", expand=True)

        # 전체메뉴 탭: 관리자 모드 여부에 따라 admin_mode, on_edit, on_delete 전달
        self.tabs["전체메뉴"] = MenuTab(
            self.tabview.tab("전체메뉴"),
            self.fonts,
            self._add_to_cart,
            admin_mode=self.is_admin,
            on_edit=self._on_menu_edit,
            on_delete=self._on_menu_delete
        )
        self.tabs["전체메뉴"].pack(fill="both", expand=True)

        if not self.is_admin:
            self.tabs["추천"] = SearchTab(self.tabview.tab("추천"), self.fonts, self._on_search)
            self.tabs["추천"].pack(fill="both", expand=True)

        # 장바구니 탭: CartListTab에 콜백 전달 및 구매하기 버튼 포함
        self.tabs["장바구니"] = CartListTab(
            self.tabview.tab("장바구니"),
            self.fonts,
            self.cart,
            on_qty_change=self._on_cart_qty_change,
            on_remove=self._on_cart_remove,
            on_purchase=self._on_purchase
        )
        self.tabs["장바구니"].pack(fill="both", expand=True, padx=PADDING, pady=PADDING)

        self.tabs["요청사항"] = RequestTab(self.tabview.tab("요청사항"), self.fonts)
        self.tabs["요청사항"].pack(fill="both", expand=True)

    def _refresh_cart(self):
        self.tabs["장바구니"].cart = self.cart
        self.tabs["장바구니"].refresh()

    def _show_main(self):
        self.detail_frame.pack_forget()
        self.start_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)
        # 관리자 모드가 변경되었을 수 있으니 전체메뉴 탭을 다시 생성
        self.tabs["전체메뉴"].destroy()
        self.tabs["전체메뉴"] = MenuTab(
            self.tabview.tab("전체메뉴"),
            self.fonts,
            self._add_to_cart,
            admin_mode=self.is_admin,
            on_edit=self._on_menu_edit,
            on_delete=self._on_menu_delete
        )
        self.tabs["전체메뉴"].pack(fill="both", expand=True)

    def _show_detail(self, item):
        self.main_frame.pack_forget()
        self.detail_frame.show_detail(item)
        self.detail_frame.pack(fill="both", expand=True)

    def _show_toast(self, message):
        Toast(self, message)

    def _add_to_cart(self, item, qty):
        self.cart[item['name']] = self.cart.get(item['name'], 0) + qty
        self._show_toast(f"{item['name']} {qty} added to cart.")
        self._refresh_cart()

    def _on_cart_qty_change(self, item, qty):
        if qty < 1:
            self._on_cart_remove(item)
            return
        self.cart[item['name']] = qty
        self._refresh_cart()

    def _on_cart_remove(self, item):
        if item['name'] in self.cart:
            del self.cart[item['name']]
            self._show_toast(f"{item['name']} removed from cart.")
            self._refresh_cart()

    def _on_search(self):
        # 메인 메뉴(전체메뉴)에서 이름으로 검색 기능 완성
        # "추천" 탭에서 검색 버튼 클릭 시 호출됨
        # self.tabs["추천"]의 search_entry에서 입력값을 받아 전체메뉴에서 이름으로 검색
        search_tab = self.tabs.get("추천")
        menu_tab = self.tabs.get("전체메뉴")
        if not search_tab or not menu_tab:
            return
        keyword = search_tab.search_entry.get().strip()
        if not keyword:
            # 검색어 없으면 전체 메뉴 보여주기
            menu_tab._filtered_menus = menu_tab._all_menus.copy()
        else:
            kw = keyword.lower()
            menu_tab._filtered_menus = [
                item for item in menu_tab._all_menus
                if kw in item['name'].lower()
            ]
        menu_tab._current_page = 0
        menu_tab._draw_menu_list()
        # 전체메뉴 탭으로 전환
        self.tabview.set("전체메뉴")

    def _save_order_to_csv(self):
        order_service = OrderService()
        success = True
        for name, qty in self.cart.items():
            # 주문 실패 시 success = False로
            if not order_service.process_gui_order(name, qty):
                success = False
        return success

    def _on_purchase(self):
        # 구매하기 버튼 클릭 시 주문 정보를 CSV에 저장
        if not self.cart:
            self._show_toast("장바구니가 비어 있습니다.")
            return
        result = self._save_order_to_csv()
        if result:
            self._show_toast("주문이 성공적으로 저장되었습니다!")
            self.cart.clear()
            self._refresh_cart()
        else:
            self._show_toast("주문 저장에 실패했습니다.")

    # 관리자 모드에서 전체메뉴 상품 수정/삭제 콜백
    def _on_menu_edit(self, item):
        self._show_toast(f"'{item['name']}' menu edit feature is not implemented yet.")

    def _on_menu_delete(self, item):
        self._show_toast(f"'{item['name']}' menu delete feature is not implemented yet.")

    def _on_close(self):
        # 안전하게 종료
        try:
            self.destroy()
        except Exception:
            import sys
            sys.exit(0)

    def _show_admin(self):
        # 관리자 모드 진입 시 사용자와 동일한 화면을 보여줌
        self.is_admin = True
        self._show_toast("Entering admin mode.")
        # 탭뷰를 다시 생성하여 어드민 전용 탭만 보이게 함
        # 기존 탭뷰와 탭 프레임들 제거
        self.main_frame.pack_forget()
        self.tabview.destroy()
        self.tabview = ctk.CTkTabview(self.main_frame, width=600)
        self.tabview.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        self.tabs = {}
        self._setup_tabs()
        self._show_main()
        # 앞으로 관리자 전용 기능이 추가될 예정

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception:
        # 예외 발생시 안전하게 종료
        import sys
        sys.exit(0)