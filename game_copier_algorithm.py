import os
import subprocess
import shutil
import sys
import ctypes
from user_games import update_current_game_resaves, connect_db, take_paths, take_game_info


instruction_text = """Инструкция по дальнейшему импорту:
1. Если вы, что скорее всего, импортируйте сохранения своих игр на другое устройство, то вам потребудется скачать также последнюю версию ReSave Manager на другом устройстве.
2. Перенесите ранее вами созданный архим с экспортом игровых сохранений на ваше новое устройство.
3. Зайдите в ReSave Manager, откройте настройки, выберите пункт "Испорт игровых сохранений", после чего откроется окно проводника для выбора архива.
4. Далее дождитесь небольшой загрузки и можете наслаждаться игрой!

Огромное спасибо, что пользуйтесь нашим софтом! Будем рады если порекомендуете нас своим друзьям и знакомым! :)


Instructions for further import:
1. If you, as most likely, import your game saves to another device, then you will also need to download the latest version of ReSave Manager on the other device.
2. Transfer the previously created archive with the export of game saves to your new device.
3. Go to ReSave Manager, open the settings, select "Export game saves", after which a window will open to select the archive.
4. Then wait for a short download and you can enjoy the game!

Thank you very much for using our software! We will be glad if you recommend us to your friends and acquaintances! :)
"""

def resave_copier_algorithm(conn, game: list) -> bool:
    """Создание единичной копии игры"""
    path = os.path.expandvars(rf"{game[4]}") #Расшифровка пути к игре
    contents = os.listdir(path)

    
    if contents == []:
        # Выполняется в том случаи, если НЕТ НИ ОДНОГО РЕСЕЙВА игры
        a = fr'{os.path.expandvars(game[5])}'
        b = fr'{path}\ReSave 1\{game[5].split("\\")[-1]}'
        os.makedirs(fr'{path}\\ReSave 1', exist_ok=True) # Создаёт папку для первого ресейва
        try:
            shutil.copytree(a, b)
            return True
        except:
            return False
    else:

        update_current_game_resaves(conn, game[0])

        if game[6] < game[7] and game[7] != 0: # Проверяем не превышает ли текущее количество сохранений установленный лимит
            os.makedirs(fr'{path}\\ReSave {int(contents[-1][-1]) + 1}', exist_ok=True) # Создаёт папку для последующего ресейва
            a = fr'{os.path.expandvars(game[5])}'
            b = fr'{path}\ReSave {int(contents[-1][-1]) + 1}\{game[5].split("\\")[-1]}'
            shutil.copytree(a, b)
            return

        elif game[6] >= game[7] and game[7] != 0:
            # ПРЕВЫШЕНИЕ ЛИМИТОВ по количеству ресейвов 
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
                        try:
                            shutil.copytree(a, source_path)
                            return True
                        except:
                            return False
            return

        elif game[7] == 0: # Отсутствие лимитов по количеству ресейвов
            os.makedirs(fr'{path}\\ReSave {int(contents[-1][-1]) + 1}', exist_ok=True) # Создаёт папку для последующего ресейва
            a = fr'{os.path.expandvars(game[5])}'
            b = fr'{path}\ReSave {int(contents[-1][-1]) + 1}\{game[5].split("\\")[-1]}'
            try:
                shutil.copytree(a, b)
                return True
            except:
                return False
        return
        
        # game[6] = len(os.listdir(fr'{path}')) # Обновляем данные о количестве всего резервных копий

def game_detection():
    """Алгорит автоматического обнаружения игр на устройстве пользователя"""
    games_names = []
    games_saves_path = []
    with open("games list.txt") as f:
        for i in f.readlines():
            directory_path = os.path.expandvars(rf"{i.split(";")[1]}")
            if os.path.exists(directory_path):
                games_names.append(i.split(";")[0])
                games_saves_path.append(i.split(";")[1])
    return games_names, games_saves_path


def selective_game_resaves_export(names_of_games_to_export: list, folder_path_to_export: str):
    """
    Экспорт резервных сохранений в виде архива для дальнейшего использования пользователем.

    На вход: список названий игр, которые нужно экспортировать, путь к файлу куда экспортировать.

    В итоге будет создан архив с папками каждой игры, где будут лежать резервные копии сохранений.
    """
    conn = connect_db()
    for name in names_of_games_to_export:
        # Создания папки ReSave 0 с текущем сохранение игры.
        resave_copier_algorithm(conn, take_game_info(conn, name))
    

        path_to_resave = take_paths(conn, name)[1]
        shutil.copytree(fr"{os.path.expandvars(path_to_resave)}", fr"saves/export/{str(os.path.expandvars(path_to_resave)).split("\\")[-1]}")

        # Добавление текстового файла с интструкцией
        with open("saves/export/instruction.txt", "w") as instruction:
            instruction.write(instruction_text)

    # Создание нового ZIP-архива
    shutil.make_archive(fr'{folder_path_to_export}/games_resaves__export.zip', 'zip', r"saves/export")

    # Очистка директории export
    try:
        shutil.rmtree(r"saves/export")
        os.makedirs(r"saves/export")
    except OSError as e:
        print(f"Ошибка при очистке директории: {e}")