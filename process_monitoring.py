import asyncio
import psutil
import os
from datetime import datetime
import logging
from time import time, ctime

from user_games import *
from game_copier_algorithm import resave_copier_algorithm

LOG_FILE = 'process_monitor.log'


# games_frame_ref = None

# def set_games_frame_ref(ref):
#     global games_frame_ref
#     games_frame_ref = ref

# === Callback для обработки событий закрытия ===
def on_program_closed(program_name: str, end_time: datetime, runtime, target_path: str):
    conn = connect_db()
    try:
        global history_time_of_resave_game
        print(f"[INFO] Программа '{program_name}' закрыта в {end_time}, общее время работы: {runtime}")
        
        name_of_game = find_path_exe(conn, target_path)
        if not name_of_game:
            print(f"[WARNING] Не удалось найти игру для exe: {target_path}")
            return
            
        parametrs = take_parametrs(conn, name_of_game)
        update_last_date(conn, name_of_game, end_time)
        
        if parametrs and parametrs[2] == "on":
            print(f"[INFO] Сохранение после каждой игровой сессии включено для игры {name_of_game}")
            game_info = take_game_info(conn, name_of_game)
            if game_info:
                resave_copier_algorithm(conn, game_info)
    finally:
        conn.close()


# === Мониторинг процесса ===
async def monitor_process(target_path: str, check_interval_in_seconds: int):

    # === Настройка логгера ===
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=LOG_FILE,
        filemode='a',
        encoding="UTF-8"
    )
    logger = logging.getLogger(__name__)

    if not os.path.isfile(target_path):
        logger.error(f"Файл {target_path} не существует.")
        return

    running = False
    start_time = None
    program_name = os.path.basename(target_path)

    logger.info(f"Начато наблюдение за программой: {program_name}")

    while True:
        found = False
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                if proc.info['exe'] and os.path.samefile(proc.info['exe'], target_path):
                    found = True
                    if not running:
                        start_time = datetime.fromtimestamp(proc.create_time())
                        logger.info(f"Программа {program_name} запущена. Время запуска: {start_time}")
                        running = True
                    break
            except Exception as e:
                continue

        if running and not found:
            end_time = datetime.now()
            runtime = end_time - start_time
            logger.info(f"Программа {program_name} завершила работу. "
                        f"Время завершения: {end_time}. Общее время работы: {runtime}")

            # Вызов обработчика закрытия
            on_program_closed(program_name, end_time, runtime, target_path)

            running = False

        await asyncio.sleep(check_interval_in_seconds)

# === Основная асинхронная задача ===
async def a_main(list_of_game_paths: list):
    tasks = [asyncio.create_task(monitor_process(path, 1)) for path in list_of_game_paths]
    await asyncio.gather(*tasks)