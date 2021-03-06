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

import argparse
import subprocess
import os
import csv
import time
import requests
import sys
import json
import pkg_resources
from geojson2id import idl
from text_split import idsplit
from idlist_orders import batch_order
from msize import ordsize
from mdown import downloader
from planet.api.auth import find_api_key
from prettytable import PrettyTable
os.chdir(os.path.dirname(os.path.realpath(__file__)))
lpath=os.path.dirname(os.path.realpath(__file__))
sys.path.append(lpath)

x = PrettyTable()



# Get package version
def pobatch_version():
    print('Running porder version:' +str(pkg_resources.get_distribution("porder").version))
    print('Running pobatch version:' +str(pkg_resources.get_distribution("pobatch").version))
def version_from_parser(args):
    pobatch_version()


# Function to get user's quota
def planet_quota():
    # Get API Key: Requires user to have initialized Planet CLI
    try:
        api_key = find_api_key()
        os.environ['PLANET_API_KEY'] = find_api_key()
    except Exception as e:
        print('Failed to get Planet Key')
        sys.exit()

    '''Print allocation and remaining quota in Sqkm.'''
    try:
        main = requests.get('https://api.planet.com/auth/v1/experimental/public/my/subscriptions', auth=(api_key, ''))
        if main.status_code == 200:
            content = main.json()
            for item_id in content:
                print(" ")
                print(
                    'Subscription ID: %s'
                    % item_id['id'])
                print(
                    'Plan ID: %s'
                    % item_id['plan_id'])
                print(
                    'Allocation Name: %s'
                    % item_id['organization']['name'])
                print(
                    'Allocation active from: %s'
                    % item_id['active_from'].split("T")[0])
                print(
                    'Quota Enabled: %s'
                    % item_id['quota_enabled'])
                print(
                    'Total Quota in SqKm: %s'
                    % item_id['quota_sqkm'])
                print(
                    'Total Quota used: %s'
                    % item_id['quota_used'])
                if (item_id['quota_sqkm'])is not None:
                    leftquota = (float(
                        item_id['quota_sqkm'] - float(item_id['quota_used'])))
                    print(
                        'Remaining Quota in SqKm: %s' % leftquota)
                else:
                    print('No Quota Allocated')
                print('')
        elif main.status_code == 500:
            print('Temporary issue: Try again')
        else:
            print('Failed with exception code: ' + str(
                main.status_code))

    except IOError:
        print('Initialize client or provide API Key')


def planet_quota_from_parser(args):
    planet_quota()


# Create ID List with structured JSON
def idlist_from_parser(args):
    print('')
    if args.asset is None:
        with open(os.path.join(lpath,'bundles.json')) as f:
            r=json.load(f)
            for key,value in r['bundles'].items():
                mydict=r['bundles'][key]['assets']
                for item_types in mydict:
                    if args.item ==item_types:
                        print('Assets for item '+str(args.item)+' of Bundle type '+str(key)+': '+str(', '.join(mydict[args.item])))
        sys.exit()
    idl(infile=args.input,
        start=args.start,
        end=args.end,
        item=args.item,
        asset=args.asset,
        num=args.number,
        cmin=args.cmin,
        cmax=args.cmax,
        ovp=args.overlap,
        outfile=args.outfile,
        filters=args.filters)

# Split large idlist to smaller subparts
def idsplit_from_parser(args):
    idsplit(infile=args.idlist,linenum=args.lines,
        output=args.local)


# Get bundles
def bundles(item):
    with open(os.path.join(lpath,'bundles.json')) as f:
        r=json.load(f)
        for key,value in r['bundles'].items():
            mydict=r['bundles'][key]['assets']
            for item_types in mydict:
                if item ==item_types:
                    print('Bundle type: '+str(key)+'\n'+str(', '.join(mydict[item]))+'\n')
def bundles_from_parser(args):
    bundles(item=args.item)

