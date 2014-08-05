import pprint
import sys

import pathlib

import lib
from lib import debug

DEBUG = True
SKIP_HASHES = False

DEST_DIR = '/media/sdb1/photos/'

if not DEBUG:
    debug = list

importroot = pathlib.Path(DEST_DIR)

print('Checking for duplicate photos, mis-categorised photos, generating a hash store')
print('Photo store: %s' % DEST_DIR)

print('')
print('Fetching photo list...')
toimport = lib.get_all_files(importroot)
print('%s files found...' % len(toimport))

print('')
print('Types of items found:')
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
if 'image' not in import_sorted:
    print('No images found!')
    sys.exit()

counter = 0
for f in import_sorted['image']:
    # Load file and grab details
    with open(f) as fobj:
        counter += 1

        if counter % int(len(import_sorted['image']) / 10) == 0:
            print('.')

        exif_tags = lib.get_exif_data(fobj)
        metadata = {}
        metadata['datedata'] = lib.get_date_data(f, exif_tags)
        metadata['dateextra'] = lib.get_real_date(metadata['datedata'])
        metadata['date'] = metadata['dateextra']['date']
        
        # Check for duplicates
        if not SKIP_HASHES:
            metadata['hash'] = lib.get_file_hash(fobj)

            if metadata['hash'] in hashes:
                duplicates.append((hashes[metadata['hash']], f))
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
print('Dates:')
dk = dates.keys()
dk.sort()
for s in dk:
    print('%s: %d' % (s, dates[s]))

print('')
print('%d images do not have matching dates' % (len(not_allsame)))
for f in not_allsame:
    print(f)
    pprint.pprint(import_metadata[f])
                
if not SKIP_HASHES:
    print('')
    print('Writing hash store...')

    hashstore = open(DEST_DIR + 'hash.store', 'w')
    for hash in hashes:
        hashstore.write('%s\t%s\n' % (hash, hashes[hash]))
    hashstore.close()

    print('Done')

    print('')
    print('%d images are duplicates' % (len(duplicates)))
    for f1,f2 in duplicates:
        print('%s == %s' % (f1, f2))
