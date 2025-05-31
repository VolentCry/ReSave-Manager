import customtkinter
import time
import subprocess
import shutil



# Данные пользователя
games = [["Elden Ring", "5 Май 2025 18:05:56", ["on", "off", "off", "off", "off"], r"E:\Games\ELDEN RING\Game", r"%USERPROFILE%\Desktop\Programming\ReSave Manager\saves\games\Elden Ring", r"%USERPROFILE%\AppData\Roaming\EldenRing\76561197960267366"]]


class ToplevelWindow(customtkinter.CTkToplevel):
    """Окно настройки определённой игры"""
    def __init__(self, name_of_game, directory_of_game, dir_of_resave, dir_of_cur_save, parametrs):
        super().__init__()
        self.geometry("650x400")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(12, weight=1)

        self.directory_of_game = directory_of_game
        self.dir_of_resave = dir_of_resave
        self.dir_of_cur_save = dir_of_cur_save

        self.label = customtkinter.CTkLabel(self, text=f"Настройки резервного копирования для игры {name_of_game}")
        self.label.grid(row=0, columnspan=2, pady=5)

        # Переменные чекбоксов
        self.frequency_resave_var = customtkinter.StringVar(value=parametrs[0]) # Сохранение с определённой частотой
        self.smart_resave_var = customtkinter.StringVar(value=parametrs[1]) # Умное резервное копирование
        self.after_game_resave_var = customtkinter.StringVar(value=parametrs[2]) # Сохранение после каждой игровой сессии
        self.count_resave_var = customtkinter.StringVar(value=parametrs[3]) # Сохранение по количеству резервных сейвов
        self.memory_resave_var = customtkinter.StringVar(value=parametrs[4]) # Сохранение до поределённого лимита памяти

        # Настройка частоты автосохранений
        self.checkbox_frequency = customtkinter.CTkCheckBox(self, text="Частота автосохранений:", command=self.frequency_checkbox_event, variable=self.frequency_resave_var, onvalue="on", offvalue="off")
        self.checkbox_frequency.grid(row=1, column=0, padx=8)
        self.resave_frequency_slider = customtkinter.CTkSlider(self, from_=0, to=100)
        self.resave_frequency_slider.grid(row=2, column=0, padx=8, pady=4, sticky="ew")
        self.resave_frequency_mean = customtkinter.CTkLabel(self, text=f" дней")
        self.resave_frequency_mean.grid(row=2, column=1)

        # "Умное" резервное копирование
        self.checkbox_smart_resave = customtkinter.CTkCheckBox(self, text='"Умное" резервное копирование', command=self.smart_resave_event, variable=self.smart_resave_var, onvalue="on", offvalue="off")
        self.checkbox_smart_resave.grid(row=3, column=0, padx=8)

        # Резервное копирование после завершения каждой игровой сессии
        self.checkbox_after_game_resave = customtkinter.CTkCheckBox(self, text='Сохранение после каждой игровой сессии', command=self.after_game_resave_checkbox_event, variable=self.after_game_resave_var, onvalue="on", offvalue="off")
        self.checkbox_after_game_resave.grid(row=4, column=0, padx=8, pady=4)

        # Открытие директории ишры, резервной копии сохранений и директории с текущим сохранением
        self.button_game = customtkinter.CTkButton(self, text="Директория игры...", command=self.button_game_dir)
        self.button_game.grid(row=5, column=0, padx=(8, 0), sticky="ew", columnspan=2)
        self.button_resave = customtkinter.CTkButton(self, text="Директория резервных копий...", command=self.button_resaves)
        self.button_resave.grid(row=6, column=0, padx=8, pady=4, sticky="ew")
        self.button_cur_save = customtkinter.CTkButton(self, text="Директория текущего сохранения...", command=self.button_game_current_save)
        self.button_cur_save.grid(row=7, column=0, padx=(8, 0), sticky="ew")

        # Сохранение до определённого количества резервных копий
        self.checkbox_resave_count = customtkinter.CTkCheckBox(self, text='Резервное копирование по количеству копий: ', command=self.count_resaves_checkbox_event, variable=self.count_resave_var, onvalue="on", offvalue="off")
        self.checkbox_resave_count.grid(row=8, column=0, padx=8, pady=4)
        self.cnt_resaves_label = customtkinter.CTkLabel(self, text="Кол-во сохраняемых копий: ")
        self.cnt_resaves_label.grid(row=9, column=0, padx=8)
        self.cnt_resaves_entry = customtkinter.CTkEntry(self, placeholder_text="количество копий...")
        self.cnt_resaves_entry.grid(row=9, column=1, sticky="ew", padx=(0, 8))

        # Сохранение до определённого количества занятой памяти
        self.checkbox_resave_memory = customtkinter.CTkCheckBox(self, text='Резервное копирование по количеству занятой памяти: ', command=self.memory_resaves_checkbox_event, variable=self.memory_resave_var, onvalue="on", offvalue="off")
        self.checkbox_resave_memory.grid(row=10, column=0, padx=8, pady=4)
        self.memory_resaves_label = customtkinter.CTkLabel(self, text="Кол-во допустимой памяти: ")
        self.memory_resaves_label.grid(row=11, column=0, padx=8)
        self.cnt_resaves_memory_entry = customtkinter.CTkEntry(self, placeholder_text="МБ")
        self.cnt_resaves_memory_entry.grid(row=11, column=1, sticky="ew", padx=(0, 8))

        # Кнопка сохранения настроек
        self.button_game = customtkinter.CTkButton(self, text="Применить изменения", command=self.button_game_dir)
        self.button_game.grid(row=12, column=0, padx=8, sticky="ew", columnspan=2)

    def button_game_dir(self):
        """Открытие директории игры"""
        subprocess.Popen(['explorer', self.directory_of_game]) # Открыть проводник в заданной директории
    
    def button_resaves(self):
        """Открытие директории с резервными копиями сохранений"""
        subprocess.Popen(['explorer', self.dir_of_resave]) # Открыть проводник в заданной директории

    def button_game_current_save(self):
        """Открытие директории с текущем сохранение"""
        subprocess.Popen(['explorer', self.dir_of_cur_save]) # Открыть проводник в заданной директории

    def button_settings_save(self):
        """Сохранение изменений настроек"""
        print("Изменения сохранены")

    def frequency_checkbox_event(self):
        print("Частота автосохранений:", self.frequency_resave_var.get())

    def smart_resave_event(self):
        print('"Умное" резервное копирование:', self.smart_resave_var.get())

    def after_game_resave_checkbox_event(self):
        print('Сохранение после каждой игровой сессии:', self.after_game_resave_var.get())
    
    def count_resaves_checkbox_event(self):
        print('Сохранение взависимости от количества игровых копий:', self.count_resave_var.get())

    def memory_resaves_checkbox_event(self):
        print('Сохранение взависимости от количества игровых копий:', self.memory_resave_var.get())



