import sqlite3
from sqlite3 import Connection
from datetime import datetime
import os


# Данные пользователя
games = [["Elden Ring", "5 Май 2025 18:05:56", ["on", "off", "off", "off", "off"], r"E:\Games\ELDEN RING\Game", r"%USERPROFILE%\Desktop\Programming\ReSave Manager\saves\games\Elden Ring", r"%APPDATA%\EldenRing\76561197960267366", 0, 0, 0, "1 день", ['E:\\Games\\ELDEN RING\\Game\\eldenring.exe', 'E:\\Games\\ELDEN RING\\Game\\start_protected_game.exe']]]
# Структура массива под одну игру: название, последняя дата запуска, вкл/выкл параметры, директория игры, директория ресейвов, директория сейвов, кол-во текущих ресейвов, ограничение по кол-во сейвов(0 - нет ограничений), ограничение по памяти сейвов(0 - нет ограничений), частота автосохранений; пути к exe файлам игры


def connect_db(db_name='user_game.db') -> Connection:
    """ Подключение к БД user_game """
    conn = sqlite3.connect(db_name, check_same_thread=False, timeout=10)
    return conn

def add_game(conn: Connection, name_of_game: str, parametrs_of_settings: list, path_to_game: str, path_to_resave: str, path_to_save: str, current_resave: int, limit_resave: int, limit_memory: int, frequency_resave: str):
    """ Функция для добавления новой игры в базу """
    cursor = conn.cursor()

    path_to_exe = []
    if path_to_game == "":
        path_to_exe = ""
    else:
        for i in os.listdir(path_to_game):
            if str(i).endswith(".exe"):
                path_to_exe.append(rf"{path_to_game}\{str(i)}")
        path_to_exe = ";".join(path_to_exe)

    parametrs_of_settings = " ".join(parametrs_of_settings)
    last_date = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        cursor.execute('''
            INSERT INTO games (name_of_game, last_date, parametrs, path_to_game, path_to_resave, path_to_save, current_resave, limit_resave, limit_memory, frequency_resave, path_to_exe)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name_of_game, last_date, parametrs_of_settings, path_to_game, path_to_resave, path_to_save, current_resave, limit_resave, limit_memory, frequency_resave, path_to_exe))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Игра уже добавлена")

def take_parametrs(conn: Connection, name_of_game: str) -> list:
    """Возвращает параметры для настроек у определённой игры"""
    cursor = conn.cursor()
    cursor.execute('SELECT name_of_game, parametrs FROM games')
    rows = cursor.fetchall()
    for i in rows:
        if i[0] == name_of_game: return i[1].split()
    print("Игры нет в списке")

def take_exe_paths(conn: Connection, name_of_game: str) -> list:
    """Возвращает пути к exe-файлам игры"""
    cursor = conn.cursor()
    cursor.execute('SELECT name_of_game, path_to_exe FROM games')
    rows = cursor.fetchall()
    for i in rows:
        if i[0] == name_of_game: return i[1].split(";")
    print("Игры нет в списке")

def take_limits(conn: Connection, name_of_game: str) -> tuple:
    """Возвращает текущее количество ресейвов, лимит по количеству ресейвов, лимсит по количеству занимаемой памяти и частоту создания ресейвов."""
    cursor = conn.cursor()
    cursor.execute('SELECT name_of_game, current_resave, limit_resave, limit_memory, frequency_resave FROM games')
    rows = cursor.fetchall()
    for i in rows:
        if i[0] == name_of_game: return i[1:]
    print("Игры нет в списке")

def take_paths(conn: Connection, name_of_game: str) -> tuple:
    """Возвращает путь к игре, пуьб к ресейвам и путь к сохранению игры."""
    cursor = conn.cursor()
    cursor.execute('SELECT name_of_game, path_to_game, path_to_resave, path_to_save FROM games')
    rows = cursor.fetchall()
    for i in rows:
        if i[0] == name_of_game: return i[1:]
    print("Игры нет в списке")

def update_parametrs(conn: Connection, name_of_game: str, parametrs: list):
    """Обновляет значение параметров настройки"""
    cursor = conn.cursor()
    parametrs_of_settings = " ".join(parametrs)
    cursor.execute(
        'UPDATE games SET parametrs = ? WHERE name_of_game = ?', (parametrs_of_settings, name_of_game)
    )
    conn.commit()

def update_game_path(conn: Connection, name_of_game: str, path_to_game: str):
    """Обновляет путь к папке с игрой"""
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE games SET path_to_game = ? WHERE name_of_game = ?', (path_to_game, name_of_game)
    )
    conn.commit()

def update_game_exe(conn: Connection, name_of_game: str, paths_to_game_exe: str):
    """Обновляет пути к exe игры"""
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE games SET path_to_exe = ? WHERE name_of_game = ?', (paths_to_game_exe, name_of_game)
    )
    conn.commit()

def update_current_game_resaves(conn: Connection, name_of_game: str):
    """Обновляет значения количества текущих ресейвов в БД у определённой игры"""
    cursor = conn.cursor()
    cursor.execute("SELECT current_resave FROM games WHERE name_of_game = ?", (name_of_game,))
    rows = cursor.fetchall()
    current_resaves = int(rows[0][0]) + 1
    print(current_resaves, name_of_game)
    cursor.execute('UPDATE games SET current_resave = ? WHERE name_of_game = ?', (current_resaves, name_of_game))
    conn.commit()

def update_current_all_games_resaves(conn: Connection):
    """Обновляет значения количества текущих ресейвов у всех игр исходя из содержания папки saves/games/..."""
    cursor = conn.cursor()
    games_names = take_all_games_names(conn)
    games_current_resaves = {}
    for name in os.listdir("saves/games"):
        games_current_resaves[name] = len(os.listdir(f"saves/games/{name}"))
    for game_name in games_names:
        cursor.execute('UPDATE games SET current_resave = ? WHERE name_of_game = ?', (games_current_resaves[game_name[0]], game_name[0]))
    conn.commit()

def update_limit_resaves(conn: Connection, name_of_game: str, resaves_cnt_limit: int):
    """Обновляет значения ограничения по количеству ресейвов"""
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE games SET limit_resave = ? WHERE name_of_game = ?', (resaves_cnt_limit, name_of_game)
    )
    conn.commit()

def update_limit_memory(conn: Connection, name_of_game: str, resaves_memory_limit: int):
    """Обновляет значения ограничения по количеству занимаемой памяти"""
    cursor = conn.cursor()
    cursor.execute('UPDATE games SET limit_memory = ? WHERE name_of_game = ?', (resaves_memory_limit, name_of_game))
    conn.commit()

def update_frequency_resave(conn: Connection, name_of_game: str, frequency_resave: str):
    """Обновляет значения частоты создания резервных копий"""
    cursor = conn.cursor()
    cursor.execute('UPDATE games SET frequency_resave = ? WHERE name_of_game = ?', (frequency_resave, name_of_game))
    conn.commit()

def delete_game(conn: Connection, name_of_game: str):
    """Удаляет игру из базы данных"""
    cursor = conn.cursor()
    cursor.execute('DELETE FROM games WHERE name_of_game = ?', (name_of_game,))
    conn.commit()

def take_game_info(conn: Connection, name_of_game: str) -> list:
    """Возвращает все параметры для определённой игры"""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM games')
    rows = cursor.fetchall()
    for i in rows:
        if i[0] == name_of_game: return i   
    print("Игры нет в списке")

def take_all_games(conn: Connection) -> list:
    """Возвращает все игры из базы данных"""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM games')
    return cursor.fetchall()

def take_all_games_names(conn: Connection) -> list:
    """Возвращает все названия игр из базы данных"""
    cursor = conn.cursor()
    cursor.execute('SELECT name_of_game FROM games')
    return cursor.fetchall()

def take_frequency_resave(conn: Connection, name_of_game: str) -> str:
    """Возвращает частоты сохранений резервных копий для определённой игры"""
    cursor = conn.cursor()
    cursor.execute('SELECT frequency_resave FROM games WHERE name_of_game = ?', (name_of_game,))
    rows = cursor.fetchall()
    return rows[0][0]

def take_all_games_frequency(conn: Connection) -> list:
    """Возвращает название игры и её частоту сохранения"""
    cursor = conn.cursor()
    cursor.execute('SELECT name_of_game, frequency_resave FROM games')
    return cursor.fetchall()

def update_last_date(conn: Connection, name_of_game: str, last_date):
    """Обновляет значение даты последнего запуска игры"""
    cursor = conn.cursor()
    cursor.execute('UPDATE games SET last_date = ? WHERE name_of_game = ?', (last_date, name_of_game))
    conn.commit()

def find_path_exe(conn: Connection, path_to_exe: str) -> str|None:
    """Находит название игры, к который указывает exe-файл"""
    cursor = conn.cursor()
    cursor.execute('SELECT name_of_game, path_to_exe FROM games')
    rows = cursor.fetchall()
    for i in rows:
        paths_to_exe = i[1].split(";")
        for path in paths_to_exe:
            if path == path_to_exe:
                return i[0]
    return None


def update_frequency_resave(conn: Connection, name_of_game: str, new_future_date: str):
    """ Обновляет дату будущего автосохранения игры исходя из периода """
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET future_date = ? WHERE name_of_game = ?', (new_future_date, name_of_game))
    conn.commit()

# conn1 = connect_db()
# add_game(conn1, "The Planet Crafter", ["off", "off", "off", "off", "off"], r"E:\Games\The Planet Crafter (2024)\The Planet Crafter", r"saves\games\The Planet Crafter", r"%USERPROFILE%\AppData\LocalLow\MijuGames\Planet Crafter", 0, 0, 0, "1 день")