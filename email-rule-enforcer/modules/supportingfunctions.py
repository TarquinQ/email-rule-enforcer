import sys


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

