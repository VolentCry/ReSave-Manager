import time
import os


print(time.time())
print(time.ctime(time.time()))


games = [["Elden Ring", "time", ["on", "off", "off", "off", "off"], "game_directory", "resave_directory", "cur_save_dir"]]

import os
import subprocess

# Формируем путь с заменой переменной среды
path = os.path.expandvars(r"%USERPROFILE%\Documents\Horizon Zero Dawn")
path = os.path.expandvars(r"%USERPROFILE%\AppData\Local\FactoryGame\Saved\SaveGames")


# Проверяем существование папки
if os.path.exists(path):
    # Открываем проводник
    subprocess.Popen(f'explorer "{path}"')
else:
    print(f"Папка не найдена: {path}")

os.listdir()