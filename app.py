import customtkinter


class ToplevelWindow(customtkinter.CTkToplevel):
    """Окно настройки определённой игры"""
    def __init__(self):
        super().__init__()
        self.geometry("400x300")

        self.label = customtkinter.CTkLabel(self, text="Настройки")
        self.label.pack(padx=20, pady=20)

class GameFrame(customtkinter.CTkFrame):
    """Блок, который будет создаваться для каждой игры пользователя"""
    def __init__(self, master, name, date):
        super().__init__(master)

        # Название игры
        self.label_name = customtkinter.CTkLabel(self, text=name)
        self.label_name.grid(row=0, column=0)

        # Отображение последней даты запуска игры
        self.label_name = customtkinter.CTkLabel(self, text=f"Последняя дата запуска: {date}")
        self.label_name.grid(row=1, column=0)

        # Заход в настройки каждого приложения
        self.game_resave_settings = customtkinter.CTkButton(self, text="Настройки", command=self.button_callbck)
        self.game_resave_settings.grid(row=0, column=1)

        self.toplevel_window = None

    def button_callbck(self):
        """Заход в меню настроек определённой игры"""
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self) 
        else:
            self.toplevel_window.focus()

class SettingsFrame(customtkinter.CTkFrame):
    def __init__(self, master, name):
        super().__init__(master)

        self.label = customtkinter.CTkLabel(self, text=name)
        self.label.grid(row=0, column=0, sticky="nsew")

        self.label = customtkinter.CTkLabel(self, text="Тема приложения:")
        self.label.grid(row=0, column=0, sticky="nsew")

class SettingsFrameForGame(customtkinter.CTkFrame):
    def __init__(self, master, name):
        super().__init__(master)

        self.label = customtkinter.CTkLabel(self, text=name)
        self.label.grid(row=0, column=0, sticky="nsew")

        self.label = customtkinter.CTkLabel(self, text="Тема приложения:")
        self.label.grid(row=0, column=0, sticky="nsew")

class Settings(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x150")
        self.title("Settings")

        self.label = customtkinter.CTkLabel(self, text="Тема приложения:")
        self.label.grid(row=0, column=0, sticky="nsew")

        self.button_confirn = customtkinter.CTkButton(self, text="Confirm", command=self.button_callbck)
        self.button_confirn.grid(row=3, column=0)

    def button_callbck(self):
        self.destroy()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x150")
        self.title("ReSave Manager")

        # test
        self.games_frame = GameFrame(self, name="REPO", date="5 июня")
        self.games_frame.grid(row=1, column=0, sticky="nsew")

        self.label_of_app = customtkinter.CTkLabel(self, text="List of your games:")
        self.label_of_app.grid(row=0, column=0)
        self.button_settings = customtkinter.CTkButton(self, text="Settings", command=self.button_callbck)
        self.button_settings.grid(row=0, column=1, sticky="nsew")

    def button_callbck(self):
        self.settings_app = Settings()
        self.settings_app.mainloop()

        



app = App()
app.mainloop()