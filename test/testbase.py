import sys
sys.path.insert(1, '..')

from datetime import datetime

def now_timestamp():
    return int(datetime.now().timestamp()*1000)
