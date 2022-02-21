"""
Created on Thursday, 10 February 2022

@author Eloi Schlegel
"""

import requests
import json

def communicate_staff_in( nb_staff = 1):
    """
    Request to communicate one or several entries
    """
    for i in range(nb_staff):
        # Send one entrance
        pload =  [{"type": "LineCrossing", "direction": "inward"}]
        r = requests.post('http://34.120.144.162:8080/xovis/XOVIS_PC2S_801F12D5EB94_staff_filtering',data = json.dumps(pload))


def communicate_staff_out( nb_staff = 1 ):
    """
    Request to communicate one or several exits
    """
    for i in range(nb_staff):
        # Send one exit
        pload =  [{"type": "LineCrossing", "direction": "backward"}]
        r = requests.post('http://34.120.144.162:8080/xovis/XOVIS_PC2S_801F12D5EB94_staff_filtering',data = json.dumps(pload))


def selector(incr):
    """
    Call the correct function depending of the sign of the incrementation
    """
    if incr > 0:
        communicate_staff_in(incr)
    elif incr < 0:
        communicate_staff_out(incr)


if __name__ == '__main__':

    print('toolbox executed')