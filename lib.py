import hashlib
import os
import re

import arrow
import exifread
import imghdr
import pathlib
#import Pillow

# Get all files recursively
def get_all_files(root):
    return list(root.glob('**/*'))


# Sort files
def sort_files(filelist):
    types = {}
    for f in filelist:
        if f.is_dir():
            t = 'directory'
        else:
            f = str(f)

            # Test if image
            img = imghdr.what(f)
            if not img:
                t = 'other'
            else:
                t = 'image'

        if t not in types:
            types[t] = []

        types[t].append(f)

    return types


# Get date data
def get_date_data(fpath, fobj):

    # Get exif tags
    tags = exifread.process_file(fobj, details=False)
    for t in tags.keys():
        if re.search('gps', t.lower()):
            del tags[t]
            continue

        if not re.search('date', t.lower()):
            del tags[t]

    # Get file creation time
    tags['ctime'] = os.path.getctime(fpath)

    # Check filename for a date
    m = re.search(re.compile('(20[0-9]{2}-?[0-9]{2}-?[0-9]{2})'), pathlib.Path(fpath).name)
    if m:
        match = m.group(0)
        tags['pathtime'] = '%s-%s-%s' % (match[0:4], match[4:6], match[6:8])

    # Normalize all the dates
    for t in tags:
        tags[t] = arrow.get(str(tags[t]))
#        debug('%s: %s' % (t, tags[t]))

    return tags


# Get real date
def get_real_date(dates):

    res = {
        'source': None,
        'date': None,
        'allmatch': None
    }

    if len(dates) == 1:
        res['source'] = 'ctime'
        res['date'] = dates['ctime'].format('YYYY-MM-DD')
        res['allmatch'] = True
        return res

    allmatch = True
    earliest = None
    for date in dates:
        if date == 'ctime':
            continue

        d = dates[date].format('YYYY-MM-DD')
        if earliest == None:
            earliest = d
            res['source'] = date

        if d != earliest:
            allmatch = False
            if d < earliest:
                earliest = d
                res['source'] = date

    res['date'] = earliest
    res['allmatch'] = allmatch
    return res


def get_file_hash(fobj):
    return hashlib.md5(fobj.read())


# Show debug messages
def debug(message):
    print(message)
