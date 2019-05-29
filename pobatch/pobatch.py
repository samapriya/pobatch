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
import sys
from geojson2id import idl
from text_split import idsplit
from idlist_orders import batch_order
from msize import ordsize
from mdown import downloader
os.chdir(os.path.dirname(os.path.realpath(__file__)))
lpath=os.path.dirname(os.path.realpath(__file__))
sys.path.append(lpath)


#Get quota for your account
def planet_quota():
    try:
        subprocess.call('python planet_quota.py',shell=True)
    except Exception as e:
        print(e)
def planet_quota_from_parser(args):
    planet_quota()

#Create ID List with structured JSON
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

#Place orders in folders
def multiorder_from_parser(args):
    batch_order(infolder=args.infolder,
        outfile=args.outfile,
        max_conc=args.max,
        item=args.item,
        asset=args.asset,
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

    parser_multiorder = subparsers.add_parser('multiorder', help='Place multiple orders based on idlists in folder')
    required_named = parser_multiorder.add_argument_group('Required named arguments.')
    required_named.add_argument('--infolder', help='Folder with multiple order list', required=True)
    required_named.add_argument('--outfile', help='CSV file with list of order urls', required=True)
    required_named.add_argument('--max', help='Maximum concurrent orders allowed on account', required=True)
    required_named.add_argument('--item', help='Item Type PSScene4Band|PSOrthoTile|REOrthoTile etc', required=True)
    required_named.add_argument('--asset', help='Asset Type analytic, analytic_sr,visual etc', required=True)
    optional_named = parser_multiorder.add_argument_group('Optional named arguments')
    optional_named.add_argument('--boundary', help='Boundary/geometry for clip operation geojson|json|kml',default=None)
    optional_named.add_argument('--projection', help='Projection for reproject operation of type "EPSG:4326"',default=None)
    optional_named.add_argument('--kernel', help='Resampling kernel used "near", "bilinear", "cubic", "cubicspline", "lanczos", "average" and "mode"',default=None)
    optional_named.add_argument('--compression', help='Compression type used for tiff_optimize tool, "lzw"|"deflate"',default=None)
    optional_named.add_argument('--aws', help='AWS cloud credentials config yml file',default=None)
    optional_named.add_argument('--azure', help='Azure cloud credentials config yml file',default=None)
    optional_named.add_argument('--gcs', help='GCS cloud credentials config yml file',default=None)
    optional_named.add_argument('--op', nargs='+',help="Add operations, delivery & notification clip|toar|composite|zip|zipall|compression|projection|kernel|aws|azure|gcs|email <Choose indices from>: ndvi|gndvi|bndvi|ndwi|tvi|osavi|evi2|msavi2|sr",default=None)
    parser_multiorder.set_defaults(func=multiorder_from_parser)

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
