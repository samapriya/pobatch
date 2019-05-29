import csv
import subprocess
import requests
import time
import sys
import logging
from planet.api.auth import find_api_key

# Setup logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

try:
    PL_API_KEY = find_api_key()
except Exception as e:
    print('Failed to get Planet Key')
    sys.exit()
SESSION = requests.Session()
SESSION.auth = (PL_API_KEY, '')


def downloader(infile, folderpath, method):
    with open(infile) as f:
        try:
            reader = csv.reader(f)
            for row in reader:
                order_url = row[0]
                response = SESSION.get(order_url)
                resp = response.json()
                print('')
                logging.info('Attemting to download ' + str(resp['name']) + ' with ' + str(len(resp['products'][0]['item_ids'])) + ' assets')
                time.sleep(1)
                if method == 'download':
                    subprocess.call('porder download --url ' + str(order_url) + ' --local ' + str(folderpath), shell=False)
                elif method == 'multipart':
                    subprocess.call('porder multipart --url ' + str(order_url) + ' --local ' + str(folderpath), shell=False)
                elif method == 'multiproc':
                    subprocess.call('porder multiproc --url ' + str(order_url) + ' --local ' + str(folderpath), shell=False)
        except Exception as e:
            print(e)
            print('Issue with reading: ' + str(infile))
#downloader(infile=r'C:\planet_demo\nimbios_olist2.csv',folderpath=r'C:\planet_demo',method='multipart')
