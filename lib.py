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


def get_exif_data(fobj):
    # Get exif tags
    return exifread.process_file(fobj, details=False)


# Get date data
def get_date_data(fpath, exif):

    tags = {}
    
    # Check filename for a date
    m = re.search(re.compile('(?<![0-9])(20[0-9]{2})-?([0-9]{2})-?([0-9]{2})(?![0-9])'), pathlib.Path(fpath).name)
    if m:
        tags['pathtime'] = '%s-%s-%s' % (m.group(0), m.group(1), m.group(2))

    # Add exif dates
    for ex in exif.keys():
        if re.search('gps', ex.lower()):
            continue

        if not re.search('date', ex.lower()):
            continue

        tags[ex] = exif[ex]

    # Get file creation time
    tags['ctime'] = os.path.getctime(fpath)

    # Normalize all the dates
    for t in tags.keys():
        try:
            tags[t] = arrow.get(str(tags[t]))
        except arrow.parser.ParserError:
            debug('Skipping %s for %s' % (t, fpath))
            debug(repr(tags[t]))
            del tags[t]

    return tags


# Get real date
def get_real_date(dates):

    # If we have a reliable source, then ditch the dodgy ones
    if 'EXIF DateTimeOriginal' in dates:
        # Ignore 'Image DateTime' as it's wrong
        if 'Image DateTime' in dates:
            del dates['Image DateTime']
        # Ignore 'Thumbnail DateTime' as it's wrong
        if 'Thumbnail DateTime' in dates:
            del dates['Thumbnail DateTime']

    res = {
        'source': None,
        'date': None,
        'allmatch': None
    }

    # If all we have is ctime, then go with that
    if 'ctime' in dates and len(dates) == 1:
        res['source'] = 'ctime'
        res['date'] = dates['ctime'].format('YYYY-MM')
        res['allmatch'] = True
        return res

    allmatch = True
    earliest = None
    for date in dates:
        if date == 'ctime':
            continue

        # We only care about dates at month-level detail
        d = dates[date].format('YYYY-MM')
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
    return hashlib.md5(fobj.read()).hexdigest()


# Show debug messages
def debug(message):
    print(message)
