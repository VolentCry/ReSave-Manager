"""
Здесь будут все алгоритмы, которые отвечают за сохранение резервных копий игр в определённый пмомент времени, исходя из установленного таймера
"""

from apscheduler.schedulers.background import BackgroundScheduler
import time
from datetime import datetime, timedelta
import logging
import sqlite3
from sqlite3 import Connection

from user_games import take_frequency_resave, connect_db, take_game_info, take_all_games_frequency
from game_copier_algorithm import resave_copier_algorithm
from process_monitoring import LOG_FILE

frequency_conn = connect_db()
scheduler = BackgroundScheduler()

# === Настройка логгера ===
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
    filemode='a'
)
logger = logging.getLogger(__name__)


def time_task_to_resave(name_of_game: str):
    """
    Функция делает резервную копию игры по заданному распсианию расписанию

    На вход: названия игры (str)
    """

    logger.debug(f"Задача по запланированному ресейву {name_of_game} выполняется!", time.strftime("%H:%M:%S"))

    result = resave_copier_algorithm(take_game_info(frequency_conn, name_of_game))

    if result == True:
        logger.info(f"Копия {name_of_game} выполнена успешно и по расписанию!")
    else:
        logger.error(f"Возниколи неизвестные проблемы во время копирования игры {name_of_game}!")


def create_tasks_at_db(conn: Connection):
    """
    Расчитывает в какую дату будет следующее сохранение игры, после чего создаёт таск и данные о нём заносит в БД.
    """
    all_games_frequency = take_all_games_frequency(frequency_conn)
    for game_frequency in all_games_frequency:
        if "день" in game_frequency[1] or "дней" in game_frequency[1]:
            future_date = timedelta(days=int(game_frequency[1].replace("день", "").replace("дней", "")))
            now = datetime.now()
            print(game_frequency[0], datetime.now(), now + future_date)

            conn.cursor()


        elif "час" in game_frequency[1] or "часов" in game_frequency[1]:
            ...
            
    
create_tasks_at_db()





# # Добавляем задачу (каждые 5 секунд)
# scheduler.add_job(job, 'interval', seconds=5)

# # Запускаем планировщик (начинает работать в фоне)
# scheduler.start()

# # Основной поток продолжает работать
# try:
#     while True:
#         print("Основной поток работает...", time.strftime("%H:%M:%S"))
#         time.sleep(1)
# except (KeyboardInterrupt, SystemExit):
#     # Останавливаем планировщик при прерывании
#     scheduler.shutdown()

# # Каждый день в 12:30
# scheduler.add_job(job, 'cron', hour=12, minute=30)

# # Запустить задачу 25 декабря 2024 года в 12:00
# task_time = datetime(2024, 12, 25, 12, 0)
# scheduler.add_job(job, 'date', run_date=task_time)

