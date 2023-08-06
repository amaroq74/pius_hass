#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import time
import socket
import urllib.request
from urllib.parse import urlparse
from datetime import datetime, timedelta
import re
from googletrans import Translator, constants

Expanded = {'Gn '  : ['Genesis ',       'Génesis ' ],
            'Ex '  : ['Exodus ',        'Éxodo ' ],
            'Lv '  : ['Leviticus ',     'Levítico ' ],
            'Nu '  : ['Numbers ',       'Números ' ],
            'Dn '  : ['Daniel ',        'Daniel ' ],
            'Dt '  : ['Deuteronomy ',   'Deuteronomio ' ],
            'Jos ' : ['Joshua ',        'Josué ' ],
            'Jgs ' : ['Judges ',        'Jueces ' ],
            'Ru '  : ['Ruth ',          'Rut ' ],
            'Sm '  : ['Samuel ',        'Samuel ' ],
            'Ki '  : ['Kings ',         'Reyes ' ],
            'Ch '  : ['Chronicles ',    'Crónicas ' ],
            'Ezr ' : ['Ezra ',          'Esdras ' ],
            'Ne '  : ['Nehemiah ',      'Nehemías ' ],
            'Tb '  : ['Tobit ',         'Tobías ' ],
            'Jth ' : ['Judith ',        'Judit ' ],
            'Es '  : ['Esther ',        'Ester ' ],
            'Ma '  : ['Maccabees ',     'Macabeos ' ],
            'Jb '  : ['Job ',           'Job ' ],
            'PS '  : ['Psalms ',        'Salmos ' ],
            'Ps '  : ['Psalms ',        'Salmos ' ],
            'Pr '  : ['Proverbs ',      'Proverbios ' ],
            'Ec '  : ['Ecclesiastes ',  'Eclesiastés ' ],
            'Sg '  : ['Song of Songs ', 'Cantar de los Cantares ' ],
            'Ws '  : ['Wisdom ',        'Sabiduría ' ],
            'Sir ' : ['Sirach ',        'Sirácides ' ],
            'Is '  : ['Isaiah ',        'Isaías ' ],
            'Je '  : ['Jeremiah ',      'Jeremías ' ],
            'La '  : ['Lamentations ',  'Lamentaciones ' ],
            'Ba '  : ['Baruch ',        'Baruc ' ],
            'Ezr ' : ['Ezekiel ',       'Ezequiel ' ],
            'Da '  : ['Daniel ',        'Daniel ' ],
            'Ho '  : ['Hosea ',         'Oseas ' ],
            'Jl '  : ['Joel ',          'Joel ' ],
            'Am '  : ['Amos ',          'Amós ' ],
            'Ob '  : ['Obadiah ',       'Abdías ' ],
            'Jon ' : ['Jonah ',         'Jonás ' ],
            'Mi '  : ['Micah ',         'Miqueas ' ],
            'Na '  : ['Nahum ',         'Nahún ' ],
            'Hb '  : ['Habakkuk ',      'Habacuc ' ],
            'Zep ' : ['Zephaniah ',     'Sofonías ' ],
            'Hg '  : ['Haggai ',        'Ageo ' ],
            'Zec ' : ['Zechariah ',     'Zacarías ' ],
            'Ml '  : ['Malachi ',       'Malaquías ' ],
            'Mt '  : ['Matthew ',       'Mateo ' ],
            'Mk '  : ['Mark ',          'Marcos ' ],
            'Lu '  : ['Luke ',          'Lucas ' ],
            'Jo '  : ['John ',          'Juan ' ],
            'Ac '  : ['Acts ',          'Hechos ' ],
            'Acts ': ['Acts ',          'Hechos ' ],
            'Ro '  : ['Romans ',        'Romanos ' ],
            'Rom ' : ['Romans ',        'Romanos ' ],
            'Cor ' : ['Corinthians ',   'Corintios ' ],
            'Ga '  : ['Galatians ',     'Gálatas ' ],
            'Ep '  : ['Ephesians ',     'Efesios ' ],
            'Php ' : ['Philippians ',   'Filipenses ' ],
            'Co '  : ['Colossians ',    'Colosenses ' ],
            'Th '  : ['Thessalonians ', 'Tesalonicenses ' ],
            'Tm '  : ['Timothy ',       'Timoteo ' ],
            'Ti '  : ['Titus ',         'Tito ' ],
            'Phm ' : ['Philemon ',      'Filemón ' ],
            'He '  : ['Hebrews ',       'Hebreos ' ],
            'Heb ' : ['Hebrews ',       'Hebreos ' ],
            'Ja '  : ['James ',         'Santiago ' ],
            'Pt '  : ['Peter ',         'Pedro ' ],
            'Jn '  : ['John ',          'Juan ' ],
            'Ju '  : ['Jude ',          'Judas ' ],}

