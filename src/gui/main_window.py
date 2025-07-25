import customtkinter as ctk
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.services.cocktail_service import CocktailService
from src.services.order_service import OrderService
import random
import csv

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

cocktail_service = CocktailService()
ALL_MENUS = cocktail_service.get_all_cocktails()

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
    def __init__(self, parent, item, fonts, detail_callback=None, cart_callback=None, show_detail_btn=True, show_cart_btn=False, fixed_width=240, fixed_height=220):
        super().__init__(parent, fg_color=CARD_COLOR, corner_radius=8, border_width=1, border_color="#333333")
        self.item = item
        self.fonts = fonts
        self.detail_callback = detail_callback
        self.cart_callback = cart_callback
        self.configure(width=fixed_width, height=fixed_height)
        self.grid_propagate(False)
        ctk.CTkLabel(
            self,
            text=item['name'],
            font=fonts['item'],
            text_color=TEXT_COLOR,
            wraplength=fixed_width-32,
            justify="center"
        ).pack(pady=(12, 4), fill="x")
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
    def __init__(self, parent, item, qty, fonts, on_qty_change, on_remove, req_text=None, on_req_change=None):
        super().__init__(parent, fg_color=CARD_COLOR, corner_radius=8, border_width=1, border_color="#333333")
        self.item = item
        self.fonts = fonts
        self.on_qty_change = on_qty_change
        self.on_remove = on_remove
        self.qty = ctk.IntVar(value=qty)
        self.on_req_change = on_req_change

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

        # 삭제 버튼 아래에 요구사항 입력란 추가
        self.req_text = ctk.StringVar(value=req_text if req_text is not None else "")
        req_label = ctk.CTkLabel(self, text="요구사항", font=fonts['small'], text_color=ACCENT_COLOR, anchor="w")
        req_label.grid(row=1, column=0, sticky="w", padx=(16,0), pady=(0,2), columnspan=2)
        self.req_entry = ctk.CTkTextbox(self, height=36, font=fonts['small'])
        self.req_entry.insert("1.0", self.req_text.get())
        self.req_entry.grid(row=2, column=0, columnspan=5, sticky="ew", padx=(16,8), pady=(0,8))
        self.req_entry.bind("<KeyRelease>", self._on_req_change)

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

    def _on_req_change(self, event=None):
        text = self.req_entry.get("1.0", "end").strip()
        self.req_text.set(text)
        if self.on_req_change:
            self.on_req_change(self.item, text)

