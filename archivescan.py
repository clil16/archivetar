#!/usr/bin/python


# Brock Palen
# brockp@umich.edu
#
# The intent of this is to generate a report for data to be uploaded to Data Den
# https://arc-ts.umich.edu/data-den/
# Data Den only accepts files > 100MB, it enforces this by providing only 10,000 files/TB of prvisoned capacity
#
# Often data in a single folder looks like:
# Files >100MB   100 Files  100GB
# Files <100MB 10000 Files  2GB
#
# You could combine Locker
# https://arc-ts.umich.edu/locker/
# Which frontends Data Den as a cache to hold smaller files

## TODO
#
# * Generate optional list of files
# * Make seetings setable from envrionment

import os
import time
import math

# This is to get the directory that the program  
# is currently running in. 
dir_path = os.getcwd()

# cost of data den/TB/yr
datadenrate = os.getenv('DATADENRATE', 40)

# data den Migrate size MB
migratesize = os.getenv('MIGRATESIZE', 100)

# cost of Locker/TB/yr
lockerrate = os.getenv('LOCKERRATE', 80)

# Locker file quota/MB
lockerinode = os.getenv('LOCKERINODE', 1.0e6)

byteintbyte = 1024.0*1024*1024*1024


# get size of all files in a directory path
# filter_size : files greater than this are counted
def get_size(start_path = '.', filter_size = 104857600):
    total_size = 0  # total size to archive
    total_cnt = 0   # counts for archive
    ctotal_size = 0 # size for cache (to small for archive)
    ctotal_cnt = 0  # counts for cache (to small for archive)
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                size = os.path.getsize(fp)
                if size > filter_size:
                    total_size += size
                    total_cnt += 1
                if size <= filter_size:
                    ctotal_size += size
                    ctotal_cnt += 1

    return total_size, total_cnt, ctotal_size, ctotal_cnt

# borrowed from
# https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
# Thank You!
# Converts to human friendly units
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


# cache size for transent data to and from tape
# In TB max(1.0, min( 10% tape, 10))
def calc_cache(tapesize):
    return max(1.0, min( 0.1*tapesize, 10))

####  Main Program

# This is to get the directory that the program  
# is currently running in. 
dir_path = os.getcwd()

start_time = time.time()


print "----- Results ------"
print("Data Den Candidates:")

size, count, csize, ccnt = get_size()
tbyte = math.ceil(size/byteintbyte)
extra_cache = calc_cache(tbyte)  # calculate extra cache for tape data in flight
print("Files: %s" % (count))
print("Size: %s" % (sizeof_fmt(size)))
print("Terabyte %s Cost: $%d" % (tbyte, tbyte*datadenrate))

# get locker sizes
tbyte = math.ceil(csize/byteintbyte) 
filestb = math.ceil((count+ccnt)/lockerinode)
tbyte = max(tbyte, filestb)
print""
print("Cache (Locker) Candidates:")
print("Files: %s" % (ccnt))
print("Size: %s" % (sizeof_fmt(csize)))
print("Terabyte %s (Storage: %s, Tape Cache: %s) Cost: $%d" % (tbyte+extra_cache, tbyte, extra_cache, tbyte*lockerrate))
print""
print("Scan Time %s Seconds" % (time.time() - start_time))
