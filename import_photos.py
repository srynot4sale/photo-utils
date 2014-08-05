import subprocess

import pathlib

import lib
from lib import debug

DEBUG = True

DEST_DIR = '/media/sdb1/photos/'
#DEST_DIR = '/home/aaronb/Downloads/test/'

if not DEBUG:
    debug = list


importroot = pathlib.Path.cwd()
print('Importing photos')
print('From: %s' % str(importroot))
print('To: %s' % DEST_DIR)

print('')
print('Fetching photo list...')

toimport = lib.get_all_files(importroot)
print('%s files found...' % len(toimport))

print('')
print('Items found:')
import_sorted = lib.sort_files(toimport)
for key in import_sorted.keys():
    print '%s: %d' % (key, len(import_sorted[key]))

print('')
print('Scanning images for dates and hashes...')

sources = {}
dates = {}
duplicates = []
not_allsame = []
hashes = {}

import_metadata = {}
if 'image' in import_sorted:
    for f in import_sorted['image']:
        # Load file and grab details
        with open(f) as fobj:
            metadata = {}

            exif_tags = lib.get_exif_data(fobj)
            metadata = {}
            metadata['datedata'] = lib.get_date_data(f, exif_tags)
            metadata['dateextra'] = lib.get_real_date(metadata['datedata'])
            metadata['date'] = metadata['dateextra']['date']
            
            # Check for duplicates
            metadata['hash'] = lib.get_file_hash(fobj)
            
            # Check in hashstore
            hashstore = DEST_DIR + 'hash.store'
            cmd = ["""grep %s %s | grep -oP '(?<=\t)(.+)'""" % (metadata['hash'], hashstore)]
            try:
                match_search = subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError:
                match_search = False

            if metadata['hash'] in hashes:
                duplicates.append((hashes[metadata['hash']], f))
            elif match_search:
                duplicates.append((match_search.strip(), f))
            else:
                hashes[metadata['hash']] = f

            # Check if date data is inconsistent
            if not metadata['dateextra']['allmatch']:
                not_allsame.append(f)
                print(f)
                pprint.pprint(exif_tags)
        
            # Sort for reporting
            if metadata['dateextra']['source'] not in sources:
                sources[metadata['dateextra']['source']] = 0
            sources[metadata['dateextra']['source']] += 1

            if metadata['date'][0:7] not in dates:
                dates[metadata['date'][0:7]] = 0
            dates[metadata['date'][0:7]] += 1

        import_metadata[str(f)] = metadata


print('')
print('Sources:')
for s in sources:
    print('%s: %d' % (s, sources[s]))

print('')
print('%d do not have matching dates' % (len(not_allsame)))

print('')
print('Dates:')
dk = dates.keys()
dk.sort()
for s in dk:
    print('%s: %d' % (s, dates[s]))

print('')
print('%d images are duplicates' % (len(duplicates)))
for f1,f2 in duplicates:
    print('%s == %s' % (f1, f2))
