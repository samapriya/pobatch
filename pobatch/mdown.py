from __future__ import print_function
import csv
import subprocess
import requests
import time
import sys
import logging
from planet.api.auth import find_api_key


try:
    import Queue
    q = Queue.Queue()
except ImportError:
    import queue
    q = queue.Queue()

# Setup logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Get API Key
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
            your_list = list(reader)
            for row in your_list:
                order_url = row[0]
                q.put(order_url)
            i=0.5
            while not q.empty():
                t = time.localtime()
                print(str(time.asctime(t))+': Number of orders remaining in order list '+str(q.qsize()), end='\r')
                try:
                    order_url=q.get()
                    response = SESSION.get(order_url)
                    if response.status_code==200:
                        resp = response.json()
                        if resp['state']=='success':
                            logging.info('Attemting to download ' + str(resp['name']) + ' with ' + str(len(resp['products'][0]['item_ids'])) + ' assets')
                            time.sleep(1)
                            if method == 'download':
                                subprocess.call('porder download --url ' + str(order_url) + ' --local ' + str(folderpath), shell=False)
                            elif method == 'multipart':
                                subprocess.call('porder multipart --url ' + str(order_url) + ' --local ' + str(folderpath), shell=False)
                            elif method == 'multiproc':
                                subprocess.call('porder multiproc --url ' + str(order_url) + ' --local ' + str(folderpath), shell=False)
                            #print('Number of orders remaining in url'+str(q.qsize()))
                        else:
                            if i==60: # Reset delay after reaching 60 seconds or 120 tries
                                i=1
                            time.sleep(i)
                            q.put(order_url)
                    else:
                        print(response.status_code)
                    i=i+0.5
                except Exception as e:
                    print(e)
                    print('Issue with reading: ' + str(infile))
        except Exception as e:
            print(e)
            print('Issue with reading: ' + str(infile))
        except (KeyboardInterrupt, SystemExit) as e:
            print('\n')
            print('Program escaped by User')
            sys.exit()
#downloader(infile=r'C:\planet_demo\nimbios_olist2.csv',folderpath=r'C:\planet_demo',method='multipart')
