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
city = 'Sankt Petersburg'
bit_value = 3 # bit number for values
g = Nominatim().geocode(city, timeout=5)
position = (g.longitude, g.latitude)


# Extract raster data value at a point :
# https://gist.github.com/jdherman/dbbe3e16d488450515ac
def get_value_at_point(rasterfile, pos):
    gdata = gdal.Open(rasterfile)
    gt = gdata.GetGeoTransform()
    band = gdata.GetRasterBand(1)
    nodata = band.GetNoDataValue()     
    data = gdata.ReadAsArray().astype(np.float)
    gdata = None
    masked_data = ma.masked_values(data, nodata, copy=False) # mask no value data
    masked_data.fill_value = nodata
    d_values = np.around(masked_data, decimals=bit_value) # bit number of values
    x = int((pos[0] - gt[0])/gt[1])
    y = int((pos[1] - gt[3])/gt[5])

    return d_values[y, x]
    
# get geolocation from pixel coordinate
def pixtomap(pix):
    coordinate = (gt[3] + pix[1] * gt[4] + pix[0] * gt[5],
                  gt[0] + pix[1] * gt[1] + pix[0] * gt[2])
    return coordinate
    
def search_climate_value(rasterfile, x_value):
    global gt
    gdata = gdal.Open(rasterfile)
    gt = gdata.GetGeoTransform()
    band = gdata.GetRasterBand(1)
    nodata = band.GetNoDataValue()    
    data = gdata.ReadAsArray().astype(np.float)
    gdata = None   
    masked_data = ma.masked_values(data, nodata, copy=False) # mask no value data
    masked_data.fill_value = nodata
    d_values = np.around(masked_data, decimals=bit_value) # bit number of values
    search_pix = zip(*np.where(d_values == x_value)) # search pixel cootdinates
    for pix in search_pix:
        return pixtomap(pix)     
    
    
# WorldClim data tiff processing:

def ext_data():
    result_data = []
    val_dataset = sorted(os.listdir(path))
    for val in val_dataset: # list of datasets by climate values
        res = []
        for m in [x for x in range(1,13)]: #get data by month(from datasets like wc2.0_5m_tmax_01.tif) 
            result = get_value_at_point('data/%s/wc2.0_5m_%s_%02d.tif' % (val, val, m), position) # p -position     
            res.append(result)    
        result_data.append((val, res))
    return result_data, val_dataset
    
# Prettytable output:
def output_table(extdata):
    mgen_names = [calendar.month_name[x] for x in range(1,13)]
    table = PrettyTable()
    table.add_column("Month", mgen_names)
    for k in extdata[0]:    
        table.add_column(k[0],k[1])
    print(city, position)
    print(table)
    
    return extdata


def comparsion_climate(result_data):
    result_data = result_data[0]
    val_dataset = result_data[1]
    comparsion_result = []
    for val in result_data: # list of datasets by climate values
        if val[0] in val_dataset: # val[0] - name of climat value
            
            res = []
            for month_val in val[1]: # val[1] - monthly climate result for origin location
                m_index = val[1].index(month_val)+1 # indexes of value in reault_data
                result = search_climate_value('data/%s/wc2.0_5m_%s_%02d.tif' % (val[0], val[0], m_index), month_val)
                res.append(result)
         
            comparsion_result.append((val[0], res))
    return comparsion_result

output_table(ext_data()) # ext_data()[0] - result of search climate values
for result in comparsion_climate(output_table(ext_data())):
    print result
