#!/usr/bin/env python
# -*- coding: utf-8 -*-

from osgeo import gdal
from geopy.geocoders import Nominatim
from collections import OrderedDict
from prettytable import PrettyTable
import calendar
import os
import numpy as np

path = 'data'
city = 'Moscow'
g = Nominatim().geocode(city, timeout=5)
p = (g.longitude, g.latitude)


# Extract raster data value at a point :
# https://gist.github.com/jdherman/dbbe3e16d488450515ac
def get_value_at_point(rasterfile, pos):
    gdata = gdal.Open(rasterfile)
    gt = gdata.GetGeoTransform()
    data = gdata.ReadAsArray().astype(np.float)
    gdata = None
    x = int((pos[0] - gt[0])/gt[1])
    y = int((pos[1] - gt[3])/gt[5])

    return data[y, x]

# WorldClim data tiff processing:

result_data = []
for val in sorted(os.listdir(path)): # list of datasets by climate values
    res = []
    for m in [x for x in range(1,13)]: #get data by month(from datasets like wc2.0_5m_tmax_01.tif) 
        result = get_value_at_point('data/%s/wc2.0_5m_%s_%s.tif' % (val, val, '{:02d}'.format(m)), p) # p -position     
        res.append(result)    
    result_data.append((val, res))

# Prettytable output:

mgen_names = [calendar.month_name[x] for x in range(1,13)]
table = PrettyTable()
table.add_column("Month", mgen_names)
for k in result_data:    
    table.add_column(k[0],k[1])
print(table)
