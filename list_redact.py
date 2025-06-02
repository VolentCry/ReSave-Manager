f = open("pupa.txt", encoding='utf-8')
a = [x for x in f.readlines()]
f.close()

for game in a:
    x = game.replace("\n", "")
    x = x[game.replace("\n", "").index(" ")+1:]
    name_of_game = x[:x.index("%")-1]
    x = x[x.index("%"):]
    x = x[::-1]
    size = x[:x.index(" ", 3)]
    size = size[::-1]
    size = size[:-3]
    x = x[x.index(" ", 3)+1:]
    x = x[::-1]
    path = x.replace(" ", "")
    # print(f"{name_of_game};{path};{size};")

    with open("games list.txt", "a", encoding='utf-8') as f:
        f.write(f"{name_of_game};{path};{size};\n")