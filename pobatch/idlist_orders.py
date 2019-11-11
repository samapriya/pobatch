import os
import time
import pendulum
import requests
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


# Get overall stats
def stats():
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
            oqueue=int(page['organization']['queued_orders'])
            uqueue=int(page['user']['queued_orders'])
            urunning=int(page['user']['running_orders'])
            return (oqueue,uqueue,urunning)
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


def batch_order(infolder, outfile, errorlog,item, bundle, sid, boundary,projection,kernel,compression,aws,azure,gcs,op):
    try:
        PL_API_KEY = find_api_key()
    except Exception as e:
        print('Failed to get Planet Key: Try planet init to initialize')
        sys.exit()
    SESSION = requests.Session()
    SESSION.auth = (PL_API_KEY, '')
    n = 1
    open(outfile, 'w')
    open(errorlog, 'w')
    for files in os.listdir(infolder):
        if files.endswith('.csv'):
            filebase = os.path.basename(files).split('.')[0]
            name = filebase + '-' + str(pendulum.now()).split('T')[0]
            idlist = os.path.join(infolder, files)
            q.put([name, idlist, item, bundle, sid, boundary, projection,kernel,compression,aws,azure,gcs,op])
    total=q.qsize()
    while not q.empty():
        try:
            print('\n'+'Processing: '+str(n)+' of '+str(total))
            text = q.get()
            name = text[0]
            idlist = text[1]
            item = text[2]
            bundle = text[3]
            sid=text[4]
            boundary = text[5]
            projection=text[6]
            kernel=text[7]
            compression=text[8]
            aws=text[9]
            azure=text[10]
            gcs=text[11]
            op = text[12]
            if op is not None:
                jtext='porder order --name '+str(name)+' --idlist '+'"'+str(idlist)+'"'+' --item '+str(item)+' --bundle '+str(bundle)+' --sid '+'"'+str(sid)+'"'+' --boundary '+'"'+str(boundary)+'"'+' --projection '+'"'+str(projection)+'"'+' --kernel '+'"'+str(kernel)+'"'+' --compression '+'"'+str(compression)+'"'+' --aws '+'"'+str(aws)+'"'+' --azure '+'"'+str(azure)+'"'+' --gcs '+'"'+str(gcs)+'"'+' --op '+str(' '.join(op))
                if sid is None:
                    jtext=jtext.replace('--sid "None" ',"")
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
            elif op is None and sid is not None:
                 jtext='porder order --name '+str(name)+' --idlist '+'"'+str(idlist)+'"'+' --item '+str(item)+' --bundle '+str(bundle)+' --sid '+str(sid)
            elif op is None and sid is None:
                 jtext='porder order --name '+str(name)+' --idlist '+'"'+str(idlist)+'"'+' --item '+str(item)+' --bundle '+str(bundle)
            ogq,uq,ur=stats()
            print('Currently queued orders for organization: Total of '+str(ogq)+' orders')
            print('Currently queued orders for user: Total of '+str(uq)+' orders')
            print('Currently running orders for user: Total of '+str(ur)+' orders')
            while int(ogq)>=10000:
                print('Reached max queue length: Waiting 5 minutes')
                bar = progressbar.ProgressBar()
                for z in bar(range(300)):
                    time.sleep(1)
                ogq,uq,ur=conc()
            orderurl=subprocess.check_output(jtext,shell=True)
            try:
                urltext=orderurl.decode('utf-8').split('at ')[1].split(' and')[0]
                print('Order created at: '+str(urltext))
                with open(outfile,'a') as csvfile:
                    writer=csv.writer(csvfile,delimiter=',',lineterminator='\n')
                    writer.writerow([str(idlist),str(urltext)])
            except Exception as e:
                print('Idlist '+str(idlist)+' failed to place order')
                with open(errorlog,'a') as csvfile:
                    writer=csv.writer(csvfile,delimiter=',',lineterminator='\n')
                    writer.writerow([str(idlist),orderurl.decode('utf-8')])
            time.sleep(1)
            q.task_done()
            n = n + 1
        except Exception as e:
            print(e)
# batch_order(infolder=r'C:\planet_demo\nmsplit',max_conc=40,item='PSScene4Band',asset='analytic',
#     boundary=r'C:\Users\samapriya\Downloads\Geometries\nimbios.geojson',op=['clip','zip','email'])

