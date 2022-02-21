"""
Created on Tuesday, 4 January 2022

@author Eloi Schlegel
"""

import os
import numpy as np
from datetime import datetime, timedelta


def data_from_txt(path:str, split_ch = ","):
    """
    Import data from a .txt file

    Return
    ------
    List of lists:
        each sublist correspond to a line of the txt file
    """

    Data = []
    try:
        with open(path, 'r') as f:
            for line in f:
                Data.append([i for i in line.split(split_ch)])
    except:
        print(" *** Error: File not found or else")

    return Data


def data_to_txt(data, path):
    """
    Export data in a txt file from a list of string
    """

    try:
        textfile = open( path , "w")
        for line in data:
            textfile.write(line + "\n")
        textfile.close()
        print("\n--- Data Exported ---")
        print(path, "\n")
    except:
        print("\nError occured: data not exported\n")


def create_folder( path ):
    """
    Create a folder according to the given path
    """
    
    try:
        os.mkdir(path)
        print("Folder created: ", path)
    except:
        print("Folder already exist or wrong path: ", path)


def put_data_to_norm(path, path_save = None):
    """
    Take data generate by Live_eval.py and normalize ( keep only the second in the time data
     and take the relatif time of the experiment ). Generate a new file .txt with the data in the good format.
    """

    Data = data_from_txt(path)
    new_Data = ["EPC, RSSI, Antenna, Time"]

    if Data == []:
        return

    start_time = float(Data[0][3][-10:-1])

    for line in Data:
        time = str(float(line[3][-10:-1]) - start_time + 2)
        new_line = line[0] + "," + line[1] + "," + line[2] + "," + time
        new_Data.append(new_line)

    if path_save == None:
        path_save = path[:-4] + "_n.txt"

    data_to_txt(new_Data, path_save)


def repetiteur( path_folder, path_folder_save):
    """
    Executre several times the process of normalization of the data
    """
    extra = ""
    if path_folder == path_folder_save:
        extra = "n_"

    filenames  = [ x for x in os.listdir(path_folder) if ".txt" in x]

    print(filenames)
    for filename in filenames:
        path = os.path.join(path_folder, filename)
        path_save = os.path.join(path_folder_save, extra+filename)
        put_data_to_norm(path, path_save)


def outoftime_tags(Tags, limit = 5):
    """
    Evaluate which tag was not detected since too long

    Return
    ------
    list of dimension [n] containing indexes of the time out tags

    """

    ind = []
    for i in range( len(Tags)):
        if ( datetime.today() - Tags[i][3]) > timedelta(seconds=limit):
            ind.append(i)

    return ind


if __name__ == '__main__':
    
    path = "/home/moi/Documents/data/Distance_evaluation_2/ground_both_150cm"
    #path_save = "/home/moi/Documents/data/Distance_evaluation/Data_norm/Count/ant2.txt"
    print("function")
    repetiteur(path, path)

    print('toolbox executed')