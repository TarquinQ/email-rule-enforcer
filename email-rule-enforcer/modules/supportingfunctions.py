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


def get_ISOTimestamp_ForLogFilenames():
    timestamp = datetime.datetime.now().isoformat()  # '2016-03-20T21:30:44.560397'
    timestamp = ''.join(timestamp.split(':')[0:2])  # Remove the seconds & milliseconds => '2016-03-20T2130'
    timestamp = timestamp.replace('T','')  # Remove the 'T' => '2016-03-202130'
    timestamp = timestamp.replace('-','')  # Remove the 'T' => '201603202130'
    return timestamp
