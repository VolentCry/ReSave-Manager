import customtkinter
import time
import subprocess
import shutil
import os
from tkinter import filedialog
import asyncio
from async_tkinter_loop import async_handler, async_mainloop
from async_tkinter_loop.mixins import AsyncCTk
import threading

from additional_algorithms import date_translate
from game_copier_algorithm import resave_copier_algorithm, game_detection
import user_games
from user_games import *
from process_monitoring import a_main, LOG_FILE

# Подключаемся к БД
conn_app = connect_db()

class ToplevelWindow(customtkinter.CTkToplevel):
    """Окно настройки определённой игры"""
    def __init__(self, name_of_game, directory_of_game, dir_of_resave, dir_of_cur_save, parametrs, num_of_game):
        super().__init__()
        self.geometry("650x410")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(12, weight=1)
        self.title(f"Настройки резервных сохранений дял {name_of_game}")
        self.resizable(False, False)

        self.name_of_game = name_of_game
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
            self.resave_frequency_mean.configure(text=f"{self.day} {self.type_of_time}")
        elif 27 < value < 88:
            cnt = 1
            if value <= 42:
                self.day = str(cnt + int(((value-27) // 5) + 1))
                self.type_of_time = "недели"
            else:
                self.day = str(cnt + int(((value-27) // 5) + 1))
                self.type_of_time = "недель"
            self.resave_frequency_mean.configure(text=f"{self.day} {self.type_of_time}")
        elif value >= 88:
            cnt = 2
            if value <= 96:
                self.day = str(cnt + int(((value-88) // 4) + 1))
                self.type_of_time = "месяца"
            else:
                self.day = str(cnt + int(((value-88) // 4) + 1))
                self.type_of_time = "месяцев"
            self.resave_frequency_mean.configure(text=f"{self.day} {self.type_of_time}")


    def button_game_current_save(self):
        """Открытие директории с текущем сохранение"""
        subprocess.Popen(['explorer', self.dir_of_cur_save]) # Открыть проводник в заданной директории

    def button_settings_save(self):
        """Сохранение изменений настроек"""
        setting_chackbox_parametrs = [self.checkbox_frequency.get(), self.checkbox_smart_resave.get(), self.checkbox_after_game_resave.get(), self.checkbox_resave_count.get(), self.checkbox_resave_memory.get()]
        update_parametrs(conn_app, self.name_of_game, setting_chackbox_parametrs)
        user_games.games[self.num_of_game][2][0] = self.checkbox_frequency.get()
        user_games.games[self.num_of_game][2][1] = self.checkbox_smart_resave.get()
        user_games.games[self.num_of_game][2][2] = self.checkbox_after_game_resave.get()
        user_games.games[self.num_of_game][2][3] = self.checkbox_resave_count.get()
        user_games.games[self.num_of_game][2][4] = self.checkbox_resave_memory.get()
        user_games.games[self.num_of_game][7] = int(self.cnt_resaves_entry.get())
        user_games.games[self.num_of_game][8] = int(self.cnt_resaves_memory_entry.get())
        user_games.games[self.num_of_game][9] = self.resave_frequency_mean.cget("text")
        print(user_games.games[self.num_of_game])
        self.destroy()

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
        self.game_frames = []  # Храним ссылки на фреймы
        self.update_games()    # Инициализация при создании
    
    def update_games(self):
        # Удаляем старые фреймы
        for frame in self.game_frames:
            frame.destroy()
        self.game_frames.clear()
        
        # Создаем новые фреймы для всех игр
        for i, game in enumerate(user_games.games):
            game_frame = GameFrame(
                self, 
                name=game[0],
                date=game[1],
                par=game[2],
                game_dir=game[3],
                resave_dir=game[4],
                cur_save_dir=game[5],
                num_of_game=i,
                current_cnt_resaves=game[6],
                resaves_limit_cnt=game[7],
                resaves_limit_memory=game[8]
            )
            game_frame.grid(row=i, column=0, sticky="ew", padx=8, pady=(6, 0))
            self.game_frames.append(game_frame)



class AddGameWindow(customtkinter.CTkToplevel):
    def __init__(self, games_frame_ref):  # Добавляем параметр
        super().__init__()
        self.geometry("500x300")
        self.title("Добавление новой игры...")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.path_to_game = None
        self.path_to_save = None
        self.games_frame_ref = games_frame_ref  # Сохраняем ссылку

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
        if name_of_game == "" or name_of_game == None or self.path_to_game == None or self.path_to_save == None:
            print("Пожалуйста укажите все данные")
        else:
            path_to_resave = fr'C:\Users\Semen\Desktop\Programming\ReSave Manager\saves\games\{name_of_game}'
            os.makedirs(path_to_resave, exist_ok=True) # Создание папки для новой игры
            user_games.games.append([name_of_game, time_to_start, ["on", "off", "off", "off", "off"], self.path_to_game, path_to_resave, self.path_to_save, 0, 0, 0, "1 день"])
            print(user_games.games)
        self.games_frame_ref.update_games()
        self.destroy()



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



class GameListScrollBar(customtkinter.CTkScrollableFrame):
    """Скроллбар, где отобразиться список всех обнаруженных игр"""
    def __init__(self, master, detected_games: list):
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        cnt = 0
        for i in detected_games:
            self.game_name = customtkinter.CTkLabel(self, text=f"{i}", justify="left", anchor="w", font=("Calibri", 14, "bold"))
            self.game_name.grid(row=cnt, column=0, sticky="w", padx=8, pady=(2, 0))
            cnt += 1



class DatectedGamesListTopLevel(customtkinter.CTkToplevel):
    """Создаёт окно, куда выводиться список оьбнаруженных игр"""
    
    def __init__(self, detected_games, detected_games_saves_path, games_frame_ref):
        super().__init__()
        self.geometry("380x500")
        self.title("Обноруженные файлы сохранений")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        # Переменные
        self.detected_games = detected_games
        self.detected_games_saves_path = detected_games_saves_path
        self.games_frame_ref = games_frame_ref

        # Составляющие приложения
        self.list_label = customtkinter.CTkLabel(self, text="Список обнаруженных игр:", font=("Calibri", 16, "bold"))
        self.list_label.grid(row=0, column=0, padx=8, pady=(10, 0), sticky="ew")
        self.names_scrollbar = GameListScrollBar(self, self.detected_games)
        self.names_scrollbar.grid(row=1, column=0, padx=8, pady=8, sticky="ew")
        self.text_info = customtkinter.CTkLabel(self, text="Предупреждение! Выше найденые игры это лишь показатель того, что были обнаружены файлы сохранения, так что далее укажить путь к файлу каждой игры!\n"\
                                                "После нажатия кнопки подтверждения игры автоматически будут добавлены в вашу библиотеку.", font=("Calibri", 13.5, "bold"), wraplength=(380-16))
        self.text_info.grid(row=2, column=0, padx=8, sticky="ew")
        self.confirm_button = customtkinter.CTkButton(self, text="Подтвердить", command=self.add_detected_games)
        self.confirm_button.grid(row=3, column=0, padx=8, pady=8, sticky="ew")
    
    def add_detected_games(self):
        """Добавляет обнаруженные игры в библиотеку пользователя"""
        names = [y[0] for y in user_games.games]
        for i in self.detected_games:
            if i in names:
                print(f"Игра {i} уже добавлена")
            else:
                print(f"Игра {i} теперь добавлена в библиотеку")
                time_to_start = date_translate(time.ctime(time.time())) # Получаем текущее время
                path_to_resave = fr'C:\Users\Semen\Desktop\Programming\ReSave Manager\saves\games\{i}'
                os.makedirs(path_to_resave, exist_ok=True) # Создание папки для новой игры
                user_games.games.append([i, time_to_start, ["on", "off", "off", "off", "off"], "", path_to_resave, self.detected_games_saves_path[self.detected_games.index(i)], 0, 0, 0, "1 день"])
        print(user_games.games)
        # ОБНОВЛЯЕМ ОСНОВНОЙ ФРЕЙМ
        self.games_frame_ref.update_games()
        self.destroy()



class Settings(customtkinter.CTk):
    """открывает настройки ОСНОВНОГО приложения, а не отдельных игр"""
    def __init__(self):
        super().__init__()
        self.geometry("400x150")
        self.title("Настройки приложения")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)

        self.label = customtkinter.CTkLabel(self, text="Тема приложения:", font=("Calibri", 14, "bold"))
        self.label.grid(row=0, column=0, sticky="nsew", pady=(8, 0))
        self.optionmenu = customtkinter.CTkOptionMenu(self, values=["Системная", "Светлая", "Тёмная"])
        self.optionmenu.grid(row=0, column=1, pady=(8, 0))
        self.button_confirn = customtkinter.CTkButton(self, text="Авто обноружение игр", command=self.game_detected_button)
        self.button_confirn.grid(row=1, column=0, padx=8, pady=8, sticky="ew")
        self.button_confirn = customtkinter.CTkButton(self, text="Подтвердить настройки", command=self.button_callbck)
        self.button_confirn.grid(row=3, column=0)

        self.toplevel_window = None

    def button_callbck(self):
        self.destroy()

    def game_detected_button(self):
        """Функция, которая по нажатию кнопки запускает поиск директорий сохранений игр"""
        detected_games, saves_path = game_detection()
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            # Передаем games_frame из основного окна
            self.toplevel_window = DatectedGamesListTopLevel(
                detected_games, 
                saves_path,
                app.games_frame  # Ссылка на основной фрейм
            )
            self.toplevel_window.focus()



class App(customtkinter.CTk):
    """Класс основного приложения"""
    def __init__(self):
        super().__init__()
        self.geometry("950x700")
        self.title("ReSave Manager")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        threading.Thread(target=start_async_loop).start()

        # test
        self.games_frame = GameScrollBarFrame(self)  # Сохраняем в атрибуте
        self.games_frame.grid(row=1, sticky="nsew", columnspan=2, padx=8, pady=8, rowspan=2)

        self.label_of_app = customtkinter.CTkLabel(self, text="List of your games:", font=("Calibri", 28, "bold"))
        self.label_of_app.grid(row=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.button_to_add_game = customtkinter.CTkButton(self, text="+ Добавить игру", command=self.add_game)
        self.button_to_add_game.grid(row=3, columnspan=2, sticky="sew", padx=8, pady=(0, 8))
        self.button_settings = customtkinter.CTkButton(self, text="Настройки приложения", command=self.button_callbck)
        self.button_settings.grid(row=0, column=1, sticky="e", padx=8, pady=(8, 0))

        self.toplevel_window = None

    def button_callbck(self):
        self.settings_app = Settings()
        self.settings_app.mainloop()    

    def add_game(self):
        """Заход в меню добавления определённой игры"""
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = AddGameWindow(self.games_frame) 
            self.toplevel_window.focus()
        else:
            self.toplevel_window.focus()



path_to_exe = [ r"C:\Users\Semen\AppData\Roaming\.tlauncher\legacy\Minecraft\TL.exe",
        r"E:\Games\The Planet Crafter (2024)\The Planet Crafter\Planet Crafter.exe",
        r"E:\Games\Untitled Goose Game\Untitled.exe"]

for j in user_games.games:
    for i in os.listdir(j[3]):
        if str(i).endswith(".exe"):
            path_to_exe.append(rf"{j[3]}\{str(i)}")

def start_async_loop():
    try:
        asyncio.run(a_main(path_to_exe))
    except:
        print("Не удалось запустить мониторинг процессов")
        
def on_closing():
    app.destroy()
    print("\n[INFO] Скрипт остановлен вручную (Ctrl+C).")
    # Очистка файла логов
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w'):
            pass  # Открытие в режиме 'w' очищает файл
        print(f"[INFO] Файл логов '{LOG_FILE}' успешно очищен.")
    else:
        print(f"[WARNING] Файл логов '{LOG_FILE}' не найден при попытке очистки.")

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()
    


