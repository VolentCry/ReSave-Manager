games = [["Elden Ring", "5 Май 2025 18:05:56", ["on", "off", "off", "off", "off"], r"E:\Games\ELDEN RING\Game", r"%USERPROFILE%\Desktop\Programming\ReSave Manager\saves\games\Elden Ring", r"%USERPROFILE%\AppData\Roaming\EldenRing\76561197960267366"]]
user_games_name = [x[0] for x in games]

f = open("games list.txt")
a = [x.split(";") for x in f.readlines()]
f.close()


for i in a:
    if i[0] in user_games_name:
        print(i[0])