class GameScrollBarFrame(customtkinter.CTkScrollableFrame):
    """Скроллбар, где будут находиться все карточки с играми"""
    def __init__(self, master):
        super().__init__(master)

        cnt = 0
        for i in games:
            self.games_frame = GameFrame(self, name=i[0], date=i[1], par=i[2], game_dir=i[3], resave_dir=i[4], cur_save_dir=i[5])
            self.games_frame.grid(row=cnt, column=0, sticky="ew", padx=8, pady=(6, 0))
            cnt += 1



class GameFrame(customtkinter.CTkFrame):
    """Блок, который будет создаваться для каждой игры пользователя"""
    def __init__(self, master, name, date, par, game_dir, resave_dir, cur_save_dir, num_of_game):
        super().__init__(master)

        self.name = name
        self.par = par
        self.game_dir = game_dir
        self.resave_dir = resave_dir
        self.cur_save_dir = cur_save_dir

        # Название игры
        self.label_name = customtkinter.CTkLabel(self, text=name)
        self.label_name.grid(row=0, column=0)

        # Отображение последней даты запуска игры
        self.label_name = customtkinter.CTkLabel(self, text=f"Последняя дата запуска: {date}")
        self.label_name.grid(row=1, column=0)

        # Заход в настройки каждого приложения
        self.game_resave_settings = customtkinter.CTkButton(self, text="Настройки", command=self.button_callbck)
        self.game_resave_settings.grid(row=0, column=1, padx=4)

        # Создание резервной копии
        self.game_resave_settings = customtkinter.CTkButton(self, text="Создать резервную копию", command=self.button_make_resave)
        self.game_resave_settings.grid(row=1, column=1, padx=4, pady=4)

        self.toplevel_window = None

    def button_callbck(self):
        """Заход в меню настроек определённой игры"""
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(name_of_game=self.name, directory_of_game=self.game_dir, dir_of_resave=self.resave_dir, dir_of_cur_save=self.cur_save_dir, parametrs=self.par)
            self.toplevel_window.focus()
        else:
            self.toplevel_window.focus()

    def button_make_resave(self):
        """Создаёт резервную копию"""

        shutil.copy('dir1/source.txt', 'dir2/destination.txt')




class SettingsFrameForGame(customtkinter.CTkFrame):
    """Рамка для настроек игровых сохранений приложения"""
    def __init__(self, master, name):
        super().__init__(master)

        self.label = customtkinter.CTkLabel(self, text=name)
        self.label.grid(row=0, column=0, sticky="nsew")

        self.label = customtkinter.CTkLabel(self, text="Тема приложения:")
        self.label.grid(row=0, column=0, sticky="nsew")



class Settings(customtkinter.CTk):
    """открывает настройки ОСНОВНОГО приложения, а не отдельных игр"""
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
    """Класс основного приложения"""
    def __init__(self):
        super().__init__()
        self.geometry("950x700")
        self.title("ReSave Manager")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # test
        self.games_frame = GameScrollBarFrame(self)
        self.games_frame.grid(row=1, sticky="nsew", columnspan=2, padx=8, pady=8)

        self.label_of_app = customtkinter.CTkLabel(self, text="List of your games:")
        self.label_of_app.grid(row=0, columnspan=2, sticky="ew")
        # self.button_settings = customtkinter.CTkButton(self, text="Settings", command=self.button_callbck)
        # self.button_settings.grid(row=0, column=2)

    def button_callbck(self):
        self.settings_app = Settings()
        self.settings_app.mainloop()

        



app = App()
app.mainloop()