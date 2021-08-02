from os import listdir
from os.path import isfile, join

files = [f for f in listdir('localization') if isfile(join('localization', f))][2]
lang = {}

for w in range(0, len(files)):
    lang[files[w][0:2]] = {}

for x in range(0, len(lang)):
    languages = list(lang.keys())
    with open("localization/%s.txt" % languages[x], encoding='utf-8') as conf:
        for line in conf:
            if " = " in line:
                name, value = line.split(" = ")
                lang[languages[x]][name] = value.rstrip()
