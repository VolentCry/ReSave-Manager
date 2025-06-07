import os

from user_games import *

path_to_exe = []

for i in os.listdir(games[0][3]):
    if str(i).endswith(".exe"):
        path_to_exe.append(rf"{games[0][3]}\{str(i)}")

print(path_to_exe)