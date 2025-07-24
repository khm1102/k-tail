import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class CocktailApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("k-tail Modern GUI")
        self.geometry("900x600")

        menubar = tk.Menu(self)
        cocktail_menu = tk.Menu(menubar, tearoff=False)
        cocktail_menu.add_command(label="칵테일 고르기", command=self.show_select)
        cocktail_menu.add_command(label="추천 및 검색", command=self.show_recommend)
        cocktail_menu.add_command(label="데이터 저장", command=self.show_save)
        cocktail_menu.add_command(label="어드민 관리", command=self.show_admin)
        cocktail_menu.add_command(label="판매 기능", command=self.show_sell)
        cocktail_menu.add_separator()
        cocktail_menu.add_command(label="종료", command=self.quit)
        menubar.add_cascade(label="Cocktail", menu=cocktail_menu)
        view_menu = tk.Menu(menubar, tearoff=False)
        view_menu.add_radiobutton(label="Light Mode",  command=lambda: ctk.set_appearance_mode("light"))
        view_menu.add_radiobutton(label="Dark Mode",   command=lambda: ctk.set_appearance_mode("dark"))
        view_menu.add_radiobutton(label="System Mode", command=lambda: ctk.set_appearance_mode("system"))
        menubar.add_cascade(label="View", menu=view_menu)
        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About k-tail", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

        toolbar = ctk.CTkFrame(self, height=50)
        toolbar.pack(fill="x", padx=20, pady=(10, 0))
        btns = [
            ("칵테일 고르기", self.show_select),
            ("추천 및 검색", self.show_recommend),
            ("데이터 저장", self.show_save),
            ("어드민 관리", self.show_admin),
            ("판매 기능", self.show_sell),
        ]
        for text, cmd in btns:
            btn = ctk.CTkButton(toolbar, text=text, command=cmd)
            btn.pack(side="left", padx=8, pady=8)

        self.content = ctk.CTkFrame(self)
        self.content.pack(fill="both", expand=True, padx=20, pady=20)

        self.frames = {}
        for F in (SelectFrame, RecommendFrame, SaveFrame, AdminFrame, SellFrame):
            frame = F(self.content)
            self.frames[F] = frame
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.status_bar = ctk.CTkLabel(self, text="Ready", fg_color="#E0E0E0", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")

        self.show_select()

    def show_frame(self, frame_class):
        for f in self.frames.values():
            f.lower()
        self.frames[frame_class].lift()
        # 상태바 업데이트
        self.status_bar.configure(text=f"{frame_class.__name__} 활성화")

    def show_select(self):
        self.show_frame(SelectFrame)

    def show_recommend(self):
        self.show_frame(RecommendFrame)

    def show_save(self):
        self.show_frame(SaveFrame)

    def show_admin(self):
        self.show_frame(AdminFrame)

    def show_sell(self):
        self.show_frame(SellFrame)

    def show_about(self):
        messagebox.showinfo(
            title="About k-tail",
            message="k-tail v1.0\nBuilt with CustomTkinter for modern cross-platform GUI"
        )

# ─── 기능별 플레이스홀더 프레임 ───
class BaseFrame(ctk.CTkFrame):
    def __init__(self, parent, title):
        super().__init__(parent)
        header = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=24, weight="bold"))
        header.pack(pady=20)
        placeholder = ctk.CTkLabel(self, text=f"[{title} 화면 구성 중... ]", font=ctk.CTkFont(size=16))
        placeholder.pack(expand=True)

class SelectFrame(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent, "칵테일 선택")

class RecommendFrame(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent, "추천 및 검색")

class SaveFrame(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent, "데이터 저장")

class AdminFrame(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent, "어드민 관리")

class SellFrame(BaseFrame):
    def __init__(self, parent):
        super().__init__(parent, "판매 기능")

if __name__ == "__main__":
    app = CocktailApp()
    app.mainloop()
