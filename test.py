# import psutil
# import time
# import os

# def monitor_process_lifecycle(process_path, interval=1):
#     tracked_pids = set()
#     while True:
#         current_pids = set()
#         for proc in psutil.process_iter(['pid', 'exe']):
#             try:
#                 pid = proc.info['pid']
#                 exe_path = proc.info['exe']
#                 if exe_path and os.path.normcase(exe_path) == os.path.normcase(process_path):
#                     current_pids.add(pid)
#                     if pid not in tracked_pids:
#                         print(f"Программа {exe_path} запущена.")
#             except (psutil.NoSuchProcess, psutil.AccessDenied):
#                 continue
#         # Проверяем завершённые процессы
#         for pid in tracked_pids - current_pids:
#             print(f"Программа {process_path} закрыта.")
#         tracked_pids = current_pids
#         time.sleep(interval)

# # Пример использования:
# # monitor_process_lifecycle(r'C:\Windows\System32\notepad.exe')


# monitor_process_lifecycle("C:\Program Files\HoYoPlay\launcher.exe")

import psutil
import time
import os
from datetime import datetime

def monitor_process(target_path):
    if not os.path.isfile(target_path):
        print(f"Файл {target_path} не существует.")
        return

    target_filename = os.path.basename(target_path)
    running = False
    start_time = None

    print(f"Начато наблюдение за программой: {target_path}")

    while True:
        found = False
        for proc in psutil.process_iter(['pid', 'name', 'create_time', 'exe']):
            try:
                # Проверяем имя и путь процесса
                if proc.info['exe'] and os.path.samefile(proc.info['exe'], target_path):
                    found = True
                    if not running:
                        start_time = datetime.fromtimestamp(proc.info['create_time'])
                        print(f"Программа {target_path} запущена. Время запуска: {start_time}")
                        running = True
                    break  # Выходим из цикла, если нашли процесс
            except: pass

        if running and not found:
            end_time = datetime.now()
            runtime = end_time - start_time
            print(f"Программа {target_path} завершила работу. "
                  f"Время завершения: {end_time}. "
                  f"Общее время работы: {runtime}")
            break  # Выход из цикла после завершения программы

        time.sleep(1)  # Интервал проверки (в секундах)

monitor_process(r"E:\Games\IGG-Welcome.to.the.Game\WTTG.exe")