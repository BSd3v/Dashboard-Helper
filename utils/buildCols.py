import pandas as pd
from bs4 import BeautifulSoup as bs4
import requests
import json


cols = []
multiCols = []

try:
    with open('cols.txt', 'r') as f:
        cols = json.loads(f.read())

    with open('multiCols.txt', 'r') as f:
        multiCols = json.loads(f.read())

except:
    pass

if cols == []:
    r = requests.get('https://plotly.com/python-api-reference/plotly.express.html')

    soup = bs4(r.content, 'lxml')
    refs = soup.find('table', {'class': 'longtable'}).findAll('a')
    for ref in refs:
        r = requests.get(f'https://plotly.com/python-api-reference/{ref["href"]}')
        try:
            l_opts = bs4(r.content, 'lxml').find('ul', {'class':'simple'}).findAll('li')
            for opt in l_opts:
                    if 'Either a name of a column in data_frame' in opt.text and opt.text.split(' ')[0] not in cols:
                        cols.append(opt.text.split(' ')[0])
                    if ('Either a list of names of columns in data_frame' in opt.text or
                    'Either names of columns in data_frame' in opt.text) and opt.text.split(' ')[0] not in multiCols:
                        multiCols.append(opt.text.split(' ')[0])
        except:
            pass

    with open('cols.txt', 'w') as f:
        f.write(json.dumps(cols))

    with open('multiCols.txt', 'w') as f:
        f.write(json.dumps(multiCols))
