import customtkinter as ctk
from tkinter import messagebox

class ThemeSwitcherApp:
    def __init__(self):
        # Инициализация главного окна
        self.app = ctk.CTk()
        self.app.title("Theme Switcher")
        self.app.geometry("500x400")
        
        # Установка начальной темы
        self.current_theme = "dark"
        self.current_color = "blue"
        ctk.set_appearance_mode(self.current_theme)
        ctk.set_default_color_theme(self.current_color)
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Фрейм для кнопок управления
        control_frame = ctk.CTkFrame(self.app)
        control_frame.pack(pady=20, padx=20, fill="x")
        
        # Кнопки переключения темы
        ctk.CTkLabel(control_frame, text="Appearance Mode:").pack(pady=(0, 5))
        
        theme_btn_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        theme_btn_frame.pack()
        
        ctk.CTkButton(
            theme_btn_frame, 
            text="Light", 
            command=lambda: self.switch_theme("light")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            theme_btn_frame, 
            text="Dark", 
            command=lambda: self.switch_theme("dark")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            theme_btn_frame, 
            text="System", 
            command=lambda: self.switch_theme("system")
        ).pack(side="left", padx=5)
        
        # Кнопки переключения цветовой схемы
        ctk.CTkLabel(control_frame, text="Color Theme:").pack(pady=(20, 5))
        
        color_btn_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        color_btn_frame.pack()
        
        colors = ["blue", "green", "dark-blue"]
        for color in colors:
            ctk.CTkButton(
                color_btn_frame, 
                text=color.capitalize(),
                command=lambda c=color: self.switch_color(c)
            ).pack(side="left", padx=5)
        
        # Кнопка для загрузки пользовательской темы
        ctk.CTkButton(
            control_frame,
            text="Load Custom Theme",
            command=self.load_custom_theme
        ).pack(pady=(20, 0))
        
        # Демонстрационные виджеты
        demo_frame = ctk.CTkFrame(self.app)
        demo_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Различные виджеты для демонстрации
        ctk.CTkLabel(demo_frame, text="Widget Examples").pack(pady=10)
        
        ctk.CTkEntry(demo_frame, placeholder_text="Enter something...").pack(pady=5, fill="x")
        
        ctk.CTkButton(demo_frame, text="Sample Button").pack(pady=5)
        
        ctk.CTkCheckBox(demo_frame, text="Checkbox").pack(pady=5)
        
        ctk.CTkSlider(demo_frame).pack(pady=5, fill="x")
        
    def switch_theme(self, theme):
        """Переключение между светлой, темной и системной темами"""
        self.current_theme = theme
        ctk.set_appearance_mode(theme)
        
    def switch_color(self, color):
        """Переключение цветовой схемы"""
        self.current_color = color
        ctk.set_default_color_theme(color)
        
    def load_custom_theme(self):
        """Загрузка пользовательской темы из файла"""
        try:
            # В реальном приложении здесь должен быть диалог выбора файла
            # Для примера просто загружаем нашу тему
            ctk.set_default_color_theme(self.create_custom_theme())
            messagebox.showinfo("Success", "Custom theme loaded!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load theme: {e}")
    
    def create_custom_theme(self):
        """Создание пользовательской темы программно"""
        # В реальном приложении лучше сохранять в JSON файл
        custom_theme = {
            "CustomTkinter": {
                "outer_fg_color": ["#F5F5F5", "#121212"],
                "fg_color": ["#E0E0E0", "#1E1E1E"],
                "hover_color": ["#D0D0D0", "#2E2E2E"],
                "text_color": ["#000000", "#FFFFFF"],
                "button_color": ["#FF6B6B", "#FF2D2D"],
                "button_hover_color": ["#FF8E8E", "#FF5252"],
                "input_fg_color": ["#FFFFFF", "#252525"],
                "input_border_color": ["#B0B0B0", "#454545"],
                "input_text_color": ["#000000", "#FFFFFF"],
                "dropdown_fg_color": ["#FFFFFF", "#252525"],
                "dropdown_hover_color": ["#F0F0F0", "#353535"],
                "dropdown_text_color": ["#000000", "#FFFFFF"],
                "checkbox_fg_color": ["#FF6B6B", "#FF2D2D"],
                "checkbox_hover_color": ["#FF8E8E", "#FF5252"],
                "checkbox_border_color": ["#E0E0E0", "#5D646B"]
            }
        }
        
        # Сохраняем тему во временный файл (в реальном приложении сохраняйте в отдельный файл)
        import tempfile
        import json
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(custom_theme, temp_file)
        temp_file.close()
        
        return temp_file.name
    
    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    app = ThemeSwitcherApp()
    app.run()