# Get order status
def ordstatus(orderlist):
    print('Running Order Status check')
    # Get API Key: Requires user to have initialized Planet CLI
    try:
        api_key = find_api_key()
        os.environ['PLANET_API_KEY'] = find_api_key()
        SESSION = requests.Session()
        SESSION.auth = (api_key, '')
    except Exception as e:
        print('Failed to get Planet Key')
        sys.exit()
    with open(orderlist) as f:
        try:
            reader = csv.reader(f)
            your_list = list(reader)
            i=1
            for row in your_list:
                order_url = row[1]
                response = SESSION.get(order_url)
                if response.status_code == 200:
                    r=response.json()
                    try:
                        x.field_names = ["index","name", "status"]
                        x.add_row([i,r["name"], r['state']])
                        i=i+1
                    except Exception as e:
                        print(e)
                    time.sleep(0.3)
                elif response.status_code == 429:
                    while response.status_code == 429:
                        response = SESSION.get(order_url)
                        if response.status_code == 200:
                            r=response.json()
                            try:
                                x.field_names = ["index","name", "status"]
                                x.add_row([i,r["name"], r['state']])
                                i=i+1
                            except Exception as e:
                                print(e)
                else:
                    print(response.status_code)
        except Exception as e:
            print(e)
    print(x)

def status_from_parser(args):
    ordstatus(orderlist=args.orderlist)

#Get concurrent orders that are running
def stats():
    # Get API Key: Requires user to have initialized Planet CLI
    try:
        api_key = find_api_key()
        os.environ['PLANET_API_KEY'] = find_api_key()
    except Exception as e:
        print('Failed to get Planet Key: Try planet init')
        sys.exit()


    SESSION = requests.Session()
    SESSION.auth = (api_key, '')
    print('Checking on all running orders...')
    result = SESSION.get('https://api.planet.com/compute/ops/stats/orders/v2')
    if int(result.status_code)==200:
        page=result.json()
        try:
            print('\n'+'Total queued order for organization: '+str(page['organization']['queued_orders']))
            print('Total running orders for organization: '+str(page['organization']['running_orders']))
            print('\n'+'Total queued orders for user: '+str(page['user']['queued_orders']))
            print('Total running orders for user: '+str(page['user']['running_orders']))
        except Exception as e:
            print(e)
    elif int(result.status_code)==401:
        print('Access denied - insufficient privileges')
    elif int(result.status_code)==500:
        print('Server Error')
    else:
        print('Failed with '+str(result.status_code)+' '+str(result.text))
def stats_from_parser(args):
    stats()

#Place orders in folders
def multiorder_from_parser(args):
    batch_order(infolder=args.infolder,
        outfile = args.outfile,
        errorlog=args.errorlog,
        item = args.item,
        bundle = args.bundle,
        sid=args.sid,
        op=args.op,
        boundary=args.boundary,
        projection=args.projection,
        kernel=args.kernel,
        compression=args.compression,
        aws=args.aws,
        azure=args.azure,
        gcs=args.gcs)


# Estimate size of download
def ordsize_from_parser(args):
    ordsize(infile = args.infile)


# Download orders
def downloader_from_parser(args):
    downloader(infile = args.infile,
        folderpath = args.folder,
        method = args.method)

spacing="                               "

