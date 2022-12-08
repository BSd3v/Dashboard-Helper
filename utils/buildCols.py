import pandas as pd
from bs4 import BeautifulSoup as bs4
import requests
import json
from plotly.express import _doc
from plotly.express import _chart_types
from inspect import getmembers, isfunction, getargvalues, signature, isclass, ismethod
from pprint import pprint


cols = []
multiCols = []

def getColumns(selectChart):
    for i, y in getmembers(_chart_types, isfunction):
        if 'px.'+i == selectChart:
            lines = y.__doc__.split('\n')
            for l in lines:
                if ':' in l:
                    opt = l.split(':')[0]
                else:
                    if "Either a name of a column in `data_frame`" in l or _doc.colref_desc in l:
                        if opt not in cols:
                            cols.append(opt)
                    elif "Either a list of names of columns in `data_frame`" in l\
                            or _doc.colref_list_desc in l or "Either names of columns in `data_frame`" in l:
                        if opt not in multiCols:
                            multiCols.append(opt)
                    elif "can optionally be a list of column references" in l and opt != 'x':
                        if opt not in multiCols:
                            multiCols.append(opt)
    return cols, multiCols

#
# for opt in _doc.docs:
#     if (
#         _doc.colref_desc in _doc.docs[opt]
#         or "Either a name of a column in `data_frame`" in _doc.docs[opt][1]
#     ) and opt not in cols:
#         cols.append(opt)
#     if (
#         _doc.colref_list_desc in _doc.docs[opt]
#         or "Either a list of names of columns in `data_frame`" in _doc.docs[opt][1]
#     ) and opt not in multiCols:
#         multiCols.append(opt)

with open("cols.txt", "w") as f:
    f.write(json.dumps(cols))

with open("multiCols.txt", "w") as f:
    f.write(json.dumps(multiCols))