# --- 장바구니 탭 (수정된 부분) ---
class CartListTab(ctk.CTkFrame):
    def __init__(self, parent, fonts, cart, on_qty_change=None, on_remove=None, on_purchase=None, reqs=None, on_req_change=None, padding=PADDING):
        super().__init__(parent, fg_color=BG_COLOR)
        self.fonts = fonts
        self.cart = cart
        self.padding = padding
        self.on_qty_change = on_qty_change
        self.on_remove = on_remove
        self.on_purchase = on_purchase
        self.reqs = reqs if reqs is not None else {}
        self.on_req_change = on_req_change

        # 내부 스크롤 프레임
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=BG_COLOR)
        self.scroll_frame.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        # 총합 가격 라벨
        self.total_label = ctk.CTkLabel(self, text="", font=self.fonts['head'], text_color=ACCENT_COLOR, anchor="e")
        self.total_label.pack(fill="x", padx=(0, 24), pady=(8, 0), side="top", anchor="e")

        # 구매하기 버튼 프레임
        self.button_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.button_frame.pack(fill="x", side="bottom", padx=0, pady=(0, 8), anchor="se")

        # 구매하기 버튼 hover_color 강조
        self.purchase_btn = ctk.CTkButton(
            self.button_frame,
            text="구매하기",
            fg_color=ACCENT_COLOR,
            hover_color=SUCCESS_COLOR,  # hover 시 초록
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
            req_text = self.reqs.get(name, "")
            row_frame = CartListItem(
                self.scroll_frame,
                item,
                qty,
                self.fonts,
                on_qty_change=self.on_qty_change if self.on_qty_change else lambda i, q: None,
                on_remove=self.on_remove if self.on_remove else lambda i: None,
                req_text=req_text,
                on_req_change=self.on_req_change if self.on_req_change else None
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
        self._add_fab()

    def _build(self):
        all_menus = ALL_MENUS.copy()
        random.shuffle(all_menus)
        popular_menus = random.sample(all_menus, min(6, len(all_menus)))
        random.shuffle(all_menus)
        expert_menus = random.sample(all_menus, min(6, len(all_menus)))
        section_configs = [
            ("금주 인기 메뉴", popular_menus, 280),
            ("전문가 추천", expert_menus, 280),
        ]
        for idx, (title, seq, height) in enumerate(section_configs):
            ctk.CTkLabel(self, text=title, font=self.fonts['head']).pack(anchor="w", padx=PADDING, pady=(10, 4))
            pady = (0, PADDING) if idx < len(section_configs)-1 else (0, 0)
            sec = ctk.CTkScrollableFrame(self, height=height, fg_color=BG_COLOR, border_width=0)
            sec.pack(fill="x", padx=PADDING, pady=pady)
            columns = 3
            for i, item in enumerate(seq):
                row, col = divmod(i, columns)
                card = MenuCard(sec, item, self.fonts, detail_callback=None, cart_callback=self.cart_callback, show_detail_btn=True, show_cart_btn=False, fixed_width=240, fixed_height=220)
                card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            for c in range(columns):
                sec.grid_columnconfigure(c, weight=1)

    def _add_fab(self):
        # 플로팅 버튼(우측 하단)
        fab = ctk.CTkButton(
            self,
            text="💬",
            width=56,
            height=56,
            fg_color=ACCENT_COLOR,
            text_color="#fff",
            font=ctk.CTkFont(size=28, weight="bold"),
            corner_radius=28,
            hover_color="#6eaaff",  # 더 밝은 파랑
            border_width=2,
            border_color="#fff",
            command=self._on_fab_click
        )
        fab.place(relx=1.0, rely=1.0, anchor="se", x=-24, y=-24)

    def _on_fab_click(self):
        self._show_fadein_toast("무엇을 도와드릴까요?", next_callback=self._show_helper_popup)

    def _show_fadein_toast(self, message, duration=1000, next_callback=None):
        # 하단 중앙에 페이드인/아웃 토스트
        toast = ctk.CTkToplevel(self)
        toast.overrideredirect(True)
        toast.attributes('-topmost', True)
        toast.configure(bg=BG_COLOR)
        w, h = 340, 60
        self.update_idletasks()
        px = self.winfo_rootx()
        py = self.winfo_rooty()
        pw = self.winfo_width()
        ph = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + ph - h - 48
        toast.geometry(f"{w}x{h}+{x}+{y}")
        frame = ctk.CTkFrame(toast, fg_color=CARD_COLOR, corner_radius=12, border_width=0)
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.98, relheight=0.92)
        ctk.CTkLabel(
            frame,
            text=message,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="transparent",
            text_color=ACCENT_COLOR,
            anchor="center",
            wraplength=w-40,
            justify="center"
        ).pack(expand=True, fill="both", padx=12, pady=8)
        # 페이드인
        def fade_in(step=0):
            alpha = min(1.0, step / 8)
            toast.attributes("-alpha", alpha)
            if alpha < 1.0:
                toast.after(20, fade_in, step + 1)
            else:
                toast.after(duration, fade_out)
        def fade_out(step=8):
            alpha = max(0.0, step / 8)
            toast.attributes("-alpha", alpha)
            if alpha > 0.0:
                toast.after(20, fade_out, step - 1)
            else:
                toast.destroy()
                if next_callback:
                    self.after(100, next_callback)
        toast.attributes("-alpha", 0.0)
        fade_in()

    def _show_helper_popup(self):
        # 하단 중앙에 페이드인 팝업 + 버튼 2개
        popup = ctk.CTkToplevel(self)
        popup.overrideredirect(True)
        popup.attributes('-topmost', True)
        popup.configure(bg=BG_COLOR)
        w, h = 360, 120
        self.update_idletasks()
        px = self.winfo_rootx()
        py = self.winfo_rooty()
        pw = self.winfo_width()
        ph = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + ph - h - 48
        popup.geometry(f"{w}x{h}+{x}+{y}")
        frame = ctk.CTkFrame(popup, fg_color=CARD_COLOR, corner_radius=12, border_width=0)
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.98, relheight=0.92)
        ctk.CTkLabel(
            frame,
            text="원하시는 칵테일을 찾아드릴까요?",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="transparent",
            text_color=ACCENT_COLOR,
            anchor="center",
            wraplength=w-40,
            justify="center"
        ).pack(pady=(14, 2), padx=12)
        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.pack(pady=(2, 10))
        def on_yes():
            popup.destroy()
            app = self.winfo_toplevel()
            if hasattr(app, 'tabview'):
                try:
                    app.tabview.set("추천")
                except Exception:
                    pass
        def on_no():
            popup.destroy()
            app = self.winfo_toplevel()
            if hasattr(app, '_show_toast'):
                app._show_toast("언제든 불러주세요!")
        ctk.CTkButton(btns, text="Yes", fg_color=ACCENT_COLOR, corner_radius=6, width=100, command=on_yes).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="No", fg_color="#444444", corner_radius=6, width=100, command=on_no).pack(side="left", padx=8)
        # 페이드인 애니메이션
        def fade_in(step=0):
            alpha = min(1.0, step / 8)
            popup.attributes("-alpha", alpha)
            if alpha < 1.0:
                popup.after(20, fade_in, step + 1)
        popup.attributes("-alpha", 0.0)
        fade_in()

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

        if self.admin_mode:
            # 관리자 모드: 이름 | 가격 | 수정/삭제
            self.columnconfigure(0, weight=3, minsize=180)
            self.columnconfigure(1, weight=1, minsize=80)
            self.columnconfigure(2, weight=0, minsize=100)
            # 이름
            left = ctk.CTkFrame(self, fg_color="transparent")
            left.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=8)
            name_label = ctk.CTkLabel(left, text=item['name'], font=fonts['item'], text_color=TEXT_COLOR, anchor="w")
            name_label.pack(anchor="w")
            # 가격
            price_lbl = ctk.CTkLabel(self, text=item['price'], font=fonts['item'], text_color=ACCENT_COLOR, width=90, anchor="center")
            price_lbl.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
            # 수정/삭제 버튼
            btns = ctk.CTkFrame(self, fg_color="transparent")
            btns.grid(row=0, column=2, sticky="e", padx=(0, 8), pady=8)
            ctk.CTkButton(
                btns,
                text="수정",
                fg_color=ACCENT_COLOR,
                corner_radius=6,
                width=48,
                font=fonts['small'],
                command=self._open_edit_dialog
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                btns,
                text="삭제",
                fg_color=ERROR_COLOR,
                text_color="#fff",
                corner_radius=6,
                width=48,
                font=fonts['small'],
                command=self._open_delete_dialog
            ).pack(side="left", padx=2)
        else:
            # 일반 유저: 이름 | 가격 | 수량/장바구니 | 툴팁
            self.columnconfigure(0, weight=3, minsize=180)
            self.columnconfigure(1, weight=1, minsize=80)
            self.columnconfigure(2, weight=2, minsize=180)
            self.columnconfigure(3, weight=0, minsize=36)
            # 이름
            left = ctk.CTkFrame(self, fg_color="transparent")
            left.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=8)
            name_label = ctk.CTkLabel(left, text=item['name'], font=fonts['item'], text_color=TEXT_COLOR, anchor="w")
            name_label.pack(anchor="w")
            # 가격
            price_lbl = ctk.CTkLabel(self, text=item['price'], font=fonts['item'], text_color=ACCENT_COLOR, width=90, anchor="center")
            price_lbl.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
            # 수량/장바구니
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
            # 툴팁
            tooltip_btn = ctk.CTkButton(
                self,
                text="ⓘ",
                width=26,
                height=26,
                fg_color="#444444",
                text_color="#cccccc",
                font=ctk.CTkFont(size=20, weight="bold"),
                corner_radius=13,
                hover_color="#666666",
                command=None
            )
            tooltip_btn.grid(row=0, column=3, sticky="e", padx=(0, 8), pady=8)
            ingredients = item.get('ingredients', '') or item.get('desc', '') or item.get('garnish', '')
            self._tooltip = Tooltip(tooltip_btn, ingredients)
            def on_enter(event):
                x = tooltip_btn.winfo_rootx() + tooltip_btn.winfo_width() + 4
                y = tooltip_btn.winfo_rooty()
                self._tooltip.show(x, y)
            def on_leave(event):
                self._tooltip.hide()
            tooltip_btn.bind("<Enter>", on_enter)
            tooltip_btn.bind("<Leave>", on_leave)

    def _open_edit_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("메뉴 수정")
        dialog.geometry("420x340")
        dialog.grab_set()
        dialog.configure(bg=BG_COLOR)
        dialog.resizable(False, False)
        ctk.CTkLabel(dialog, text="메뉴 수정", font=ctk.CTkFont(size=18, weight="bold"), text_color=ACCENT_COLOR).pack(pady=(24, 4))
        form = ctk.CTkFrame(dialog, fg_color=CARD_COLOR, corner_radius=10)
        form.pack(fill="x", padx=24, pady=(8, 16))
        # 이름
        ctk.CTkLabel(form, text="이름", font=self.fonts['item'], text_color=TEXT_COLOR, anchor="w").pack(anchor="w", padx=16, pady=(12, 2))
        name_var = ctk.StringVar(value=self.item['name'])
        name_entry = ctk.CTkEntry(form, textvariable=name_var, font=self.fonts['item'])
        name_entry.pack(fill="x", padx=16, pady=(0, 8))
        # 가격
        ctk.CTkLabel(form, text="가격", font=self.fonts['item'], text_color=TEXT_COLOR, anchor="w").pack(anchor="w", padx=16, pady=(2, 2))
        price_var = ctk.StringVar(value=self.item['price'])
        price_entry = ctk.CTkEntry(form, textvariable=price_var, font=self.fonts['item'])
        price_entry.pack(fill="x", padx=16, pady=(0, 8))
        # 설명
        ctk.CTkLabel(form, text="설명", font=self.fonts['item'], text_color=TEXT_COLOR, anchor="w").pack(anchor="w", padx=16, pady=(2, 2))
        desc_var = ctk.StringVar(value=self.item.get('desc', ''))
        desc_entry = ctk.CTkEntry(form, textvariable=desc_var, font=self.fonts['item'])
        desc_entry.pack(fill="x", padx=16, pady=(0, 12))
        # 저장 버튼
        def save():
            updated = dict(self.item)
            updated['name'] = name_var.get()
            updated['price'] = price_var.get()
            updated['desc'] = desc_var.get()
            dialog.destroy()
            if self.on_edit:
                self.on_edit(updated)
        ctk.CTkButton(form, text="저장", fg_color=ACCENT_COLOR, corner_radius=6, font=self.fonts['item'], command=save).pack(pady=(8, 0))
        # 닫기 버튼
        ctk.CTkButton(dialog, text="닫기", fg_color="#444444", corner_radius=6, width=80, font=ctk.CTkFont(size=13), command=dialog.destroy).pack(pady=(8, 0))

    def _open_delete_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("삭제 확인")
        dialog.geometry("340x180")
        dialog.grab_set()
        dialog.configure(bg=BG_COLOR)
        dialog.resizable(False, False)
        ctk.CTkLabel(dialog, text="정말로 이 메뉴를 삭제하시겠습니까?", font=ctk.CTkFont(size=15, weight="bold"), text_color=ERROR_COLOR, wraplength=300, anchor="center", justify="center").pack(pady=(28, 8), padx=16)
        ctk.CTkLabel(dialog, text=f"'{self.item['name']}'", font=ctk.CTkFont(size=14), text_color=ACCENT_COLOR).pack(pady=(0, 12))
        btns = ctk.CTkFrame(dialog, fg_color="transparent")
        btns.pack(pady=8)
        def really_delete():
            dialog.destroy()
            if self.on_delete:
                self.on_delete(self.item)
        ctk.CTkButton(btns, text="삭제", fg_color=ERROR_COLOR, text_color="#fff", corner_radius=6, width=100, command=really_delete).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="취소", fg_color="#444444", corner_radius=6, width=100, command=dialog.destroy).pack(side="left", padx=8)

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
        self._all_menus = cocktail_service.get_all_cocktails()
        self._filtered_menus = self._all_menus.copy()
        self._current_page = 0
        # PAGE_SIZE is always 10 now
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
            width=320,
            border_width=2,
            border_color=ACCENT_COLOR
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            search_frame,
            text="검색",
            fg_color=ACCENT_COLOR,
            hover_color="#6eaaff",
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
        if self.admin_mode:
            self._draw_admin_request_dropdowns()

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

    def _draw_admin_request_dropdowns(self):
        # orders.csv에서 주문 시간별로 묶어서 읽기
        orders = self._load_orders_grouped()
        outer = ctk.CTkScrollableFrame(self, fg_color=CARD_COLOR, corner_radius=12, border_width=0, height=320)
        outer.pack(fill="x", padx=32, pady=(0, 24))
        ctk.CTkLabel(outer, text="주문 요청사항 목록", font=self.fonts['head'], text_color=ACCENT_COLOR, anchor="w").pack(anchor="w", padx=16, pady=(16, 8))
        for idx, (order_time, cocktails) in enumerate(orders, 1):
            OrderDropdownCard(outer, {"order_id": idx, "order_time": order_time, "cocktails": cocktails}, self.fonts).pack(fill="x", padx=12, pady=6)

    def _load_orders_grouped(self):
        # orders.csv에서 [order_time, name] + --재료/레시피/요구사항 읽어서 주문 시간별로 묶음
        import os
        orders_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "orders.csv")
        grouped = {}
        if not os.path.exists(orders_path):
            return []
        with open(orders_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            current_time = None
            current_name = None
            current_quantity = None
            current_ingredients = []
            current_recipe = []
            current_request = ""
            orders = []
            for row in reader:
                if not row:
                    continue
                if not row[0].startswith("--"):  # 주문 헤더(시간, 칵테일명, 수량)
                    # 이전 주문 저장
                    if current_time and current_name:
                        orders.append((current_time, [{
                            "cocktail": current_name,
                            "quantity": current_quantity,
                            "ingredients": ", ".join(current_ingredients),
                            "recipe": "\n".join(current_recipe),
                            "request": current_request
                        }]))
                    # 새 주문 시작
                    current_time = row[0]
                    current_name = row[1] if len(row) > 1 else ""
                    current_quantity = row[2] if len(row) > 2 else "1"
                    current_ingredients = []
                    current_recipe = []
                    current_request = ""
                else:
                    content = row[0][2:].strip()
                    if content.startswith("요구사항:"):
                        current_request = content.replace("요구사항:", "").strip()
                    elif any(word in content for word in ["oz", "bsp", "dash", "ml", "L", "piece", "float", "wheel", "wedge", "slice", "cup", "syrup", "juice", "bitters", "liqueur", "gin", "rum", "vodka", "whiskey", "tequila", "wine", "beer", "sugar", "lemon", "lime", "orange", "pineapple", "mint", "ice", "water", "soda", "cream", "egg", "honey", "salt", "pepper", "rosemary", "cherry", "apple", "grapefruit", "cinnamon", "vanilla", "coffee", "cocoa", "chocolate", "strawberry", "blueberry", "raspberry", "blackberry", "apricot", "pear", "peach", "melon", "banana", "passion", "apricot", "apricot", "apricot"]):
                        current_ingredients.append(content)
                    else:
                        current_recipe.append(content)
            # 마지막 주문 저장
            if current_time and current_name:
                orders.append((current_time, [{
                    "cocktail": current_name,
                    "quantity": current_quantity,
                    "ingredients": ", ".join(current_ingredients),
                    "recipe": "\n".join(current_recipe),
                    "request": current_request
                }]))
        # 최신 주문이 위로 오도록 정렬
        return sorted(orders, key=lambda x: x[0], reverse=True)

class OrderDropdownCard(ctk.CTkFrame):
    def __init__(self, parent, order, fonts):
        super().__init__(parent, fg_color="#23232a", corner_radius=8, border_width=0)
        self.order = order
        self.fonts = fonts
        self.expanded = False
        self.inner = None
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=0, pady=0)
        self.toggle_btn = ctk.CTkButton(
            top,
            text=f"주문 {self.order['order_id']} ({self.order['order_time']}) ▼",
            font=self.fonts['item'],
            fg_color=ACCENT_COLOR,
            corner_radius=6,
            width=1,
            command=self._toggle
        )
        self.toggle_btn.pack(fill="x", padx=(0, 0), pady=8)

    def _toggle(self):
        if self.expanded:
            if self.inner:
                self.inner.destroy()
            self.toggle_btn.configure(text=f"주문 {self.order['order_id']} ({self.order['order_time']}) ▼")
            self.expanded = False
        else:
            self.inner = ctk.CTkFrame(self, fg_color="#23232a")
            self.inner.pack(fill="x", padx=8, pady=(0, 8))
            for c in self.order['cocktails']:
                DropdownRequestCard(self.inner, c, self.fonts).pack(fill="x", padx=0, pady=4)
            self.toggle_btn.configure(text=f"주문 {self.order['order_id']} ({self.order['order_time']}) ▲")
            self.expanded = True

