import os

directory_path = "%USERPROFILE%\AppData\Local\FactoryGame\Saved\SaveGames"
directory_path = os.path.expandvars(rf"{directory_path}")

if os.path.exists(directory_path):
    print(f"Директория '{directory_path}' существует.")
else:
    print(f"Директория '{directory_path}' не существует.")