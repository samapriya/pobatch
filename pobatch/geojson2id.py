from __future__ import print_function
__copyright__ = """

    Copyright 2019 Samapriya Roy

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""
__license__ = "Apache 2.0"

#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json
import csv
import os
import pyproj
from functools import partial
from planet import api
from planet.api import filters
from planet.api.auth import find_api_key
from shapely.geometry import shape
from shapely.ops import transform


try:
    PL_API_KEY = find_api_key()
except Exception as e:
    print('Failed to get Planet Key')
    sys.exit()

client = api.ClientV1(PL_API_KEY)


temp={"coordinates":[],"type":"MultiPolygon"}
tempsingle={"coordinates":[],"type":"Polygon"}
stbase={'config': [], 'field_name': [], 'type': 'StringInFilter'}
rbase={'config': {'gte': [], 'lte': []},'field_name': [], 'type': 'RangeFilter'}

# get coordinates list depth
def list_depth(dic, level = 1):
    counter = 0
    str_dic = str(dic)
    if "[[[[[" in str_dic:
        counter += 2
    elif "[[[[" in str_dic:
        counter += 1
    elif "[[[" in str_dic:
        counter += 0
    return(counter)

# Area lists
ar = []
far = []
ovall=[]

# Function to use the client and then search
def idl(**kwargs):
    for key,value in kwargs.items():
        if key=='infile' and value is not None:
            infile=value
            try:
                if infile.endswith('.geojson'):
                    with open(infile) as aoi:
                        aoi_resp = json.load(aoi)
                        for things in aoi_resp['features']:
                            ovall.append(things['geometry']['coordinates'])
                    #print(list_depth(ovall))
                    if len(ovall)>1:
                        aoi_geom=ovall
                    else:
                        if list_depth(ovall)==0:
                            aoi_geom = ovall
                        elif list_depth(ovall)==1:
                            aoi_geom = ovall[0]
                        elif list_depth(ovall)==2:
                            aoi_geom = ovall[0][0]
                        else:
                            print('Please check GeoJSON: Could not parse coordinates')
                    aoi_geom==aoi_geom
                    #print(aoi_geom)
                elif infile.endswith('.json'):
                    with open (infile) as aoi:
                        aoi_resp=json.load(aoi)
                        aoi_geom=aoi_resp['config'][0]['config']['coordinates']
                elif infile.endswith('.kml'):
                    getcoord=kml2coord(infile)
                    aoi_geom=getcoord
            except Exception as e:
                print('Could not parse geometry')
                print(e)
        if key=='item' and value is not None:
            try:
                item=value
            except Exception as e:
                sys.exit(e)
        if key=='start' and value is not None:
            try:
                start=value
                st = filters.date_range('acquired', gte=start)
            except Excpetion as e:
                sys.exit(e)
        if key=='end' and value is not None:
            end=value
            ed=filters.date_range('acquired', lte=end)
        if key == 'asset' and value  is not None:
            try:
                asset=value
            except Exception as e:
                sys.exit(e)
        if key == 'cmin':
            if value ==None:
                try:
                    cmin=0
                except Exception as e:
                    print(e)
            if value  is not None:
                try:
                    cmin=float(value)
                except Exception as e:
                    print(e)
        if key == 'cmax':
            if value ==None:
                try:
                    cmax=1
                except Exception as e:
                    print(e)
            elif value  is not None:
                try:
                    cmax=float(value)
                except Exception as e:
                    print(e)
        if key=='num':
            if value is not None:
                num=value
            elif value==None:
                num=1000000
        if key == 'outfile' and value is not None:
            outfile=value
            try:
                open(outfile, 'w')
            except Exception as e:
                sys.exit(e)
        if key == 'ovp':
            if value is not None:
                ovp=int(value)
            elif value == None:
                ovp=1
        if key== 'filters' and value is not None:
            for items in value:
                ftype=items.split(':')[0]
                if ftype=='string':
                    try:
                        fname=items.split(':')[1]
                        fval=items.split(':')[2]
                        #stbase={'config': [], 'field_name': [], 'type': 'StringInFilter'}
                        stbase['config']=fval.split(',')#fval
                        stbase['field_name']=fname
                    except Exception as e:
                        print(e)
                elif ftype=='range':
                    fname=items.split(':')[1]
                    fgt=items.split(':')[2]
                    flt=items.split(':')[3]
                    #rbase={'config': {'gte': [], 'lte': []},'field_name': [], 'type': 'RangeFilter'}
                    rbase['config']['gte']=int(fgt)
                    rbase['config']['lte']=int(flt)
                    rbase['field_name']=fname

    print('Running search for a maximum of: ' + str(num) + ' assets')
    l=0
    [head,tail]=os.path.split(outfile)
    if len(ovall)>1:
        temp={"coordinates":[],"type":"MultiPolygon"}
        temp['coordinates']=aoi_geom
    else:
        temp=tempsingle
        temp['coordinates']=aoi_geom
    #print(temp)
    sgeom=filters.geom_filter(temp)
    aoi_shape = shape(temp)
    date_filter = filters.date_range('acquired', gte=start,lte=end)
    cloud_filter = filters.range_filter('cloud_cover', gte=cmin,lte=cmax)
    asset_filter=filters.permission_filter('assets.'+str(asset)+':download')
    # print(rbase)
    # print(stbase)
    if len(rbase['field_name']) !=0 and len(stbase['field_name']) !=0:
        and_filter = filters.and_filter(date_filter, cloud_filter,asset_filter,sgeom,stbase,rbase)
    elif len(rbase['field_name']) ==0 and len(stbase['field_name']) !=0:
        and_filter = filters.and_filter(date_filter, cloud_filter,asset_filter,sgeom,stbase)
    elif len(rbase['field_name']) !=0 and len(stbase['field_name']) ==0:
        and_filter = filters.and_filter(date_filter, cloud_filter,asset_filter,sgeom,rbase)
    elif len(rbase['field_name']) ==0 and len(stbase['field_name'])==0:
        and_filter = filters.and_filter(date_filter, cloud_filter,asset_filter,sgeom)
    item_types = [item]
    req = filters.build_search_request(and_filter, item_types)
    res = client.quick_search(req)
    for things in res.items_iter(1000000): # A large number as max number to check against
        itemid=things['id']
        footprint = things["geometry"]
        s = shape(footprint)
        if item.startswith('SkySat'):
            epsgcode='3857'
        else:
            epsgcode=things['properties']['epsg_code']
        if aoi_shape.area>s.area:
            intersect=(s).intersection(aoi_shape)
        elif s.area>=aoi_shape.area:
            intersect=(aoi_shape).intersection(s)
        proj = partial(pyproj.transform, pyproj.Proj(init='epsg:4326'),
            pyproj.Proj(init='epsg:'+str(epsgcode)))
        print('Processing ' + str(len(ar) + 1) + ' items', end='\r')
        if transform(proj,aoi_shape).area>transform(proj,s).area:
            if (transform(proj,intersect).area/transform(proj,s).area*100)>=ovp:
                ar.append(transform(proj,intersect).area/1000000)
                far.append(transform(proj,s).area/1000000)
                with open(outfile,'a') as csvfile:
                    writer=csv.writer(csvfile,delimiter=',',lineterminator='\n')
                    writer.writerow([itemid])
        elif transform(proj,s).area>transform(proj,aoi_shape).area:
            if (transform(proj,intersect).area/transform(proj,aoi_shape).area*100)>=ovp:
                ar.append(transform(proj,intersect).area/1000000)
                far.append(transform(proj,s).area/1000000)
                with open(outfile,'a') as csvfile:
                    writer=csv.writer(csvfile,delimiter=',',lineterminator='\n')
                    writer.writerow([itemid])
        if int(len(ar))==int(num):
            break
    num_lines = sum(1 for line in open(os.path.join(head,tail.split('.')[0]+'.csv')))
    print('Total number of assets written to '+str(os.path.join(head,tail.split('.')[0]+'.csv')+' ===> '+str(num_lines)))
    print('Total estimated cost to quota: ' + str("{:,}".format(round(sum(far)))) + ' sqkm')
    print('Total estimated cost to quota if clipped: ' + str("{:,}".format(round(sum(ar)))) + ' sqkm')

# idl(infile=r"C:\Users\samapriya\Downloads\vertex.geojson",item='PSScene4Band',asset='analytic',cmin=0.0,cmax=0.9,start='2018-01-01',end='2019-12-31',ovp=8,num=40,outfile=r'C:\planet_demo\vertexidl.csv')
