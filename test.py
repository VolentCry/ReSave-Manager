import psutil

# for process in psutil.process_iter():
#     try:
#         # Получаем имя процесса
#         process_name = process.name()
#         # Получаем PID
#         process_pid = process.pid
#         # Получаем процент использования CPU
#         cpu_percent = process.cpu_percent(interval=0.5)  # Проверяем каждые 0.5 секунды
#         # Получаем использование памяти
#         memory_info = process.memory_info()

#         # Выводим информацию
#         print(f"PID: {process_pid}, Name: {process_name}, CPU: {cpu_percent}%, Memory: {memory_info.rss / (1024 * 1024)} MB")

#     except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#         pass  # Обрабатываем ошибки
    


# for process in psutil.process_iter():
#     try:
#         print(process.name().startswith("satisfactory"))
#     except:
#         pass

# import subprocess

# print(*[line.split() for line in subprocess.check_output("tasklist").splitlines()])

# import psutil
# for proc in psutil.process_iter():
#     name = proc.name()
#     print(name)
#     if "factory" in name.lower(): print(name); break

import tkinter as tk
from tkinter import filedialog

def select_folder():
    folder_path = filedialog.askdirectory(title="Выберите папку")
    if folder_path:
        label.config(text=f"Выбрано: {folder_path}")

root = tk.Tk()
root.geometry("400x200")

tk.Button(root, text="Открыть проводник", command=select_folder).pack(pady=20)
label = tk.Label(root, text="Папка не выбрана", font=("Arial", 12))
label.pack()

root.mainloop()