import sys
import datetime


def die_with_errormsg(msg='', errnum=1):
    if isinstance(msg, str):
        print(str(msg) + "\n")
    else:
        try:
            for msg_item in msg:
                print(str(msg_item))
        except:
            try:
                print(str(msg) + "\n")
            except:
                pass
            pass
    sys.exit(errnum)


def get_ISOTimestamp_ForLogFilename():
    timestamp = datetime.datetime.now().isoformat()  # '2016-03-20T21:30:44.560397'
    timestamp = ''.join(timestamp.split(':')[0:2])  # Remove the seconds & milliseconds => '2016-03-20T2130'
    timestamp = timestamp.replace('T', '')  # Remove the 'T' => '2016-03-202130'
    timestamp = timestamp.replace('-', '')  # Remove the 'T' => '201603202130'
    return timestamp


def generate_logfile_fullpath(log_directory, filename_pre, filename_post='', filename_extension='.log', insert_datetime=True, specific_logname=None):
    if not log_directory.endswith('\\'):
        log_directory = log_directory + '\\'

    if specific_logname:
        filename = specific_logname
    else:
        filename = generate_logfilename(filename_pre, filename_post, filename_extension, insert_datetime, None)

    filepath = log_directory + filename

    return filepath


def generate_logfilename(filename_pre, filename_post='', filename_extension='.log', insert_datetime=True, specific_logname=None):
    if specific_logname:
        return specific_logname

    ret_val = ''

    if filename_pre.endswith('.'):
        filename_pre = filename_pre[:-1]

    if insert_datetime:
        timestamp = get_ISOTimestamp_ForLogFilename()
        timeval = '-' + timestamp + '-'
        if filename_pre.endswith('-'):
            filename_pre = filename_pre[:-1]
        if filename_post.startswith('-'):
            filename_pre = filename_pre[1:]
    else:
        timeval = ''

    if filename_post.endswith('.'):
        filename_pre = filename_pre[:-1]

    if not filename_extension.startswith('.'):
        filename_extension = '.' + filename_extension

    ret_val = filename_pre + timestamp + filename_extension

    return ret_val


def convert_text_to_boolean(text):
    y = frozenset(['yes', 'y', 'true', 'defintely', 'totally'])
    n = frozenset(['no', 'n', 'false', 'nuh-uh no way'])
    if text.lower() in y:
        return True
    if text.lower() in n:
        return False
    return None

