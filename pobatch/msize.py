import csv
import subprocess
import requests
import time
import sys
from planet.api.auth import find_api_key


try:
    PL_API_KEY = find_api_key()
except Exception as e:
    print('Failed to get Planet Key')
    sys.exit()
SESSION = requests.Session()
SESSION.auth = (PL_API_KEY, '')


def ordsize(infile):
    with open(infile) as f:
        try:
            reader = csv.reader(f)
            for row in reader:
                order_url = row[0]
                response = SESSION.get(order_url)
                resp = response.json()
                print('')
                print('Processing order: ' + str(resp['name']))
                time.sleep(1)
                subprocess.call('porder ordersize --url ' + str(order_url), shell=True)
        except Exception as e:
            print(e)
            print('Issue with reading: ' + str(infile))
#ordsize(infile=r'C:\planet_demo\nimbios_olist.csv')
