import time
import os
import shutil
# print(time.time())
# print(time.ctime(time.time()))


games = [["Elden Ring", "time", ["on", "off", "off", "off", "off"], "game_directory", "resave_directory", "cur_save_dir"]]


import subprocess

# # Формируем путь с заменой переменной среды
# path = os.path.expandvars(r"%USERPROFILE%\Documents\Horizon Zero Dawn")
# path = os.path.expandvars(r"%USERPROFILE%\AppData\Local\FactoryGame\Saved\SaveGames")


# # Проверяем существование папки
# if os.path.exists(path):
#     # Открываем проводник
#     subprocess.Popen(f'explorer "{path}"')
# else:
#     print(f"Папка не найдена: {path}")


games = [["Elden Ring", "5 Май 2025 18:05:56", ["on", "off", "off", "off", "off"], r"E:\Games\ELDEN RING\Game", r"%USERPROFILE%\Desktop\Programming\ReSave Manager\saves\games\Elden Ring", r"%USERPROFILE%\AppData\Roaming\EldenRing\76561197960267366", 0, 0, 0]]
# Раскрываем переменные среды в пути
path = os.path.expandvars(rf"{games[0][5]}")

        # Проверяем существование папки
# if os.path.exists(path):
#     try:
#                 # Получаем список файлов/папок
#         contents = os.listdir(path)
#         print(contents)
#         if contents == []:
#             #subprocess.Popen(f'explorer "{path}"')
#             a = fr'{os.path.expandvars(games[0][5])}'
#             b = fr'{path}\ReSave 1\{games[0][5].split("\\")[-1]}'
#             os.makedirs(fr'{path}\\ReSave 1', exist_ok=True) # Создаёт папку для первого ресейва
#             shutil.copy(a, b)
#     except PermissionError:
#         print("Ошибка: Нет доступа к папке")
#     except NotADirectoryError:
#         print("Ошибка: Это не папка")
# else:
#     print(f"Папка не найдена: {path}")\




# def check_permissions(path):
#     st = os.stat(path)
#     return {
#         'user_read': bool(st.st_mode & stat.S_IRUSR),
#         'user_write': bool(st.st_mode & stat.S_IWUSR),
#         'user_exec': bool(st.st_mode & stat.S_IXUSR)
#     }

# print(check_permissions(path))

# # # Попробуйте получить права администратора
# # if not ctypes.windll.shell32.IsUserAnAdmin():
# #     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

# path = os.path.expandvars(rf"{games[0][4]}")
# contents = os.listdir(path)
# if contents == []:
#     #subprocess.Popen(f'explorer "{path}"')
#     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
#     a = fr'{os.path.expandvars(games[0][5])}'
#     b = fr'{path}\ReSave 1\{games[0][5].split("\\")[-1]}'
#     os.makedirs(fr'{path}\\ReSave 1', exist_ok=True) # Создаёт папку для первого ресейва
#     shutil.copy(a, b)


