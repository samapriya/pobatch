# pobatch: porder wrapper for Ordersv2 Batch Client

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3066368.svg)](https://doi.org/10.5281/zenodo.3066368)
[![PyPI version](https://badge.fury.io/py/pobatch.svg)](https://badge.fury.io/py/pobatch)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


**This tool is an addon to the porder tool, so [read about the project here](https://github.com/samapriya/porder) and make sure you take additional installation steps before starting with this**. This tool fits the need to order large orders in terms of spatial and temporal grids, splitting them into smaller manageable order and occur then while keeping in mind the concurrency limits. In this case the user sets a concurrency limit and the tool automatically checks and waits before placing next order. The tool can also estimate order size in terms of bytes per order download. The last step is to perform the same, download using porder's downloaders and an order list as created by multiorder tools. The design of the tool is kept simple, meaning you are relying on combined use or **porder** and **pobatch** to perform these operations. [Ordersv2 is the next iteration of Planet's API](https://developers.planet.com/docs/orders/) in getting Analysis Ready Data (ARD) delivered to you. Orders v2 allows you to improved functionality in this domain, including capability to submit an number of images in a batch order, and perform operations such as top of atmospheric reflectance, compression, coregistration and also enhanced notifications such as email and webhooks.

**Please note: This tool is in no way an official tool or Planet offering, but is a personal project created and maintained by Samapriya Roy**

If you find this tool useful, star and cite it as below

```
Samapriya Roy. (2019, May 20). samapriya/pobatch: pobatch: porder wrapper for Ordersv2 Batch Client (Version 0.0.1). Zenodo.
http://doi.org/10.5281/zenodo.3066368
```

## Table of contents
* [Installation](#installation)
* [Getting started](#getting-started)
* [porder wrapper for Ordersv2 Batch Client](#porder wrapper for Ordersv2 Batch Client)
    * [quota](#quota)
    * [idsplit](#idsplit)
    * [multiorder](#multiorder)
    * [ordsize](#ordsize)
    * [downloader](#downloader)
    * [Example Setup](#example-setup)

## Installation
This assumes that you have native python & pip installed in your system, you can test this by going to the terminal (or windows command prompt) and trying

```python``` and then ```pip list```

If you get no errors and you have python 2.7.14 or higher you should be good to go. Please note that I have tested this only on python 2.7.15 but it should run on python 3.

Shapely is notoriously difficult as a library to install on windows machines so follow the steps mentioned from [Shapely’s PyPI package page](https://pypi.org/project/Shapely/). You can download and install from the [Unofficial Wheel files from here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely) download depending on the python version you have. You will get a wheel file or a file ending with .whl. You can now simply browse to the folder or migrate to it in your command prompt , for example in my case I was running Python 2.7.15 and win32 version so the command was

```pip install Shapely-1.6.4.post1-cp27-cp27m-win32.whl```

Or you can use [anaconda to install](https://conda-forge.github.io/). Again, both of these options are mentioned on [Shapely’s Official PyPI page](https://pypi.org/project/Shapely/). **Fiona** is a recommended install used by the simplify tool, but it is not necessary. You can find installation instructions [here](https://pypi.org/project/Fiona/1.8.6/#description)

Once you have shapely configured. To install **porder: Simple CLI for Planet ordersv2 API** you can install using two methods

```pip install pobatch```

on Ubuntu I found it helps to specify the pip type and use sudo

```sudo pip2 install pobatch or sudo pip3 install pobatch```

or you can also try

```
git clone https://github.com/samapriya/pobatch.git
cd pobatch
python setup.py install
```
For linux use sudo or --user.

Installation is an optional step; the application can be also run directly by executing porder.py script. The advantage of having it installed is being able to execute porder as any command line tool. I recommend installation within virtual environment. If you don't want to install, browse into the porder folder and try ```python porder.py``` to get to the same result.


## Getting started

Make sure you initialized planet client by typing ```planet init``` or ```export``` or ```set PL_API_KEY=Your API Key``` As usual, to print help:

```
pobatch -h
usage: pobatch [-h] {idsplit,multiorder,ordsize,downloader} ...

porder wrapper for Ordersv2 Batch Client

positional arguments:
  {quota,idsplit,multiorder,ordsize,downloader}
    quota               Prints your Planet Quota Details
    idsplit             Splits ID list incase you want to run them in small
                        batches
    multiorder          Place multiple orders based on idlists in folder
    ordsize             Estimates total download size for each completed
                        order(Takes times)
    downloader          Download using order url list

optional arguments:
  -h, --help            show this help message and exit
```

To obtain help for a specific functionality, simply call it with _help_ switch, e.g.: `pobatch idsplit -h`. If you didn't install porder, then you can run it just by going to *pobatch* directory and running `python pobatch.py [arguments go here]`

## porder wrapper for Ordersv2 Batch Client
The tool is designed to simplify using the ordersv2 API and allows the user to chain together tools and operations for multiple item and asset types and perform these operations and download the assets locally.

### quota
Just a simple tool to print your planet subscription quota quickly.

```
porder quota
```

### idsplit
This allows you to split your idlist into small csv files incase you wanted to created batches of orders.

```
usage: porder idsplit [-h] [--idlist IDLIST] [--lines LINES] [--local LOCAL]

optional arguments:
  -h, --help       show this help message and exit
  --idlist IDLIST  Idlist txt file to split
  --lines LINES    Maximum number of lines in each split files
  --local LOCAL    Output folder where split files will be exported
```

A simple setup would be
```
porder idsplit --idlist "path to idlist.csv" --lines "number of lines in each idlist" --local "folder path to export split id lists"
```

### multiorder
It is possible for you to modify the idlist, add or remove ids. Once done, this tool allows you to estimate the total area of images and area that intersect with your geometry or area if clipped.

```
usage: pobatch multiorder [-h] --infolder INFOLDER --outfile OUTFILE --max MAX
                          --item ITEM --asset ASSET [--boundary BOUNDARY]
                          [--projection PROJECTION] [--kernel KERNEL]
                          [--compression COMPRESSION] [--aws AWS]
                          [--azure AZURE] [--gcs GCS] [--op OP [OP ...]]

optional arguments:
  -h, --help            show this help message and exit

Required named arguments.:
  --infolder INFOLDER   Folder with multiple order list
  --outfile OUTFILE     CSV file with list of order urls
  --max MAX             Maximum concurrent orders allowed on account
  --item ITEM           Item Type PSScene4Band|PSOrthoTile|REOrthoTile etc
  --asset ASSET         Asset Type analytic, analytic_sr,visual etc

Optional named arguments:
  --boundary BOUNDARY   Boundary/geometry for clip operation geojson|json|kml
  --projection PROJECTION
                        Projection for reproject operation of type "EPSG:4326"
  --kernel KERNEL       Resampling kernel used "near", "bilinear", "cubic",
                        "cubicspline", "lanczos", "average" and "mode"
  --compression COMPRESSION
                        Compression type used for tiff_optimize tool,
                        "lzw"|"deflate"
  --aws AWS             AWS cloud credentials config yml file
  --azure AZURE         Azure cloud credentials config yml file
  --gcs GCS             GCS cloud credentials config yml file
  --op OP [OP ...]      Add operations, delivery & notification clip|toar|comp
                        osite|zip|zipall|compression|projection|kernel|aws|azu
                        re|gcs|email <Choose indices from>:
                        ndvi|gndvi|bndvi|ndwi|tvi|osavi|evi2|msavi2|sr
```

### ordsize
This tool allows you to actually place the order using the idlist that you created earlier. the ```--op``` argument allows you to take operations, delivery and notifications in a sequence for example ```--op toar clip email``` performs Top of Atmospheric reflectance, followed by clipping to your geometry and send you an email notification once the order has completed, failed or had any any change of status. The list of operations are below and **order is important**

```
usage: pobatch ordsize [-h] --infile INFILE

optional arguments:
  -h, --help       show this help message and exit

Required named arguments.:
  --infile INFILE  CSV file with order list
```

### downloader
The tool now allows you to estimate the total download size for a specific order.

```
usage: pobatch downloader [-h] --infile INFILE --folder FOLDER --method METHOD

optional arguments:
  -h, --help       show this help message and exit

Required named arguments.:
  --infile INFILE  CSV file with order list
  --folder FOLDER  Local folder to save order files
  --method METHOD  Method to be utilized for downloading
                   download|multipart|multiproc
```


### Example Setup

* Get idlist for geometry using porder (porder is installed as a dependency for this tool)

```
porder idlist --input "geometry file.geojson" --start "2018-01-01" --end "2019-02-01" --item "PSScene4Band" --asset "analytic" --outfile "path to idlist.csv"
```

* Split idlist into smaller subparts

```
pobatch idsplit --idlist "idlist file created earlier" --lines "number of lines in split files" --local "folder where we save the split id files"
```

* Now place order using idlists that you created. This requires you to set up a limit on the maximum number of concurrent orders you can place. This setups clips the image to a geometry, zips them and send you an email notification on completion.

```
pobatch multiorder --infolder "folder where we save the split id files" --max "Maximum concurrent orders you can placed and allowed on your account" --outfile "path to an orderlist with order url" --item "PSScene4Band" --asset "analytic" --boundary "path to geometry.geojson" --op clip zip email
```

* Estimate order download size for each order (This is optional)

```
pobatch ordsize --infile "Path to order url list"
```

* Finally download the order, and choose the download method (choose from sequential download or download| multipart download or multiproc or multiprocessing download)

```
pobatch downloader --infile "Path to order url list" --folder "download folder" --method "multipart"
```
