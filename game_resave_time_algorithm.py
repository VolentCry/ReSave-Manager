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
    """Создаёт таску для определённой игры"""
    cursor = conn.cursor()
    cursor.execute("SELECT frequency_resave FROM games WHERE name_of_game = ?", (name_of_game,))
    rows = cursor.fetchall()
    conn.commit()

    period = rows[0][0]
    period_copy = period

    if "день" in period or "дней" in period:
        period = int(period.replace("день", "").replace("дней", ""))

        now = datetime.now().replace(second=0, microsecond=0)
        future_date = timedelta(days=period)
        date_of_resave = now + future_date
        date_of_resave = date_of_resave.replace(second=0, microsecond=0)

    elif "неделя" in period or "недель" in period or "недели" in period:
        period = int(period.replace("неделя", "").replace("недель", "").replace("недели", "")) * 7

        now = datetime.now().replace(second=0, microsecond=0)
        future_date = timedelta(days=period)
        date_of_resave = now + future_date
        date_of_resave = date_of_resave.replace(second=0, microsecond=0)

    elif "месяца" in period or "месяцев" in period:
        period = int(period.replace("месяцев", "").replace("месяца", "")) * 30

        now = datetime.now().replace(second=0, microsecond=0)
        future_date = timedelta(days=period)
        date_of_resave = now + future_date
        date_of_resave = date_of_resave.replace(second=0, microsecond=0)

    scheduler.add_job(time_task_to_resave, 'interval', days=period, args=[name_of_game])
    logger.info(f"Создан таск для игры {name_of_game} с частотой {period_copy}")

    try:
        conn.cursor()
        conn.execute('''INSERT INTO tasks (name_of_game, period, future_date) VALUES (?, ?, ?)''', (name_of_game, period_copy, str(date_of_resave), ))
        conn.commit()
    except IntegrityError:
        # Таск уже создан
        pass


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
        cursor = conn.cursor()
        cursor.execute("SELECT future_date FROM tasks WHERE name_of_game = ?", (name[0],))
        rows = cursor.fetchall()
        conn.commit()

        date_future = [int(x) for x in rows[0][0].replace("-", " ").replace(":", " ").split()]
        # date_future = timedelta(rows[0], rows[1], rows[2], rows[3], rows[4], rows[5])
        date_now = [int(x) for x in datetime.now().replace(second=0, microsecond=0).strftime("%Y %m %d %H %M %S").split()]
        # date_future_timedelta = timedelta(days=date_future[2], hours=date_future[3], minutes=date_future[4])
        # date_now_timedelta = timedelta(days=date_now[2], hours=date_now[3], minutes=date_now[4])
        date_now_datetype = datetime.now()
        date_future_datetype = datetime.strptime(rows[0][0], "%Y-%m-%d %H:%M:%S")
        print(date_now_datetype > date_future_datetype)
        

        if name in jobs_list:
            print(f"Процесс {name[0]} запущен.")

            if date_future[0] >= date_now[0] and date_future[1] >= date_now[1]:
                ...
            else:
                # Исходя из провреки мы поняли, что так как программа не была запущена, то мы пропустили необходимую проверку, поэтому делаем её вручную
                resave_copier_algorithm(take_game_info(frequency_conn, name[0]))

        else:
            create_task_to_game(name[0], conn)
            print(f"Процесс {name[0]} был не запущен, но теперь стартовал.")


scheduler.start()
create_tasks_for_all_games(frequency_conn)
process_start_check(frequency_conn)

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

