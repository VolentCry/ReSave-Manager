import os
import subprocess
import shutil
import sys
import ctypes

# Данные пользователя
games = [["Elden Ring", "5 Май 2025 18:05:56", ["on", "off", "off", "off", "off"], r"E:\Games\ELDEN RING\Game", r"%USERPROFILE%\Desktop\Programming\ReSave Manager\saves\games\Elden Ring", r"%APPDATA%\EldenRing\76561197960267366", 0, 0, 0]]
# Структура массива под одну игру: название, последняя дата запуска, вкл/выкл параметры, директория игры, директория ресейвов, директория сейвов, кол-во текущих ресейвов, ограничение по кол-во сейвов(0 - нет ограничений), ограничение по памяти сейвов(0 - нет ограничений)

user_games_name = [x[0] for x in games]

# f = open("games list.txt")
# a = [x.split(";") for x in f.readlines()]
# f.close()

# for i in a:
#     if i[0] in user_games_name:
#         print(i[0])


def resave_copier_algorithm(game: list, num_of_game: int):
    """Создание единичной копии"""
    global games
    path = os.path.expandvars(rf"{game[4]}") #Расшифровка пути к игре
    contents = os.listdir(path)
    if contents == []: # Проверка на то, что нет ещё ни одного ресейва
        a = fr'{os.path.expandvars(game[5])}'
        b = fr'{path}\ReSave 1\{game[5].split("\\")[-1]}'
        os.makedirs(fr'{path}\\ReSave 1', exist_ok=True) # Создаёт папку для первого ресейва
        shutil.copytree(a, b)
    else:
        games[num_of_game][6] = len(os.listdir(fr'{path}')) # Обновляем данные о количестве всего резервных копий

        if game[6] < game[7] and game[7] != 0: # Проверяем не превышает ли текущее количество сохранений установленный лимит
            os.makedirs(fr'{path}\\ReSave {int(contents[-1][-1]) + 1}', exist_ok=True) # Создаёт папку для последующего ресейва
            a = fr'{os.path.expandvars(game[5])}'
            b = fr'{path}\ReSave {int(contents[-1][-1]) + 1}\{game[5].split("\\")[-1]}'
            shutil.copytree(a, b)

        elif game[6] >= game[7] and game[7] != 0: # Превышение лимитов по количеству ресейвов 
            list_of_resaves = os.listdir(fr'{path}')
            path_to_remove = fr"{path}\{list_of_resaves[0]}" # То содержимое, которое будет удалено

            try:
                shutil.rmtree(path_to_remove)
            except FileNotFoundError:
                print(f"Папка '{path_to_remove}' не найдена.")
            except OSError as e:
                print(f"Ошибка при удалении папки: {e}")
            os.makedirs(fr'{path}\\ReSave 1', exist_ok=True) # Вновь создаём папку ReSave 1
            for i in range(len(list_of_resaves)):
                # Пробегаемся по всем папкам с ресейвами
                if list_of_resaves[i] == "ReSave 1": pass
                elif i != len(list_of_resaves):
                    source_path = fr"{path}\{list_of_resaves[i]}\{os.listdir(fr"{path}\{list_of_resaves[i]}")[0]}"
                    destination_path = fr"{path}\{list_of_resaves[i - 1]}"
                    shutil.move(source_path, destination_path)
                    if i == (len(list_of_resaves) - 1):
                        source_path = fr"{path}\{list_of_resaves[i]}\{game[5].split("\\")[-1]}"
                        a = fr'{os.path.expandvars(game[5])}'
                        shutil.copytree(a, source_path)

        elif game[7] == 0: # Отсутствие лимитов по количеству ресейвов
            os.makedirs(fr'{path}\\ReSave {int(contents[-1][-1]) + 1}', exist_ok=True) # Создаёт папку для последующего ресейва
            a = fr'{os.path.expandvars(game[5])}'
            b = fr'{path}\ReSave {int(contents[-1][-1]) + 1}\{game[5].split("\\")[-1]}'
            shutil.copytree(a, b)

        games[num_of_game][6] = len(os.listdir(fr'{path}')) # Обновляем данные о количестве всего резервных копий

