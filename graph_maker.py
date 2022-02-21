"""
Created on Friday, 31 December 2021

@author Eloi Schlegel
"""

import sys
import os

import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(""))
print(sys.path)

import toolbox


def extract_data(path):
    """
    Extract data from the file

    Return
    ------

    EPC, RSSI, Antenna, Time - Numpy Array - Dimension: [1xN] with N, the number of elements
    """

    Data_file = toolbox.data_from_txt(path)

    if Data_file == []:
        return 0,0,0,0

    array_data = np.array(Data_file)
    N = len(Data_file)

    for i in range(N):
        array_data[i,-1] = array_data[i,-1][:-1]  # remove \n at the end of the line fixed with time

    EPC     = array_data[1:,0]
    RSSI    = array_data[1:,1].astype(int)
    Antenna = array_data[1:,2].astype(int)
    Time    = array_data[1:,3].astype(float)

    return EPC, RSSI, Antenna, Time


def plot_graph(path, path_save = None):
    """
    Plot the graph from one file (path) and save the .png of the result in the selected folder (path_save)
    """

    if path_save == None:
        path_save = os.path.dirname(path)
    
    filename = os.path.basename(path)[:-4]

    _, RSSI, _, Time = extract_data(path)
    plt.plot(Time, RSSI)
    plt.xlabel("Time [s]")
    plt.ylabel("RSSI [dBm]")
    plt.title("Graph: " + filename)

    path_save_file = os.path.join(path_save, filename + ".png")

    print(path_save_file)
    plt.savefig(path_save_file)
    plt.clf()


def plot_folder(path, path_save = None):
    """
    Plot all the curves of the same folder on one plot and save it in the selected folder (path_save)
    """
    if path_save == None:
        path_save = path

    filenames  = [ x for x in os.listdir(path) if ".txt" in x]

    foldername = os.path.basename(path)
    path_save  = os.path.join(path_save, foldername + ".png")

    for filename in filenames:

        path_file = os.path.join(path, filename)
        
        _, RSSI, _, Time = extract_data(path_file)
        plt.plot(Time, RSSI)
    
    plt.xlabel("Time [s]")
    plt.ylabel("RSSI [dBm]")

    plt.title(foldername)
    plt.legend(filenames)

    print( path_save)
    plt.savefig(path_save)
    plt.clf()


def plot_ind_graphs(path, path_save = None):
    """
    Plot all the curves of the same folder independently and save them in the folder path_save
    """

    filenames  = [ x for x in os.listdir(path) if ".txt" in x]

    for filename in filenames:
        path_file = os.path.join(path, filename)
        plot_graph(path_file, path_save)


def plot_multi_folder( path, path_save = None, fonction = plot_ind_graphs):
    """
    Execute the given fonction for all the folder or file in the selected directory
    """

    path_folder_save = None
    dir_list = os.listdir(path)

    folders_list  = [ x for x in dir_list if "." not in x ]

    for folder in folders_list:
        path_folder = os.path.join(path,folder)

        if path_save != None:
            path_folder_save = os.path.join(path_save,folder)
            toolbox.create_folder(path_folder_save)
    
        if fonction == "Ind": #si ne fonctionne pas -> only keep the comment line
            plot_ind_graphs(path_folder, path_folder_save)
        elif fonction == "Together":
            plot_folder(path_folder, path_folder_save)

        #fonction(path_folder, path_folder_save)

    print("Process complete")


def plot_comparison(path, path_save= None, target=""):
    """
    Plot the first curves of several folders
    """

    if path_save == None:
        path_save = path

    dir_list = os.listdir(path)

    folders_list  = [ x for x in dir_list if "." not in x ]
    folders_target = [x for x in folders_list if target in x]

    Curves_names = []

    for folder in folders_target:
        
        path_file = os.path.join(path,folder,"0.txt")

        _, RSSI, _, Time = extract_data(path_file)
        plt.plot(Time, RSSI)

        print(folder)
        Curves_names.append(folder)

    if target == "":
        Title = "All cases"
    else:
        Title = "Comparison between the " + target

    plt.xlabel("Time [s]")
    plt.ylabel("RSSI [dBm]")
    #plt.axis([0, 7, -80, -40])
    plt.title(Title)
    plt.legend(Curves_names)

    plt.savefig(os.path.join(path_save, "plot_test.png"))

    print("not finsihed")


if __name__ == '__main__':

    path = "/home/moi/Documents/data/Live_eval/T_scan_eval/Solo/Mid"

    fct = plot_folder

    plot_multi_folder(path, fonction="Together")

    print('\n graph_maker file executed')