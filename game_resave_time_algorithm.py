"""
Здесь будут все алгоритмы, которые отвечают за сохранение резервных копий игр в определённый пмомент времени, исходя из установленного таймера
"""

from apscheduler.schedulers.background import BackgroundScheduler
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
from sqlite3 import Connection, IntegrityError

from user_games import *
from game_copier_algorithm import resave_copier_algorithm
from process_monitoring import LOG_FILE

scheduler = BackgroundScheduler()

# === Настройка логгера ===
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
    filemode='a',
    encoding="UTF-8"
)
logger = logging.getLogger(__name__)


def time_task_to_resave(name_of_game: str):
    """
    Функция делает резервную копию игры по заданному распсианию расписанию

    На вход: названия игры (str)
    """

    conn = connect_db()
    try:
        logger.debug(f"Задача по запланированному ресейву {name_of_game} выполняется!", time.strftime("%H:%M:%S"))

        # ИЗМЕНЕНО: Используем локальное 'conn' и передаем его дальше
        game_info = take_game_info(conn, name_of_game)
        if game_info:
            result = resave_copier_algorithm(conn, game_info)
            if result:
                logger.info(f"Копия {name_of_game} выполнена успешно и по расписанию!")
            else:
                logger.error(f"Возникли неизвестные проблемы во время копирования игры {name_of_game}!")
    finally:
        # ДОБАВЛЕНО: Гарантированно закрываем соединение
        conn.close()


def make_future_resave_date(period: str) -> tuple[int, datetime]:
    """ Вовзращает в числовом формате кол-во дней, именно с таким периодом будут создаваться автоматические резервные копии игры. 
    А также возвращает дату в формате datetime, в эту дату должно произойти авто резервное копирование игры """
    if "день" in period or "дней" in period:
        # Установка автосохранения по дням
        new_period = int(period.replace("день", "").replace("дней", ""))

        now = datetime.now().replace(second=0, microsecond=0) # Текущая дата
        future_date = timedelta(days=new_period)
        date_of_resave = now + future_date
        date_of_resave = date_of_resave.replace(second=0, microsecond=0)

    elif "неделя" in period or "недель" in period or "недели" in period:
        # Установка автосохранения по неделям
        new_period = int(period.replace("неделя", "").replace("недель", "").replace("недели", "")) * 7

        now = datetime.now().replace(second=0, microsecond=0) # Текущая дата
        future_date = timedelta(days=new_period)
        date_of_resave = now + future_date
        date_of_resave = date_of_resave.replace(second=0, microsecond=0)

    elif "месяца" in period or "месяцев" in period:
        # Установка автосохранения по месяцам
        new_period = int(period.replace("месяцев", "").replace("месяца", "")) * 30

        now = datetime.now().replace(second=0, microsecond=0) # Текущая дата
        future_date = timedelta(days=new_period)
        date_of_resave = now + future_date
        date_of_resave = date_of_resave.replace(second=0, microsecond=0)
    
    return new_period, date_of_resave


