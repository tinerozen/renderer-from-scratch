

trikotniki = []

verteksi = []

with open("models/model.obj", "r") as f:
    for line in f:
        if len(line) > 1:
            line = line.split()
            if line[0] == "v":
                verteksi.append((line[1],line[2],line[3]))
            elif line[0] == "f":
                trikotniki.append((verteksi[int(line[1])-1],verteksi[int(line[2])-1],verteksi[int(line[3])-1]))


print(trikotniki)