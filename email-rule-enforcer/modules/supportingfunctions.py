import sys
import datetime
import os
import socket
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


def text_to_bool(text, default=None):
    y = frozenset(['yes', 'y', 'true', 'on', 'affirmative', 'defintely', 'totally'])
    n = frozenset(['no', 'n', 'false', 'off', 'None', 'negatory', 'nuh-uh no way'])
    if str(text).lower() in y:
        return True
    if str(text).lower() in n:
        return False
    return default


def text_to_bool_force(text):
    return text_to_bool(text, default=False)


def text_to_int(text, default=None):
    try:
        ret_val = int(text)
    except:
        ret_val = default
    return ret_val


def strip_quotes(text):
    try:
        text = text.strip('\'\"')
    except AttributeError:
        pass
    return text


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
        if isinstance(element, set):
            new_str += '{'
            return_arr.append(new_str)
        if isinstance(element, tuple):
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
        if isinstance(element, set):
            return_arr.append(align_output(depth) + '}')
        if isinstance(element, tuple):
            return_arr.append(align_output(depth) + ')')
    return return_arr


def get_username():
    return os.getenv('USERNAME', 'Unknown')


def get_hostname():
    hostname = 'Uknown'
    try:
        hostname = socket.gethostname()
    except:
        pass
    return hostname


def get_os():
    return os.uname()


def get_os_str():
    ret_val = ', '.join(get_os())
    return ret_val


def dict_from_list(list_):
    ret_dict = None
    try:
        if len(list_) % 2 == 0:
            ret_dict = dict(list_[n:n+2] for n in range(0, len(list_), 2))
    except (TypeError, ValueError):
        pass
    return ret_dict


def null_func(inst, *args, **kwargs):
    return None


def list_into_chunks(lst, chunk_size):
    return [lst[x:x+chunk_size] for x in range(0, len(lst), chunk_size)]


def iterable_into_chunks(iter, chunk_size):
    curr_chunk_size = 0
    curr_chunk = []
    try:
        for s in iter:
            curr_chunk.append(s)
            curr_chunk_size = (curr_chunk_size + 1) % chunk_size
            if curr_chunk_size == 0:
                yield curr_chunk
                curr_chunk = []
    except TypeError:
        pass
    yield curr_chunk


def is_list_like(iter):
    if (isinstance(iter, list)) or (isinstance(iter, tuple)) or (isinstance(iter, set)):
        return True
    else:
        return False
