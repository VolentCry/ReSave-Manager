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


def create_tasks_at_db(conn: Connection):
    """
    Расчитывает в какую дату будет следующее сохранение игры, после чего создаёт таск и данные о нём заносит в БД.
    """
    all_games_frequency = take_all_games_frequency(frequency_conn)
    for game_frequency in all_games_frequency:
        if "день" in game_frequency[1] or "дней" in game_frequency[1]:
            name_of_game = game_frequency[0]

            future_date = timedelta(days=int(game_frequency[1].replace("день", "").replace("дней", "")))
            now = datetime.now().replace(second=0, microsecond=0)
            date_of_resave = now + future_date
            date_of_resave = date_of_resave.replace(second=0, microsecond=0)

            period = game_frequency[1]

            try:
                conn.cursor()
                conn.execute('''INSERT INTO tasks (name_of_game, period, start_date, resave_date) VALUES (?, ?, ?, ?)''', (name_of_game, period, str(now), str(date_of_resave), ))
                conn.commit()
            except IntegrityError:
                # Таск уже создан
                pass

        elif "неделя" in game_frequency[1] or "недель" in game_frequency[1] or "недели" in game_frequency[1]:
            name_of_game = game_frequency[0]

            future_date = timedelta(days=(int(game_frequency[1].replace("неделя", "").replace("недель", "").replace("недели", "")) * 7))
            now = datetime.now().replace(second=0, microsecond=0)
            date_of_resave = now + future_date
            date_of_resave = date_of_resave.replace(second=0, microsecond=0)

            period = game_frequency[1]

            try:
                conn.cursor()
                conn.execute('''INSERT INTO tasks (name_of_game, period, start_date, resave_date) VALUES (?, ?, ?, ?)''', (name_of_game, period, str(now), str(date_of_resave), ))
                conn.commit()
            except IntegrityError:
                # Таск уже создан
                pass

        elif "месяца" in game_frequency[1] or "месяцев" in game_frequency[1]:
            name_of_game = game_frequency[0]

            future_date = relativedelta(months=int(game_frequency[1].replace("месяцев", "").replace("месяца", "")))
            now = datetime.now().replace(second=0, microsecond=0)
            date_of_resave = now + future_date
            date_of_resave = date_of_resave.replace(second=0, microsecond=0)

            period = game_frequency[1]

            try:
                conn.cursor()
                conn.execute('''INSERT INTO tasks (name_of_game, period, start_date, resave_date) VALUES (?, ?, ?, ?)''', (name_of_game, period, str(now), str(date_of_resave), ))
                conn.commit()
            except IntegrityError:
                # Таск уже создан
                pass

def create_task_to_game(name_of_game: str, conn: Connection):
    cursor = conn.cursor()
    cursor.execute("SELECT resave_date FROM tasks WHERE name_of_game = ?", (name_of_game,))
    rows = cursor.fetchall()
    conn.commit()

    task_time = rows[0][0]
    task_time = datetime.strptime(task_time, "%Y-%m-%d %H:%M:%S")
    scheduler.add_job(time_task_to_resave, 'date', run_date=task_time, args=[name_of_game])

def create_tasks_for_all_games(conn: Connection):
    names_fo_games = take_all_games_names(frequency_conn)
    for name in names_fo_games:
        create_task_to_game(name[0], conn)


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

