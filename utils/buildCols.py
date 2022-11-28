import pandas as pd
from bs4 import BeautifulSoup as bs4
import requests
import json
from plotly.express import _doc


cols = []
multiCols = []

try:
    with open("cols.txt", "r") as f:
        cols = json.loads(f.read())

    with open("multiCols.txt", "r") as f:
        multiCols = json.loads(f.read())

except:
    pass

if cols == []:
    for opt in _doc.docs:
        if (
            _doc.colref_desc in _doc.docs[opt]
            or "Either a name of a column in `data_frame`" in _doc.docs[opt][1]
        ) and opt not in cols:
            cols.append(opt)
        if (
            _doc.colref_list_desc in _doc.docs[opt]
            or "Either a list of names of columns in `data_frame`" in _doc.docs[opt][1]
        ) and opt not in cols:
            multiCols.append(opt)

    with open("cols.txt", "w") as f:
        f.write(json.dumps(cols))

    with open("multiCols.txt", "w") as f:
        f.write(json.dumps(multiCols))