def main(args=None):
    parser = argparse.ArgumentParser(description='porder wrapper for Ordersv2 Batch Client')
    subparsers = parser.add_subparsers()

    parser_version = subparsers.add_parser('version', help='Prints porder version and exists')
    parser_version.set_defaults(func=version_from_parser)

    parser_planet_quota = subparsers.add_parser('quota', help='Prints your Planet Quota Details')
    parser_planet_quota.set_defaults(func=planet_quota_from_parser)

    parser_idlist = subparsers.add_parser('idlist', help='Get idlist using geometry & filters')
    required_named = parser_idlist.add_argument_group('Required named arguments.')
    required_named.add_argument('--input', help='Input geometry file for now geojson/json/kml', required=True)
    required_named.add_argument('--start', help='Start date in format YYYY-MM-DD', required=True)
    required_named.add_argument('--end', help='End date in format YYYY-MM-DD', required=True)
    required_named.add_argument('--item', help='Item Type PSScene4Band|PSOrthoTile|REOrthoTile etc', required=True)
    required_named.add_argument('--asset', help='Asset Type analytic, analytic_sr,visual etc', default=None)
    required_named.add_argument('--outfile', help='Output csv file', required=True)
    optional_named = parser_idlist.add_argument_group('Optional named arguments')
    optional_named.add_argument('--cmin', help="Minimum cloud cover", default=None)
    optional_named.add_argument('--cmax', help="Maximum cloud cover", default=None)
    optional_named.add_argument('--number', help="Total number of assets, give a large number if you are not sure", default=None)
    optional_named.add_argument('--overlap', help="Percentage overlap of image with search area range between 0 to 100", default=None)
    optional_named.add_argument('--filters', nargs='+',help="Add an additional string or range filter", default=None)
    parser_idlist.set_defaults(func=idlist_from_parser)

    parser_idsplit = subparsers.add_parser('idsplit',help='Splits ID list incase you want to run them in small batches')
    parser_idsplit.add_argument('--idlist',help='Idlist txt file to split')
    parser_idsplit.add_argument('--lines',help='Maximum number of lines in each split files')
    parser_idsplit.add_argument('--local',help='Output folder where split files will be exported')
    parser_idsplit.set_defaults(func=idsplit_from_parser)

    parser_bundles = subparsers.add_parser('bundles',help='Check bundles of assets for given item type')
    parser_bundles.add_argument('--item',help='Item type')
    parser_bundles.set_defaults(func=bundles_from_parser)

    parser_multiorder = subparsers.add_parser('multiorder', help='Place multiple orders based on idlists in folder')
    required_named = parser_multiorder.add_argument_group('Required named arguments.')
    required_named.add_argument('--infolder', help='Folder with multiple order list', required=True)
    required_named.add_argument('--outfile', help='CSV file with list of order urls', required=True)
    required_named.add_argument('--errorlog', help='Path to idlist it could not submit,error message log csv file', required=True)
    required_named.add_argument('--item', help='Item Type PSScene4Band|PSOrthoTile|REOrthoTile etc', required=True)
    required_named.add_argument('--bundle', help='Bundle Type: analytic, analytic_sr,analytic_sr_udm2', required=True)
    optional_named = parser_multiorder.add_argument_group('Optional named arguments')
    optional_named.add_argument('--sid', help='Subscription ID',default=None)
    optional_named.add_argument('--boundary', help='Boundary/geometry for clip operation geojson|json|kml',default=None)
    optional_named.add_argument('--projection', help='Projection for reproject operation of type "EPSG:4326"',default=None)
    optional_named.add_argument('--kernel', help='Resampling kernel used "near", "bilinear", "cubic", "cubicspline", "lanczos", "average" and "mode"',default=None)
    optional_named.add_argument('--compression', help='Compression type used for tiff_optimize tool, "lzw"|"deflate"',default=None)
    optional_named.add_argument('--aws', help='AWS cloud credentials config yml file',default=None)
    optional_named.add_argument('--azure', help='Azure cloud credentials config yml file',default=None)
    optional_named.add_argument('--gcs', help='GCS cloud credentials config yml file',default=None)
    optional_named.add_argument('--op', nargs='+',help="Add operations, delivery & notification clip|toar|composite|zip|zipall|compression|projection|kernel|aws|azure|gcs|email <Choose indices from>: ndvi|gndvi|bndvi|ndwi|tvi|osavi|evi2|msavi2|sr",default=None)
    parser_multiorder.set_defaults(func=multiorder_from_parser)

    parser_ordstatus = subparsers.add_parser('status',help='Check order status on submitted orders')
    parser_ordstatus.add_argument('--orderlist',help='Orderlist created earlier')
    parser_ordstatus.set_defaults(func=status_from_parser)

    parser_stats = subparsers.add_parser('stats', help='Prints number of orders queued and running for org & user')
    parser_stats.set_defaults(func=stats_from_parser)

    parser_ordsize = subparsers.add_parser('ordsize', help='Estimates total download size for each completed order(Takes times)')
    required_named = parser_ordsize.add_argument_group('Required named arguments.')
    required_named.add_argument('--infile', help='CSV file with order list', required=True)
    parser_ordsize.set_defaults(func=ordsize_from_parser)

    parser_downloader = subparsers.add_parser('downloader', help='Download using order url list')
    required_named = parser_downloader.add_argument_group('Required named arguments.')
    required_named.add_argument('--infile', help='CSV file with order list', required=True)
    required_named.add_argument('--folder', help='Local folder to save order files', required=True)
    required_named.add_argument('--method', help='Method to be utilized for downloading download|multipart|multiproc', required=True)
    parser_downloader.set_defaults(func=downloader_from_parser)
    args = parser.parse_args()

    args.func(args)

if __name__ == '__main__':
    main()