class DropdownRequestCard(ctk.CTkFrame):
    def __init__(self, parent, req, fonts):
        super().__init__(parent, fg_color="#23232a", corner_radius=8, border_width=0)
        self.req = req
        self.fonts = fonts
        self._build()

    def _build(self):
        # 펼침 없이 항상 보이게 (OrderDropdownCard에서만 드롭다운)
        qty_str = f" (수량: {self.req.get('quantity', '1')})" if self.req.get('quantity') else ""
        ctk.CTkLabel(self, text=f"{self.req['cocktail']}{qty_str}", font=self.fonts['item'], text_color=ACCENT_COLOR, anchor="w").pack(anchor="w", padx=8, pady=(4, 2))
        ctk.CTkLabel(self, text=f"재료: {self.req['ingredients']}", font=self.fonts['item'], text_color=TEXT_COLOR, anchor="w", wraplength=440, justify="left").pack(anchor="w", padx=8, pady=(0, 2))
        ctk.CTkLabel(self, text=f"요청사항: {self.req['request']}", font=self.fonts['item'], text_color=ACCENT_COLOR, anchor="w", wraplength=440, justify="left").pack(anchor="w", padx=8, pady=(0, 8))

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
        self.fonts = {
            'head': ctk.CTkFont(size=18, weight="bold"),
            'item': ctk.CTkFont(size=14),
            'small': ctk.CTkFont(size=12)
        }
        self.title("k-tail")
        self.geometry("640x840")
        self.configure(fg_color=BG_COLOR)
        self.cart = {}
        self.cart_reqs = {}  # 제품별 요구사항 저장

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.is_admin = False  # 관리자 모드 여부

        self.start_frame  = StartFrame(self, self.fonts, self._show_main, self._show_admin)
        self.main_frame   = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.detail_frame = DetailFrame(self, self.fonts, self._show_main)

        # 탭뷰 스타일 강조
        self.tabview = ctk.CTkTabview(
            self.main_frame,
            width=600,
            corner_radius=12,
            fg_color=BG_COLOR,
            segmented_button_fg_color="#444444",  # 테두리도 회색
            segmented_button_selected_color="#444444",  # 회색
            segmented_button_unselected_color="#222",
            segmented_button_selected_hover_color="#444444",  # 회색
            segmented_button_unselected_hover_color="#333"
        )
        self.tabview.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        self.tabs = {}
        self._setup_tabs()

        self.start_frame.pack(fill="both", expand=True)

    def _setup_tabs(self):
        # 어드민 모드일 때는 추천, 검색, 장바구니, 요청사항 탭을 안보이게 한다
        if self.is_admin:
            tab_names = ["전체메뉴"]
        else:
            tab_names = ["인기", "추천", "전체메뉴", "장바구니"]
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
        if not self.is_admin:
            self.tabs["장바구니"] = CartListTab(
                self.tabview.tab("장바구니"),
                self.fonts,
                self.cart,
                on_qty_change=self._on_cart_qty_change,
                on_remove=self._on_cart_remove,
                on_purchase=self._on_purchase,
                reqs=self.cart_reqs,
                on_req_change=self._on_cart_req_change
            )
            self.tabs["장바구니"].pack(fill="both", expand=True, padx=PADDING, pady=PADDING)

    def _refresh_cart(self):
        self.tabs["장바구니"].cart = self.cart
        self.tabs["장바구니"].reqs = self.cart_reqs
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

    def _on_cart_req_change(self, item, req_text):
        self.cart_reqs[item['name']] = req_text

    def _on_cart_remove(self, item):
        if item['name'] in self.cart:
            del self.cart[item['name']]
            if item['name'] in self.cart_reqs:
                del self.cart_reqs[item['name']]
            self._show_toast(f"{item['name']} removed from cart.")
            self._refresh_cart()

    def _on_search(self):
        search_tab = self.tabs.get("추천")
        menu_tab = self.tabs.get("전체메뉴")
        current_tab = self.tabview.get()
        if current_tab == "추천":
            if not search_tab:
                return
            keyword = search_tab.search_entry.get().strip()
            # 추천 결과 리스트 초기화
            for w in search_tab.result_list.winfo_children():
                w.destroy()
            from src.services.cocktail_service import CocktailService
            service = CocktailService()
            results = service.recommend_by_taste_ingredients(keyword, top_n=5)
            if not results:
                ctk.CTkLabel(search_tab.result_list, text="추천 결과가 없습니다.", font=self.fonts['item'], text_color=ERROR_COLOR).pack(pady=20)
                return
            for idx, item in enumerate(results, 1):
                card = ctk.CTkFrame(search_tab.result_list, fg_color=CARD_COLOR, corner_radius=10, border_width=1, border_color="#333")
                card.pack(fill="x", padx=12, pady=8)
                ctk.CTkLabel(card, text=f"{idx}. 유사도: {item.get('similarity_score', 0):.3f}", font=self.fonts['small'], text_color=ACCENT_COLOR, anchor="w").pack(anchor="w", padx=8, pady=(8,2))
                ctk.CTkLabel(card, text=f"칵테일명: {item.get('name','')}", font=self.fonts['item'], text_color=TEXT_COLOR, anchor="w").pack(anchor="w", padx=8, pady=2)
                ctk.CTkLabel(card, text=f"재료: {item.get('ingredients','')}", font=self.fonts['item'], text_color="#bbbbbb", anchor="w", wraplength=420, justify="left").pack(anchor="w", padx=8, pady=2)
                ctk.CTkLabel(card, text=f"일치 검색어: {' '.join(item.get('matching_keywords', []))}", font=self.fonts['small'], text_color=ACCENT_COLOR, anchor="w").pack(anchor="w", padx=8, pady=2)
                ctk.CTkLabel(card, text=f"가격: {item.get('price','')}", font=self.fonts['item'], text_color=ACCENT_COLOR, anchor="w").pack(anchor="w", padx=8, pady=(2,8))
        elif current_tab == "전체메뉴":
            if not menu_tab:
                return
            keyword = menu_tab._search_var.get().strip()
            if not keyword:
                menu_tab._filtered_menus = menu_tab._all_menus.copy()
            else:
                kw = keyword.lower()
                menu_tab._filtered_menus = [
                    item for item in menu_tab._all_menus
                    if kw in item['name'].lower()
                ]
            menu_tab._current_page = 0
            menu_tab._draw_menu_list()
            # 전체메뉴 탭에서만 탭 전환
            self.tabview.set("전체메뉴")

        # 추천 탭에서 검색 시 추천 결과 출력
        if self.tabview.get() == "추천":
            # 추천 결과 리스트 초기화
            for w in search_tab.result_list.winfo_children():
                w.destroy()
            from src.services.cocktail_service import CocktailService
            service = CocktailService()
            results = service.recommend_by_taste_ingredients(keyword, top_n=5)
            if not results:
                ctk.CTkLabel(search_tab.result_list, text="추천 결과가 없습니다.", font=self.fonts['item'], text_color=ERROR_COLOR).pack(pady=20)
                return
            for idx, item in enumerate(results, 1):
                card = ctk.CTkFrame(search_tab.result_list, fg_color=CARD_COLOR, corner_radius=10, border_width=1, border_color="#333")
                card.pack(fill="x", padx=12, pady=8)
                ctk.CTkLabel(card, text=f"{idx}. 유사도: {item.get('similarity_score', 0):.3f}", font=self.fonts['small'], text_color=ACCENT_COLOR, anchor="w").pack(anchor="w", padx=8, pady=(8,2))
                ctk.CTkLabel(card, text=f"칵테일명: {item.get('name','')}", font=self.fonts['item'], text_color=TEXT_COLOR, anchor="w").pack(anchor="w", padx=8, pady=2)
                ctk.CTkLabel(card, text=f"재료: {item.get('ingredients','')}", font=self.fonts['item'], text_color="#bbbbbb", anchor="w", wraplength=420, justify="left").pack(anchor="w", padx=8, pady=2)
                ctk.CTkLabel(card, text=f"일치 검색어: {' '.join(item.get('matching_keywords', []))}", font=self.fonts['small'], text_color=ACCENT_COLOR, anchor="w").pack(anchor="w", padx=8, pady=2)
                ctk.CTkLabel(card, text=f"가격: {item.get('price','')}", font=self.fonts['item'], text_color=ACCENT_COLOR, anchor="w").pack(anchor="w", padx=8, pady=(2,8))

    def _save_order_to_csv(self):
        order_service = OrderService()
        success = True
        # 주문 시간 한 번만 생성
        from datetime import datetime
        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for name, qty in self.cart.items():
            req = self.cart_reqs.get(name, "")
            # 주문 시간(order_time)을 전달
            if not order_service.process_gui_order(name, qty, req, order_time=order_time):
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
            self.cart_reqs.clear()
            self._refresh_cart()
        else:
            self._show_toast("주문 저장에 실패했습니다.")

    # 관리자 모드에서 전체메뉴 상품 수정/삭제 콜백
    def _on_menu_edit(self, item):
        # 실제 DB 수정
        try:
            from src.db.cocktail import coctail_update
            name = item['name']
            price = None
            desc = None
            if 'price' in item:
                # '$12.00' → 12.0
                price = float(str(item['price']).replace('$','').replace(',',''))
            if 'desc' in item:
                desc = item['desc']
            ok = coctail_update(name, price=price, note=desc)
            if ok:
                self._show_toast(f"'{name}' 메뉴가 수정되었습니다.")
                self.tabs["전체메뉴"]._all_menus = self.tabs["전체메뉴"]._filtered_menus = self.tabs["전체메뉴"].cocktail_service.get_all_cocktails()
                self.tabs["전체메뉴"]._draw_menu_list()
            else:
                self._show_toast(f"'{name}' 메뉴 수정 실패.")
        except Exception as e:
            self._show_toast(f"수정 오류: {e}")

    def _on_menu_delete(self, item):
        # 실제 DB 삭제
        try:
            from src.db.cocktail import coctail_delete
            name = item['name']
            ok = coctail_delete(name)
            if ok:
                self._show_toast(f"'{name}' 메뉴가 삭제되었습니다.")
                self.tabs["전체메뉴"]._all_menus = self.tabs["전체메뉴"]._filtered_menus = self.tabs["전체메뉴"].cocktail_service.get_all_cocktails()
                self.tabs["전체메뉴"]._draw_menu_list()
            else:
                self._show_toast(f"'{name}' 메뉴 삭제 실패.")
        except Exception as e:
            self._show_toast(f"삭제 오류: {e}")

    def _on_close(self):
        # 안전하게 종료
        try:
            self.destroy()
        except Exception:
            import sys
            sys.exit(0)

    def _show_admin(self):
        # 관리자 모드 진입 시 인증 팝업
        self._show_admin_login_popup()

    def _show_admin_login_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("관리자 로그인")
        popup.geometry("400x320")
        popup.resizable(False, False)
        popup.grab_set()
        popup.configure(bg=BG_COLOR)
        popup.focus_force()
        # 상단 아이콘과 타이틀
        icon_label = ctk.CTkLabel(popup, text="🛡️", font=ctk.CTkFont(size=38), text_color=ACCENT_COLOR)
        icon_label.pack(pady=(18, 0))
        ctk.CTkLabel(popup, text="관리자 로그인", font=ctk.CTkFont(size=22, weight="bold"), text_color=ACCENT_COLOR).pack(pady=(2, 10))
        form = ctk.CTkFrame(popup, fg_color=CARD_COLOR, corner_radius=18, border_width=0)
        form.pack(fill="both", expand=True, padx=32, pady=(0, 18))
        # 이름
        ctk.CTkLabel(form, text="아이디", font=self.fonts['item'], text_color=TEXT_COLOR, anchor="w").pack(anchor="w", padx=18, pady=(18, 2))
        name_var = ctk.StringVar()
        name_entry = ctk.CTkEntry(form, textvariable=name_var, font=self.fonts['item'], placeholder_text="아이디를 입력하세요", corner_radius=10, border_width=2)
        name_entry.pack(fill="x", padx=18, pady=(0, 10))
        name_entry.focus_set()
        # 비밀번호
        ctk.CTkLabel(form, text="비밀번호", font=self.fonts['item'], text_color=TEXT_COLOR, anchor="w").pack(anchor="w", padx=18, pady=(2, 2))
        passwd_var = ctk.StringVar()
        passwd_entry = ctk.CTkEntry(form, textvariable=passwd_var, font=self.fonts['item'], show="*", placeholder_text="비밀번호를 입력하세요", corner_radius=10, border_width=2)
        passwd_entry.pack(fill="x", padx=18, pady=(0, 18))
        # 엔터키로 로그인 시도
        passwd_entry.bind("<Return>", lambda event: try_login())
        name_entry.bind("<Return>", lambda event: try_login())
        # 실패 안내 라벨
        fail_label = ctk.CTkLabel(form, text="", font=self.fonts['small'], text_color=ERROR_COLOR)
        fail_label.pack(pady=(0, 2))
        # 버튼 영역 (form 바깥, 팝업 맨 아래)
        btns = ctk.CTkFrame(popup, fg_color="transparent")
        btns.pack(side="bottom", fill="x", pady=(10, 18))
        def try_login():
            from src.db.admin import verify_admin
            name = name_var.get().strip()
            passwd = passwd_var.get().strip()
            if not name or not passwd:
                fail_label.configure(text="아이디와 비밀번호를 모두 입력하세요.")
                name_entry.configure(border_color=ERROR_COLOR)
                passwd_entry.configure(border_color=ERROR_COLOR)
                return
            if verify_admin(name, passwd):
                popup.destroy()
                self.is_admin = True
                self._show_toast("관리자 인증 성공! 관리자 모드로 진입합니다.")
                self.main_frame.pack_forget()
                self.tabview.destroy()
                self.tabview = ctk.CTkTabview(
                    self.main_frame,
                    width=600,
                    corner_radius=12,
                    fg_color=BG_COLOR,
                    segmented_button_fg_color="#444444",
                    segmented_button_selected_color="#444444",
                    segmented_button_unselected_color="#222",
                    segmented_button_selected_hover_color="#444444",
                    segmented_button_unselected_hover_color="#333"
                )
                self.tabview.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
                self.tabs = {}
                self._setup_tabs()
                self._show_main()
            else:
                fail_label.configure(text="로그인 실패: 아이디 또는 비밀번호가 올바르지 않습니다.")
                name_entry.configure(border_color=ERROR_COLOR)
                passwd_entry.configure(border_color=ERROR_COLOR)

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception:
        # 예외 발생시 안전하게 종료
        import sys
        sys.exit(0)