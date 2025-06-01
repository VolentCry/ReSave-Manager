import customtkinter
import time
import subprocess
import shutil
import os
from tkinter import filedialog


from additional_algorithms import date_translate
from game_copier_algorithm import resave_copier_algorithm
import user_games

class ToplevelWindow(customtkinter.CTkToplevel):
    """Окно настройки определённой игры"""
    def __init__(self, name_of_game, directory_of_game, dir_of_resave, dir_of_cur_save, parametrs, num_of_game):
        super().__init__()
        self.geometry("650x410")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(12, weight=1)
        self.title(f"Настройки резервных сохранений дял {name_of_game}")
        self.resizable(False, False)

        self.directory_of_game = directory_of_game
        self.dir_of_resave = dir_of_resave
        self.dir_of_cur_save = dir_of_cur_save
        self.num_of_game = num_of_game
        self.day = 1
        self.type_of_time = "дней"

        # Переменные чекбоксов
        self.frequency_resave_var = customtkinter.StringVar(value=parametrs[0]) # Сохранение с определённой частотой
        self.smart_resave_var = customtkinter.StringVar(value=parametrs[1]) # Умное резервное копирование
        self.after_game_resave_var = customtkinter.StringVar(value=parametrs[2]) # Сохранение после каждой игровой сессии
        self.count_resave_var = customtkinter.StringVar(value=parametrs[3]) # Сохранение по количеству резервных сейвов
        self.memory_resave_var = customtkinter.StringVar(value=parametrs[4]) # Сохранение до поределённого лимита памяти

        # Настройка частоты автосохранений
        self.checkbox_frequency = customtkinter.CTkCheckBox(self, text="Частота автосохранений:", command=self.frequency_checkbox_event, variable=self.frequency_resave_var, onvalue="on", offvalue="off", font=("Calibri", 17))
        self.checkbox_frequency.grid(row=1, column=0, padx=8, sticky="w", pady=(12, 0))
        self.resave_frequency_slider = customtkinter.CTkSlider(self, from_=0, to=100, command=self.change_slider)
        self.resave_frequency_slider.grid(row=2, column=0, padx=8, pady=10, sticky="we")
        self.resave_frequency_slider.set(3)
        self.resave_frequency_mean = customtkinter.CTkLabel(self, text=f"{self.day} дней")
        self.resave_frequency_mean.grid(row=2, column=1, sticky="w")

        # "Умное" резервное копирование
        self.checkbox_smart_resave = customtkinter.CTkCheckBox(self, text='"Умное" резервное копирование', command=self.smart_resave_event, variable=self.smart_resave_var, onvalue="on", offvalue="off", font=("Calibri", 17))
        self.checkbox_smart_resave.grid(row=3, column=0, padx=8, sticky="w")

        # Резервное копирование после завершения каждой игровой сессии
        self.checkbox_after_game_resave = customtkinter.CTkCheckBox(self, text='Сохранение после каждой игровой сессии', command=self.after_game_resave_checkbox_event, variable=self.after_game_resave_var, onvalue="on", offvalue="off", font=("Calibri", 17))
        self.checkbox_after_game_resave.grid(row=4, column=0, padx=8, pady=10, sticky="w")

        # Открытие директории ишры, резервной копии сохранений и директории с текущим сохранением
        self.button_game = customtkinter.CTkButton(self, text="Директория игры...", command=self.button_game_dir, font=("Calibri", 17))
        self.button_game.grid(row=5, column=0, padx=8, sticky="ew", columnspan=2)
        self.button_resave = customtkinter.CTkButton(self, text="Директория резервных копий...", command=self.button_resaves, font=("Calibri", 17))
        self.button_resave.grid(row=6, column=0, padx=8, pady=4, sticky="ew", columnspan=2)
        self.button_cur_save = customtkinter.CTkButton(self, text="Директория текущего сохранения...", command=self.button_game_current_save, font=("Calibri", 17))
        self.button_cur_save.grid(row=7, column=0, padx=8, sticky="ew", columnspan=2)

        # Сохранение до определённого количества резервных копий
        self.checkbox_resave_count = customtkinter.CTkCheckBox(self, text='Резервное копирование по количеству копий', command=self.count_resaves_checkbox_event, variable=self.count_resave_var, onvalue="on", offvalue="off", font=("Calibri", 17))
        self.checkbox_resave_count.grid(row=8, column=0, padx=8, pady=4, sticky="w")
        self.cnt_resaves_label = customtkinter.CTkLabel(self, text="Кол-во сохраняемых копий: ", font=("Calibri", 17))
        self.cnt_resaves_label.grid(row=9, column=0, padx=8, sticky="w")
        self.cnt_resaves_entry = customtkinter.CTkEntry(self, placeholder_text="количество копий...", width=300)
        self.cnt_resaves_entry.grid(row=9, column=1, sticky="w", padx=(0, 8))
        self.cnt_resaves_entry.setvar("0")

        # Сохранение до определённого количества занятой памяти
        self.checkbox_resave_memory = customtkinter.CTkCheckBox(self, text='Резервное копирование по количеству занятой памяти', command=self.memory_resaves_checkbox_event, variable=self.memory_resave_var, onvalue="on", offvalue="off", font=("Calibri", 17))
        self.checkbox_resave_memory.grid(row=10, column=0, padx=8, pady=4, sticky="w")
        self.memory_resaves_label = customtkinter.CTkLabel(self, text="Кол-во допустимой памяти: ", font=("Calibri", 17))
        self.memory_resaves_label.grid(row=11, column=0, padx=8, sticky="w")
        self.cnt_resaves_memory_entry = customtkinter.CTkEntry(self, placeholder_text="МБ", width=300)
        self.cnt_resaves_memory_entry.grid(row=11, column=1, sticky="w", padx=(0, 8))
        self.cnt_resaves_memory_entry.setvar("0")

        # Кнопка сохранения настроек
        self.button_game = customtkinter.CTkButton(self, text="Применить изменения", command=self.button_settings_save, height=38)
        self.button_game.grid(row=12, column=0, padx=8, sticky="ew", columnspan=2)

    def button_game_dir(self):
        """Открытие директории игры"""
        subprocess.Popen(['explorer', self.directory_of_game]) # Открыть проводник в заданной директории
    
    def button_resaves(self):
        """Открытие директории с резервными копиями сохранений"""
        subprocess.Popen(['explorer', self.dir_of_resave]) # Открыть проводник в заданной директории
        
    def change_slider(self, value):
        """Конфигурация изменений слайдера"""
        if value <= 27:
            self.day = str(int((value // 3) + 1))
            self.type_of_time = "дней"
            self.resave_frequency_mean.setvar(f"{self.day} {self.type_of_time}")
        elif 27 < value < 88:
            print("Weeks")
        elif value >= 88:
            print("Months")

        print(value)

    def button_game_current_save(self):
        """Открытие директории с текущем сохранение"""
        subprocess.Popen(['explorer', self.dir_of_cur_save]) # Открыть проводник в заданной директории

    def button_settings_save(self):
        """Сохранение изменений настроек"""
        user_games.games[self.num_of_game][2][0] = self.checkbox_frequency.get()
        user_games.games[self.num_of_game][2][1] = self.checkbox_smart_resave.get()
        user_games.games[self.num_of_game][2][2] = self.checkbox_after_game_resave.get()
        user_games.games[self.num_of_game][2][3] = self.checkbox_resave_count.get()
        user_games.games[self.num_of_game][2][4] = self.checkbox_resave_memory.get()
        user_games.games[self.num_of_game][7] = int(self.cnt_resaves_entry.get())
        user_games.games[self.num_of_game][8] = int(self.cnt_resaves_memory_entry.get())
        print(user_games.games[self.num_of_game])

    def frequency_checkbox_event(self):
        print("Частота автосохранений:", self.frequency_resave_var.get())

    def smart_resave_event(self):
        print('"Умное" резервное копирование:', self.smart_resave_var.get())

    def after_game_resave_checkbox_event(self):
        self.frequency_resave_var.set("off")
        self.smart_resave_var.set("off")
        if self.checkbox_after_game_resave.get() != "off":
            self.checkbox_frequency.configure(state="disabled")
            self.checkbox_smart_resave.configure(state="disabled")
            self.resave_frequency_slider.configure(state="disabled")
        else:
            self.checkbox_frequency.configure(state="normal")
            self.checkbox_smart_resave.configure(state="normal")
            self.resave_frequency_slider.configure(state="normal")
    
    def count_resaves_checkbox_event(self):
        self.memory_resave_var.set("off")
        if self.checkbox_resave_count.get() != "off":
            self.checkbox_resave_memory.configure(state="disabled")
            self.memory_resaves_label.configure(state="disabled")
            self.cnt_resaves_memory_entry.configure(state="disabled")
        else:
            self.checkbox_resave_memory.configure(state="normal")
            self.memory_resaves_label.configure(state="normal")
            self.cnt_resaves_memory_entry.configure(state="normal")

    def memory_resaves_checkbox_event(self):
        self.count_resave_var.set("off")
        if self.checkbox_resave_memory.get() != "off":
            self.checkbox_resave_count.configure(state="disabled")
            self.cnt_resaves_label.configure(state="disabled")
            self.cnt_resaves_entry.configure(state="disabled")
        else:
            self.checkbox_resave_count.configure(state="normal")
            self.cnt_resaves_label.configure(state="normal")
            self.cnt_resaves_entry.configure(state="normal")



class GameScrollBarFrame(customtkinter.CTkScrollableFrame):
    """Скроллбар, где будут находиться все карточки с играми"""
    def __init__(self, master):
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        cnt = 0
        for i in user_games.games:
            self.games_frame = GameFrame(self, name=i[0], date=i[1], par=i[2], game_dir=i[3], resave_dir=i[4], cur_save_dir=i[5], num_of_game=cnt, current_cnt_resaves=i[6], resaves_limit_cnt=i[7], resaves_limit_memory=i[8])
            self.games_frame.grid(row=cnt, column=0, sticky="ew", padx=8, pady=(6, 0))
            cnt += 1



class AddGameWindow(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.geometry("500x300")
        self.title("Добавление новой игры...")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.path_to_game = None
        self.path_to_save = None

        self.add_name_label = customtkinter.CTkLabel(self, text="Введите название игры: ", font=("Calibri", 14, "bold"))
        self.add_name_label.grid(row=0, column=0, padx=8, pady=(6, 0), sticky="w")
        self.add_name_entry = customtkinter.CTkEntry(self)
        self.add_name_entry.grid(row=1, column=0, padx=8, pady=(10, 0), sticky="we")

        self.file_path_button = customtkinter.CTkButton(self, command=self.select_folder_to_game, text="Укажите путь...")
        self.file_path_button.grid(row=2, column=0, padx=8, pady=(20, 0))
        self.file_path_label = customtkinter.CTkLabel(self, text="Путь к файлу: ...", font=("Calibri", 14, "bold"))
        self.file_path_label.grid(row=3, column=0, padx=8, pady=(7, 0), sticky="we")

        self.file_path_save_button = customtkinter.CTkButton(self, command=self.select_folder_to_game_save, text="Укажите путь сохранений...")
        self.file_path_save_button.grid(row=4, column=0, padx=8, pady=(7, 0))
        self.file_path_save_label = customtkinter.CTkLabel(self, text="Путь к файлу сохранений: ...", font=("Calibri", 14, "bold"))
        self.file_path_save_label.grid(row=5, column=0, padx=8, pady=(7, 0), sticky="we")

        self.add_game_button = customtkinter.CTkButton(self, command=self.add_game, text="Сохранить игру")
        self.add_game_button.grid(row=6, column=0, padx=8, pady=7, sticky="we")

    def select_folder_to_game(self):
        folder_path = filedialog.askdirectory(title="Выберите папку с файлами")
        if folder_path:
            self.file_path_label.configure(text=f"Выбрано: {folder_path}")
        self.path_to_game = folder_path

    def select_folder_to_game_save(self):
        folder_path = filedialog.askdirectory(title="Выберите папку с сохранение игры")
        if folder_path:
            self.file_path_save_label.configure(text=f"Выбрано: {folder_path}")
        self.path_to_save = folder_path

    def add_game(self):
        time_to_start = date_translate(time.ctime(time.time()))
        name_of_game = self.add_name_entry.get()
        path_to_resave = fr'C:\Users\Semen\Desktop\Programming\ReSave Manager\saves\games\{name_of_game}'
        os.makedirs(path_to_resave, exist_ok=True) # Создание папки для новой игры
        user_games.games.append([name_of_game, time_to_start, ["on", "off", "off", "off", "off"], self.path_to_game, path_to_resave, self.path_to_save, 0, 0, 0])
        print(user_games.games)



class GameFrame(customtkinter.CTkFrame):
    """Блок, который будет создаваться для каждой игры пользователя"""
    def __init__(self, master, name, date, par, game_dir, resave_dir, cur_save_dir, num_of_game, current_cnt_resaves, resaves_limit_cnt, resaves_limit_memory):
        super().__init__(master)

        self.columnconfigure(1, weight=1)
        self.fg_color="#3F3F3F"

        self.name = name # Название игры
        self.par = par # Параметры настроек
        self.game_dir = game_dir # Директория игры
        self.resave_dir = resave_dir # Директория ресейвов
        self.cur_save_dir = cur_save_dir # Директория текущего сейва
        self.num_of_game = num_of_game # Номер игры в общем списке игр пользователя
        self.current_cnt_resaves = current_cnt_resaves # Количество текущих ресейвов
        self.resaves_limit_cnt = resaves_limit_cnt # Ограничение по количеству ресейвов
        self.resaves_limit_memory = resaves_limit_memory # Ограничение по количеству занимаемой памяти ресейвами

        # Название игры
        self.label_name = customtkinter.CTkLabel(self, text=name)
        self.label_name.grid(row=0, column=0)

        # Отображение последней даты запуска игры
        self.label_name = customtkinter.CTkLabel(self, text=f"Последняя дата запуска: {date}")
        self.label_name.grid(row=1, column=0)

        # Заход в настройки каждого приложения
        self.game_resave_settings = customtkinter.CTkButton(self, text="Настройки", command=self.button_callbck, width=200)
        self.game_resave_settings.grid(row=0, column=1, padx=8, sticky="e")

        # Создание резервной копии
        self.game_resave_settings = customtkinter.CTkButton(self, text="Создать резервную копию", command=self.button_make_resave, width=200)
        self.game_resave_settings.grid(row=1, column=1, padx=8, pady=4, sticky="e")

        self.toplevel_window = None

    def button_callbck(self):
        """Заход в меню настроек определённой игры"""
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(name_of_game=self.name, directory_of_game=self.game_dir, dir_of_resave=self.resave_dir, dir_of_cur_save=self.cur_save_dir, parametrs=self.par, num_of_game=self.num_of_game)
            self.toplevel_window.focus()
        else:
            self.toplevel_window.focus()

    def button_make_resave(self):
        """Создаёт резервную копию"""
        resave_copier_algorithm(user_games.games[self.num_of_game], self.num_of_game)




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
        self.grid_rowconfigure(2, weight=1)

        # test
        self.games_frame = GameScrollBarFrame(self)
        self.games_frame.grid(row=1, sticky="nsew", columnspan=2, padx=8, pady=8, rowspan=2)

        self.label_of_app = customtkinter.CTkLabel(self, text="List of your games:", font=("Calibri", 28, "bold"))
        self.label_of_app.grid(row=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.button_to_add_game = customtkinter.CTkButton(self, text="+ Добавить игру", command=self.add_game)
        self.button_to_add_game.grid(row=3, columnspan=2, sticky="sew", padx=8, pady=(0, 8))
        # self.button_settings = customtkinter.CTkButton(self, text="Settings", command=self.button_callbck)
        # self.button_settings.grid(row=0, column=2)

        self.toplevel_window = None

    def button_callbck(self):
        self.settings_app = Settings()
        self.settings_app.mainloop()
    
    def add_game(self):
        """Заход в меню добавления определённой игры"""
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = AddGameWindow()
            self.toplevel_window.focus()
        else:
            self.toplevel_window.focus()

        



app = App()
app.mainloop()