values = {'first' :  {'search' : 'Reading 1 <',        'num' : None, 'val' : ["", ""]},
          'psalm' :  {'search' : 'Responsorial Psalm', 'num' : None, 'val' : ["", ""]},
          'second' : {'search' : 'Reading 2 <',        'num' : None, 'val' : ["", ""]},
          'gospel' : {'search' : 'Gospel',             'num' : None, 'val' : ["", ""]}, }

headline = ''

translator = Translator()

now = datetime.now()

# Handle special case for Saturday evening mass
if now.weekday() == 5 and now.hour > 15:
    now = datetime.now() + timedelta(hours=24)

dte = now.strftime("%m%d%y")
fmtDte = now.strftime("%A %B %-d, %Y")
tran = translator.translate(fmtDte,src='en',dest='es')
fmtDteSp = tran.text.title()

page = urllib.request.urlopen(f"https://bible.usccb.org/bible/readings/{dte}.cfm")
lines = page.read().decode('UTF-8').split('\n')

for i,line in enumerate(lines):
    for k,v in values.items():
        if v['search'] in line:
            v['num'] = i
        if 'headline' in line:
            fields = line.split(':')
            headline = fields[1].replace('",','').replace('"','')

tran = translator.translate(headline,src='en',dest='es')
headlineSp = tran.text

for k,v in values.items():
    if v['num'] is not None:
        v['val'][0] = re.findall(r'(?:>)(.*?)$',lines[v['num']+2], flags=re.M)[0].rstrip().replace("</a>","")

    if v['val'][0] == "":
        v['val'][0] = "None Today"

    v['val'][1] = v['val'][0]

for ek,ev in Expanded.items():
    for k,v in values.items():
        for i in range(2):
            if ek in v['val'][i]:
                v['val'][i] = v['val'][i].replace(ek,ev[i])

print(f"HeadlineEn: {headline}")
print(f"HeadlineSp: {headlineSp}")
print(f"DateEn: {fmtDte}")
print(f"DateSp: {fmtDteSp}")
for k,v in values.items():
    print(f"{k}: {v['val']}")

print(f"Last: {now}")

client = mqtt.Client("readings")
client.connect('127.0.0.1')
client.publish('readings/first',values['first']['val'][0])
client.publish('readings/psalm',values['psalm']['val'][0])
client.publish('readings/second',values['second']['val'][0])
client.publish('readings/gospel',values['gospel']['val'][0])
client.publish('readings/headline', headline)
client.publish('readings/last', str(now))

with open("/srv/http/readings/current.csv","w") as f:
    f.write('First,Psalm,Second,Gospel,Date,Headline\n')

    for k in ['first', 'psalm', 'second', 'gospel']:
        v = values[k]['val'][0]
        f.write(f'"{v}",')
    f.write(f'"{fmtDte}","{headline}"\n')

    for k in ['first', 'psalm', 'second', 'gospel']:
        v = values[k]['val'][1]
        f.write(f'"{v}",')
    f.write(f'"{fmtDteSp}","{headlineSp}"\n')

time.sleep(1)

