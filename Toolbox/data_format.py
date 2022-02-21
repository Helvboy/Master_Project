"""
Created on Tuesday, 31 January 2022

@author Eloi Schlegel
"""

import os
from toolbox import create_folder, data_from_txt, data_to_txt


EPC_ID  = 0
RSSI    = 1
ANTENNA = 2
TIME    = 3

def from_raw_to_tidy( raw_data ):
    """
    Sort the data in the normalized format.

    Import a list of lists ̉[4] (only data)

    Export a list of 2 lists of 2 lists where one of them is a list of lists of lists ( data)
    """

    N = len(raw_data)

    tags_epcs = []
    ant_1     = []
    ant_2     = []

    for i in range(N):
        # list tags IDs
        if raw_data[i][EPC_ID] not in tags_epcs:
            tags_epcs.append(raw_data[i][EPC_ID])

        # split data by antenna
        if int(raw_data[i][ANTENNA]) == 1:
            ant_1.append(raw_data[i])
        elif int(raw_data[i][ANTENNA]) == 2:
            ant_2.append(raw_data[i])

    data_1 = []
    data_2 = []

    for epc in tags_epcs:
        data_1.append( [ [i[1], i[3][:-1]] for i in ant_1 if epc in i] )
        data_2.append( [ [i[1], i[3][:-1]] for i in ant_2 if epc in i] )

    return data_1, data_2, tags_epcs


def normalize_file( path, path_save, forlder_name = None):
    
    raw_data = data_from_txt(path)[1:]

    data_1, data_2, tags_epcs = from_raw_to_tidy( raw_data )

    # create directory
    path_folder = os.path.join(path_save, folder_name)
    create_folder(path_folder)
    path_ant1 = os.path.join(path_folder, "Antenna_1")
    path_ant2 = os.path.join(path_folder, "Antenna_2")
    create_folder(path_ant1)
    create_folder(path_ant2)

    # save files
    
    # TODO

    print("Not finished")



if __name__ == '__main__':

    print('\n data_format.py executed')