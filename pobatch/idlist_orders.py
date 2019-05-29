import os
import time
import pendulum
import requests
import logging
import subprocess
import progressbar
import sys
import csv
try:
    import Queue
    q = Queue.Queue()
except ImportError:
    import queue
    q = queue.Queue()

from planet.api.auth import find_api_key

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
try:
    PL_API_KEY = find_api_key()
except Exception as e:
    print('Failed to get Planet Key')
    sys.exit()
SESSION = requests.Session()
SESSION.auth = (PL_API_KEY, '')

# Create an empty queue



# Check running orders
def handle_page(page):
    i = 0
    try:
        for items in page['orders']:
            if items['state'] == 'running':
                i = i + 1
        return i
    except Exception as e:
        print(e)


# Check for concurrenct orders that are running
runlist = []


def conc():
    runlist=[]
    result = SESSION.get('https://api.planet.com/compute/ops/orders/v2')
    page = result.json()
    final_list = handle_page(page)
    runlist.append(final_list)
    while page['_links'].get('next') is not None:
        time.sleep(0.5) #Create a 500ms break time just in case
        try:
            page_url = page['_links'].get('next')
            result = SESSION.get(page_url)
            page = result.json()
            ids = handle_page(page)
            runlist.append(ids)
        except Exception as e:
            print(e)
            pass
    return sum(runlist)


def batch_order(infolder, outfile, max_conc, item, asset,boundary,projection,kernel,compression,aws,azure,gcs,op):
    n = 1
    open(outfile, 'w')
    for files in os.listdir(infolder):
        if files.endswith('.csv'):
            filebase = os.path.basename(files).split('.')[0]
            name = filebase + '-' + str(pendulum.now()).split('T')[0]
            idlist = os.path.join(infolder, files)
            q.put([name, idlist, item, asset, boundary, projection,kernel,compression,aws,azure,gcs,op])
    total=q.qsize()
    while not q.empty():
        try:
            logging.info('Processing: '+str(n)+' of '+str(total))
            text = q.get()
            name = text[0]
            idlist = text[1]
            item = text[2]
            asset = text[3]
            boundary = text[4]
            projection=text[5]
            kernel=text[6]
            compression=text[7]
            aws=text[8]
            azure=text[9]
            gcs=text[10]
            op = text[11]
            jtext='porder order --name '+str(name)+' --idlist '+'"'+str(idlist)+'"'+' --item '+str(item)+' --asset '+str(asset)+' --boundary '+'"'+str(boundary)+'"'+' --projection '+'"'+str(projection)+'"'+' --kernel '+'"'+str(kernel)+'"'+' --compression '+'"'+str(compression)+'"'+' --aws '+'"'+str(aws)+'"'+' --azure '+'"'+str(azure)+'"'+' --gcs '+'"'+str(gcs)+'"'+' --op '+str(' '.join(op))
            if compression is None:
                jtext=jtext.replace('--compression "None" ',"")
            if kernel is None:
                jtext=jtext.replace('--kernel "None" ',"")
            if projection is None:
                jtext=jtext.replace('--projection "None" ',"")
            if boundary is None:
                jtext=jtext.replace('--boundary "None" ',"")
            if aws is None:
                jtext=jtext.replace('--aws "None" ',"")
            if gcs is None:
                jtext=jtext.replace('--gcs "None" ',"")
            if azure is None:
                jtext=jtext.replace('--azure "None" ',"")
            conc_count=conc()
            logging.info('Checking currently running orders: Total of '+str(conc_count)+' orders')
            while int(conc_count)>=int(max_conc):
                print('Reached max concurrency: Waiting 5 minutes')
                bar = progressbar.ProgressBar()
                for z in bar(range(300)):
                    time.sleep(1)
                conc_count=conc()
            orderurl=subprocess.check_output(jtext,shell=False)
            urltext=orderurl.split('at ')[1].split(' and')[0]
            logging.info('Order created at: '+str(urltext))
            with open(outfile,'a') as csvfile:
                writer=csv.writer(csvfile,delimiter=',',lineterminator='\n')
                writer.writerow([str(urltext)])
            time.sleep(1)
            q.task_done()
            n = n + 1
        except Exception as e:
            print(e)
# batch_order(infolder=r'C:\planet_demo\nmsplit',max_conc=40,item='PSScene4Band',asset='analytic',
#     boundary=r'C:\Users\samapriya\Downloads\Geometries\nimbios.geojson',op=['clip','zip','email'])

