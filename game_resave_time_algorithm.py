"""
Здесь будут все алгоритмы, которые отвечают за сохранение резервных копий игр в определённый пмомент времени, исходя из установленного таймера
"""

from apscheduler.schedulers.background import BackgroundScheduler
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
from sqlite3 import Connection, IntegrityError

from user_games import connect_db, take_game_info, take_all_games_frequency, take_all_games_names
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


def create_task_to_game(name_of_game: str, conn: Connection):
    cursor = conn.cursor()
    cursor.execute("SELECT frequency_resave FROM games WHERE name_of_game = ?", (name_of_game,))
    rows = cursor.fetchall()
    conn.commit()

    period = rows[0][0]

    if "день" in period or "дней" in period:
        period = int(period.replace("день", "").replace("дней", ""))
    elif "неделя" in period or "недель" in period or "недели" in period:
        period = int(period.replace("неделя", "").replace("недель", "").replace("недели", "")) * 7
    elif "месяца" in period or "месяцев" in period:
        period = int(period.replace("месяцев", "").replace("месяца", "")) * 30
    scheduler.add_job(time_task_to_resave, 'interval', days=period, args=[name_of_game])


def create_tasks_for_all_games(conn: Connection):
    """Создаёт таски с систематическим ресейвом кажд"""
    names_fo_games = take_all_games_names(frequency_conn)
    for name in names_fo_games:
        create_task_to_game(name[0], conn)


def process_start_check(conn: Connection):
    """Проверка на то, запущен ли процесс ресейва для каждой игры"""
    all_names_of_games = take_all_games_names(frequency_conn)
    jobs_list = [scheduler.get_job(y).args for y in [x.id for x in scheduler.get_jobs()]]
    for name in all_names_of_games:
        if name in jobs_list: 
            print(f"Процесс {name[0]} запущен.")
        else: 
            print(f"Процесс {name[0]} не запущен.")
            create_task_to_game(name[0], conn)


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

