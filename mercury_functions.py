"""
Created on Tuesday, 28 December 2021

@author Eloi Schlegel
"""

import time
from datetime import datetime, timedelta
import mercury
import threading

def init_reader(path = "tmr:///dev/ttyACM0", b_rate = 19200, region = "EU3", antenna = [1,2], protocol = "GEN2", epc_target = None):
    """
    Define and initialize the reader to use with the antenna

    """

    reader = mercury.Reader(path, baudrate=b_rate)
    reader.set_region(region)
    reader.set_read_plan(antenna, protocol, epc_target)

    for ant in antenna:
        reader.set_read_powers([(ant, 3000)])

    return reader


def get_read_data(reader, t_scan, mode = "Real"):
    """
    Read the data from the control antenna and return them

    Return
    ------
    list of dimension [n] containing lists of dimension [4]
    n: correspond to the number of tag read by the system (a tag can be read as many times as there are connected antenna)

    """
    if mode == "Real":
        return list( map( lambda t: [str(t.epc)[2:-1], t.rssi, t.antenna, datetime.fromtimestamp(t.timestamp)], reader.read(timeout = t_scan ) ) )
    else:
        time.sleep(t_scan/1000)
        return [["b'000666000'",-42,2,datetime.now()],["b'000666000'",-52,1,datetime.now()],
                ["b'000666001'",-52,1,datetime.now()],["b'000666001'",-43,2,datetime.now()]]


def get_read_data2(reader, t_scan, tags_targ=None, mode = "Real"):
    """
    Read the data from the control antenna and return them

    Return
    ------
    list of dimension [n] containing lists of dimension [4]
    n: correspond to the number of tag read by the system (a tag can be read as many times as there are connected antenna)

    """
    if mode == "Real":
        reader.set_read_plan([1], "GEN2")
        ant1 = list( map( lambda t: [str(t.epc)[2:-1], t.rssi, t.antenna, datetime.fromtimestamp(t.timestamp)], reader.read(timeout = t_scan/2 ) ) )
        reader.set_read_plan([2], "GEN2")
        ant2 = list( map( lambda t: [str(t.epc)[2:-1], t.rssi, t.antenna, datetime.fromtimestamp(t.timestamp)], reader.read(timeout = t_scan/2 ) ) )
        return ant1.extend(ant2)
    else:
        time.sleep(t_scan/1000)
        return [["b'000666000'",-42,2,datetime.now()],["b'000666000'",-52,1,datetime.now()],
                ["b'000666001'",-52,1,datetime.now()],["b'000666001'",-43,2,datetime.now()]]


def reading_power_set(reader):
    """
    Change the reading power used by the antenna

    Return
    ------
    """
    
    print("\n\n\n * Current Reading power: ", reader.get_read_powers())
    
    try:
        print(" * Choose an antenna ?")
        a = int(input())
        print(" * Choose a power between the following range ?", reader.get_power_range())
        b = int(input())
        reader.set_read_powers([(a, b)])
    except:
        print(" *** Settings: error - no changement occur ***")


def test_mercucu():
    print("yaya!!")


if __name__ == '__main__':
    print('mercury_functions file executed')