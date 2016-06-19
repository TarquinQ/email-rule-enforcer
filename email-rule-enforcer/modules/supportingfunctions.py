import sys
import datetime
import collections
from collections import OrderedDict


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


def convert_text_to_boolean(text, default=None):
    y = frozenset(['yes', 'y', 'true', 'affirmative', 'defintely', 'totally'])
    n = frozenset(['no', 'n', 'false', 'None', 'negatory', 'nuh-uh no way'])
    if str(text).lower() in y:
        return True
    if str(text).lower() in n:
        return False
    return default


def force_text_to_boolean(text):
    return convert_text_to_boolean(text, default=False)


def print_nested_data(element, depth=0, maxdepth=30):
    def align_output(depth):
        print (" " * depth, end="")

    # Ensure max recursion
    if depth > maxdepth:
        print ('Data Recursion Max depth of', maxdepth, 'has now been exceeded,')
        print (' Now ignoring this branch of the structure.')
        return

    # Check to see if this is a list/dict/other:
    if isinstance(element, str) or not isinstance(element, collections.Iterable):
        align_output(depth)
        print (element)
    else:
        align_output(depth)
        print(type(element), end=" ")
        if isinstance(element, dict):
            print('{')
            for key in element:
                align_output(depth + 1)
                if isinstance(element[key], collections.Iterable) and not isinstance(element[key], str):
                    print(key, ':')
                    print_nested_data(element[key], depth + 2)
                else:
                    print('%s: %s' % (key, element[key]))
            align_output(depth)
            print('}')
        else:
            if isinstance(element, list):
                print('[')
            else:
                print('(')
            for el in element:
                if isinstance(el, collections.Iterable) and not isinstance(el, str):
                    print_nested_data(el, depth + 1)
                else:
                    align_output(depth + 1)
                    print(el)
            if isinstance(element, list):
                align_output(depth)
                print(']')
            else:
                align_output(depth)
                print(')')


def nested_data_to_str(element, depth=0, maxdepth=30):
    return_arr = []

    def align_output(depth):
        return " " * depth

    # Ensure max recursion
    if depth > maxdepth:
        return_arr.append('Data Recursion Max depth of', maxdepth,
            'has now been exceeded, Now ignoring this branch of the structure.')
        return

    new_str = ''
    # Check to see if this is a list/dict/other:
    if isinstance(element, str) or not isinstance(element, collections.Iterable):
        return_arr.append(align_output(depth) + str(element))
    else:
        new_str = align_output(depth)
        new_str += str(type(element))
        if isinstance(element, dict):
            new_str += '{'
            return_arr.append(new_str)
            for key in element:
                new_str = align_output(depth + 1)
                if isinstance(element[key], collections.Iterable) and not isinstance(element[key], str):
                    new_str += '%s:' % key
                    return_arr.append(new_str)
                    return_arr.append(nested_data_to_str(element[key], depth + 2))
                else:
                    new_str += '%s: %s' % (key, element[key])
                    return_arr.append(new_str)
            return_arr.append(align_output(depth) + '}')
        if isinstance(element, list):
            new_str += '['
            return_arr.append(new_str)
        if isinstance(element, set) or isinstance(element, tuple):
            new_str += '('
            return_arr.append(new_str)
        if isinstance(element, (list, set, tuple)):
            for el in element:
                if isinstance(el, collections.Iterable) and not isinstance(el, str):
                    return_arr.append(nested_data_to_str(el, depth + 1))
                else:
                    return_arr.append(align_output(depth) + str(el))
        if isinstance(element, list):
            return_arr.append(align_output(depth) + ']')
        if isinstance(element, set) or isinstance(element, tuple):
            return_arr.append(align_output(depth) + ')')
    return return_arr


