import asyncio
import psutil
import os
from datetime import datetime
import logging

# === Настройка логгера ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='process_monitor.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# === Callback для обработки событий закрытия ===
def on_program_closed(program_name: str, end_time: datetime, runtime):
    print(f"[INFO] Программа '{program_name}' закрыта в {end_time}, общее время работы: {runtime}")
    # Здесь можно делать любую обработку: сохранение в базу, отправка, уведомление и т.д.

# === Мониторинг процесса ===
async def monitor_process(target_path: str, check_interval_in_seconds: int):
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
            on_program_closed(program_name, end_time, runtime)

            running = False

        await asyncio.sleep(check_interval_in_seconds)

# === Основная асинхронная задача ===
async def main(list_of_game_paths: list):
    tasks = [asyncio.create_task(monitor_process(path, 1)) for path in list_of_game_paths]
    await asyncio.gather(*tasks)

# === Пути к программам ===
games_exe_path = [
    r"C:\Users\Semen\AppData\Roaming\.tlauncher\legacy\Minecraft\TL.exe",
    r"E:\Games\The Planet Crafter (2024)\The Planet Crafter\Planet Crafter.exe",
    r"E:\Games\Untitled Goose Game\Untitled.exe"
]

# === Запуск ===
if __name__ == "__main__":
    asyncio.run(main(games_exe_path))