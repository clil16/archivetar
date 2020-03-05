#!/usr/bin/python3


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

# TODO
#
# * Generate optional list of files
# * Make seetings setable from envrionment

import os
import time
import math
from multiprocessing import Pool
import argparse


def get_options():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', help='Target directory to scan for archiving')
    parser.add_argument('-l', '--list', action='store_true', help='List the files')
    parser.add_argument('-f', '--file', type=str, help='File to output the list of files to.')
    arguments = parser.parse_args()
    return arguments


# This is to get the directory that the program  
# is currently running in. 
# dir_path = os.getcwd()
# dir_path = options.target

# cost of data den/TB/yr
# datadenrate = os.getenv('DATADENRATE', 40)

# data den Migrate size MB
# migratesize = os.getenv('MIGRATESIZE', 100)

# cost of Locker/TB/yr
# lockerrate = os.getenv('LOCKERRATE', 80)

# Locker file quota/MB
# lockerinode = os.getenv('LOCKERINODE', 1.0e6)

# byteintbyte = 1024.0 * 1024 * 1024 * 1024


# get size of all files in a directory path
# filter_size : files greater than this are counted
def get_size(start_path, filter_size=104857600):
    total_size = 0  # total size to archive
    total_cnt = 0  # counts for archive
    ctotal_size = 0  # size for cache (to small for archive)
    ctotal_cnt = 0  # counts for cache (to small for archive)
    file_list = []  # Files to archive
    cfile_list = []  # Files for cache (to small for archive)
    p = Pool(processes=8)
    # for dirpath, dirnames, filenames in os.walk(start_path):
    output = p.map(get_size_local,
                   [(dirpath, filenames, filter_size) for dirpath, dirnames, filenames in os.walk(start_path)])
    for (a, b, c, d, e, f) in output:
        total_size += a
        total_cnt += b
        ctotal_size += c
        ctotal_cnt += d
        file_list.extend(e)
        cfile_list.extend(f)

    return total_size, total_cnt, ctotal_size, ctotal_cnt, file_list, cfile_list


def get_size_local(fargs):
    dirpath, filenames, filter_size = fargs
    total_size = 0  # total size to archive
    total_cnt = 0  # counts for archive
    ctotal_size = 0  # size for cache (to small for archive)
    ctotal_cnt = 0  # counts for cache (to small for archive)
    file_list = []  # Files to archive
    cfile_list = []  # Files for cache (to small for archive)
    for f in filenames:
        fp = os.path.join(dirpath, f)
        # skip if it is symbolic link
        if not os.path.islink(fp):
            size = os.path.getsize(fp)
            if size > filter_size:
                total_size += size
                total_cnt += 1
                file_list.append(fp)
            if size <= filter_size:
                ctotal_size += size
                ctotal_cnt += 1
                cfile_list.append(fp)

    return total_size, total_cnt, ctotal_size, ctotal_cnt, file_list, cfile_list


# borrowed from
# https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
# Thank You!
# Converts to human friendly units
def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


# cache size for transent data to and from tape
# In TB max(1.0, min( 10% tape, 10))
def calc_cache(tapesize):
    return max(1.0, min(0.1 * tapesize, 10))


#  Main Program
def main():
    if options.list and options.file is None:
        argparse.ArgumentParser().error("-l|--list requires -f|--file.")
    # This is to get the directory that the program
    # is currently running in.
    # dir_path = os.getcwd()
    # dir_path = options.target

    # cost of data den/TB/yr
    datadenrate = os.getenv('DATADENRATE', 40)

    # data den Migrate size MB
    migratesize = os.getenv('MIGRATESIZE', 100)

    # cost of Locker/TB/yr
    lockerrate = os.getenv('LOCKERRATE', 80)

    # Locker file quota/MB
    lockerinode = os.getenv('LOCKERINODE', 1.0e6)

    byteintbyte = 1024.0 * 1024 * 1024 * 1024
    # This is to get the directory that the program
    # is currently running in.
    # dir_path = os.getcwd()
    # dir_path = options.target

    start_time = time.time()

    print("----- Results ------")
    print("Analyzed the directory {}".format(options.target))
    print("Data Den Candidates:")

    size, count, csize, ccnt, flist, cflist = get_size(options.target)
    tbyte = math.ceil(size / byteintbyte)
    extra_cache = calc_cache(tbyte)  # calculate extra cache for tape data in flight
    print("Files: {}".format(count))
    print("Size: {}".format(sizeof_fmt(size)))
    print("Terabyte {} Cost: ${:d}".format(tbyte, tbyte * datadenrate))

    # get locker sizes
    tbyte = math.ceil(csize / byteintbyte)
    filestb = math.ceil((count + ccnt) / lockerinode)
    tbyte = max(tbyte, filestb)
    print("")
    print("Cache (Locker) Candidates:")
    print("Files: {}".format(ccnt))
    print("Size: {}".format(sizeof_fmt(csize)))
    print("Terabyte {} (Storage: {}, Tape Cache: {:f}) Cost: ${:d}".format(tbyte + extra_cache, tbyte, extra_cache,
                                                                           tbyte * lockerrate))
    print("")
    print("Scan Time {:f} Seconds".format(time.time() - start_time))
    if options.list:
        with open(options.file, 'w') as fh:
            fh.write("Data Den Candidate Files:\n")
            for f in sorted(flist):
                fh.write("{}\n".format(f))
            fh.write("\nCache (Locker) Candidate Files:\n")
            for f in sorted(cflist):
                fh.write("{}\n".format(f))
            print("\nFile list was written to {}".format(options.file))


if __name__ == "__main__":
    options = get_options()
    main()
