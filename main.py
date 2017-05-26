#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from IPython.core.display import display, HTML #HTML output for ipython notebook
from osgeo import gdal
from geopy.geocoders import Nominatim
from collections import OrderedDict
from prettytable import PrettyTable
from prettytable import from_html
import calendar
import os
import numpy as np
from numpy import ma

path = 'data'
city = 'Arambol'
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
# get geolocation from pixel coordinate
def pixtomap(pix):
    coordinate = (gt[3] + pix[1] * gt[4] + pix[0] * gt[5],
                  gt[0] + pix[1] * gt[1] + pix[0] * gt[2])
    return coordinate

def search_climate_value(rasterfile):
    global gt
    gdata = gdal.Open(rasterfile)
    gt = gdata.GetGeoTransform()
    band = gdata.GetRasterBand(1)
    nodata = band.GetNoDataValue()    
    data = gdata.ReadAsArray().astype(np.float)
    gdata = None   
    masked_data = ma.masked_values(data, nodata, copy=False) # mask no value data
    masked_data.fill_value = nodata
    ddd = np.around(masked_data, decimals=3) # numbers after ,
    search_pix = zip(*np.where(ddd == -6.355)) # search pixel cootdinates
    for pix in search_pix:
        print pixtomap(pix)     
    
# WorldClim data tiff processing:

def ext_data():
    result_data = []
    for val in sorted(os.listdir(path)): # list of datasets by climate values
        res = []
        for m in [x for x in range(1,13)]: #get data by month(from datasets like wc2.0_5m_tmax_01.tif) 
            result = get_value_at_point('data/%s/wc2.0_5m_%s_%s.tif' % (val, val, '{:02d}'.format(m)), p) # p -position     
            res.append(result)    
        result_data.append((val, res))
    return result_data
    
# Prettytable output:
def output_table(extdata):
    mgen_names = [calendar.month_name[x] for x in range(1,13)]
    table = PrettyTable()
    table.add_column("Month", mgen_names)
    for k in extdata:    
        table.add_column(k[0],k[1])
    print(city)
    print(table)

#output_table(ext_data())
search_climate_value('data/tavg/wc2.0_5m_tavg_01.tif')