def create_task_to_game(name_of_game: str, conn: Connection):
    """ Создаёт таску по авто резервному копированию с определённым периодом для определённой игры """
    cursor = conn.cursor()
    cursor.execute("SELECT frequency_resave FROM games WHERE name_of_game = ?", (name_of_game,))
    rows = cursor.fetchall()
    conn.commit()

    # Период автосохранения игры
    period = rows[0][0]
    period_to_info = period

    # if "день" in period or "дней" in period:
    #     # Установка автосохранения по дням
    #     period = int(period.replace("день", "").replace("дней", ""))

    #     now = datetime.now().replace(second=0, microsecond=0) # Текущая дата
    #     future_date = timedelta(days=period)
    #     date_of_resave = now + future_date
    #     date_of_resave = date_of_resave.replace(second=0, microsecond=0)

    # elif "неделя" in period or "недель" in period or "недели" in period:
    #     # Установка автосохранения по неделям
    #     period = int(period.replace("неделя", "").replace("недель", "").replace("недели", "")) * 7

    #     now = datetime.now().replace(second=0, microsecond=0) # Текущая дата
    #     future_date = timedelta(days=period)
    #     date_of_resave = now + future_date
    #     date_of_resave = date_of_resave.replace(second=0, microsecond=0)

    # elif "месяца" in period or "месяцев" in period:
    #     # Установка автосохранения по месяцам
    #     period = int(period.replace("месяцев", "").replace("месяца", "")) * 30

    #     now = datetime.now().replace(second=0, microsecond=0) # Текущая дата
    #     future_date = timedelta(days=period)
    #     date_of_resave = now + future_date
    #     date_of_resave = date_of_resave.replace(second=0, microsecond=0)

    period, date_of_resave = make_future_resave_date(period)

    # Добавляем таск в текущие задачи
    scheduler.add_job(time_task_to_resave, 'interval', days=period, args=[name_of_game])
    logger.info(f"Создан таск для игры {name_of_game} с частотой {period_to_info}.")

    try:
        # Вносим данные о новом таске в таблицу
        conn.cursor()
        conn.execute('''INSERT INTO tasks (name_of_game, period, future_date) VALUES (?, ?, ?)''', (name_of_game, period_to_info, str(date_of_resave), ))
        conn.commit()
    except IntegrityError:
        logger.warning(f"Таск для игры {name_of_game} уже был создан ранее. Ложный вызов.")


def create_tasks_for_all_games(conn: Connection):
    """Создаёт таски с систематическим ресейвом кажд"""
    names_fo_games = take_all_games_names(conn)
    for name in names_fo_games:
        create_task_to_game(name[0], conn)


def process_start_check(conn: Connection):
    """Проверка на то, запущен ли процесс ресейва для каждой игры"""
    all_names_of_games = take_all_games_names(conn)
    jobs_list = [scheduler.get_job(y).args for y in [x.id for x in scheduler.get_jobs()]]
    
    for name in all_names_of_games:
        cursor = conn.cursor()
        cursor.execute("SELECT future_date FROM tasks WHERE name_of_game = ?", (name[0],))
        rows = cursor.fetchall()
        conn.commit()
        
        date_now_datetype = datetime.now() # текущее время
        date_future_datetype = datetime.strptime(rows[0][0], "%Y-%m-%d %H:%M:%S")

        if name in jobs_list:
            logger.info(f"Процесс {name[0]} запущен.")

            # if date_future[0] >= date_now[0] and date_future[1] >= date_now[1]:
            if date_now_datetype <= date_future_datetype:
                ...
            else: # Исходя из провреки мы поняли, что так как программа не была запущена, то мы пропустили необходимую проверку, поэтому делаем резервную копию игры вручную
                resave_copier_algorithm(conn, take_game_info(conn, name[0]))
                logger.info(f"Резервная копия сохранения игры {name[0]} была сделана вручную, т. к. во время необходимого запланированного резервного копирования приложение было закрыто по тем или иным причинам.")

                # Период автосохранения игры
                cursor = conn.cursor()
                cursor.execute("SELECT frequency_resave FROM games WHERE name_of_game = ?", (name[0],))
                period = cursor.fetchall()[0][0]

                new_period, date_of_resave = make_future_resave_date(period) # Получаем дату для записи в БД
                update_frequency_resave(conn, name[0], str(date_of_resave))

        else:
            create_task_to_game(name[0], conn)
            print(f"Процесс {name[0]} был не запущен, но теперь стартовал.")


def initialize_scheduler_tasks():
    """
    Создает временное подключение к БД для начальной настройки
    и проверки всех запланированных задач.
    """
    conn = connect_db()
    try:
        print("[INFO] Инициализация и проверка запланированных задач...")
        create_tasks_for_all_games(conn)
        process_start_check(conn)
        print("[INFO] Инициализация завершена.")
    finally:
        conn.close()

# Запускаем сам планировщик (он работает в фоне и не требует постоянного соединения)
scheduler.start()

# 4. Вызываем нашу новую функцию для запуска
# Это произойдет один раз при старте приложения
initialize_scheduler_tasks()



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

