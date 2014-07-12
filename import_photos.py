import pathlib

import lib
from lib import debug

DEBUG = True

#DEST_DIR = '/media/sdb1/photos/'
DEST_DIR = '/home/aaronb/Downloads/test'

if not DEBUG:
    debug = list


print('Importing photos')

print('')
print('Fetching photo list...')
importroot = pathlib.Path('.')

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
not_allsame = []
hashes = {}


import_metadata = {}
if 'image' in import_sorted:
    for f in import_sorted['image']:
        # Load file and grab details
        with open(f) as fobj:
            metadata = {}
            datedata = lib.get_date_data(f, fobj)
            metadata['datedata'] = lib.get_real_date(datedata)
            metadata['date'] = metadata['datedata']['date']
            metadata['hash'] = lib.get_file_hash(fobj)

            # Sort for reporting
            if metadata['datedata']['source'] not in sources:
                sources[metadata['datedata']['source']] = 0
            sources[metadata['datedata']['source']] += 1

            if metadata['date'][0:7] not in dates:
                dates[metadata['date'][0:7]] = 0
            dates[metadata['date'][0:7]] += 1

            if not metadata['datedata']['allmatch']:
                not_allsame.append(f)

            # Check for duplicates
            if metadata['hash'] in hashes:
                print('ERROR: found duplicates! (%s, %s)' % (hashes[metadata['hash']], f))
            else:
                hashes[metadata['hash']] = f


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
