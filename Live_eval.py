"""
Created on ..., .. December 2021

@author Eloi Schlegel
"""

import time
from datetime import datetime
import mercury
import threading

import os

from mercury_functions import init_reader

path_code = os.path.dirname(__file__)
path_general = os.path.abspath(os.path.join(path_code, os.pardir))
Path_data = os.path.join(path_general, "data")
Path_save = os.path.join(Path_data, "Live_eval")

start = datetime.now() # mettre plus bas ?                  -----------

reader = init_reader()

print("\n\n ************** MAKE SURE BOTH PORT ARE CONNECTED ************** ")
input()

class states:
    page = "Menu"   # Menu, Read, Settings
    target = None
    read = False    # True, False
    save = False    # True, False
    thread = True   # True, False


def settings(time, S_g):
    print("\n\n\n##### Settings #####\n")

    print("Change the refresh time ? y/n\n")
    if input() == "y":
        print(" * Refresh time [ms]:")
        try:
            n_time = int(input()) #refresh time in ms
        except:
            print(" *** Not a number! ***\n")
    else:
        n_time = time

    print("Change the target ? y/n\n")
    if input() == "y":

        n_target = None

        while n_target == None:
            temp = reader.read()
            try:
                print("Is it the tag to track ?\n", temp[0],"y/n")
            except:
                print("No tag dedected, try again!")
                next

            x = input()
            if x == "y":
                n_target = str(temp[0])[2:-1].encode() # encode the EPC to get a binary format
            elif x == "xx":
                print("No chosen target\n")
                break
    else:
        n_target = S_g.target

    print("Change the reading power ?")
    if input() == "y":
        print(" * Current Reading power: ", reader.get_read_powers())
        
        try:
            print(" * Choose an antenna ?")
            a = int(input())
            print(" * Choose a power between the following range ?", reader.get_power_range())
            b = int(input())
            reader.set_read_powers([(a, b)])
        except:
            print(" *** Settings: error - no changement occur ***")

    return n_time, n_target


def save_Data(d_ant1, d_ant2):
    for element in d_ant1:
        data[0].append(element)
    for element in d_ant2:
        data[1].append(element)
    return data


def export_data(data, folder_name = None):

    if data == None:
        print("No data to export")
        return

    # Create folder if needed
    if folder_name == None:
        folder = input("Name the folder:" )
    else:
        folder = folder_name

    path_exp = os.path.join(Path_save, "test")
    path = os.path.join(Path_save, folder)
    try:
        os.mkdir(path)
    except:
        print("*** Error: Folder already exists or Folder not created")

    # Save the data
    try:
        textfile = open(path+"/ant1.txt", "w")
        for element in data[0]:
            textfile.write(str(element[0])+ "," + str(element[1]) + "," + str(element[2]) + "," + str(element[3]) + "\n")
        textfile.close()

        textfile = open(path+"/ant2.txt", "w")
        for element in data[1]:
            textfile.write(str(element[0])+ "," + str(element[1]) + "," + str(element[2]) + "," + str(element[3]) + "\n")
        textfile.close()

        print("\n--- Data saved ---")
    except:
        print("\nExport_data(): *** Error occured: Data are not saved ***")


def EPCs_displayer():
    #States
    global S_g
    
    # Variables
    global t_refresh
    global data

    epcs_1 = None
    epcs_2 = None

    while S_g.thread:

        if S_g.read:
            reader.set_read_plan([1], "GEN2", epc_target = S_g.target)
            epcs_1 = list( map( lambda t: [t.epc, t.rssi, t.antenna, str(datetime.fromtimestamp(t.timestamp) - start)[5::] ], reader.read(timeout = int(t_refresh/2)) ) )

            reader.set_read_plan([2], "GEN2", epc_target = S_g.target) 
            epcs_2 = list( map( lambda t: [t.epc, t.rssi, t.antenna, str(datetime.fromtimestamp(t.timestamp) - start)[5::] ], reader.read(timeout = int(t_refresh/2)) ) )

            if S_g.save:
                data = save_Data(epcs_1, epcs_2)
                print("saving\n")

        displyer(S_g, epcs_1, epcs_2)


def displyer(S_g, epcs_1, epcs_2):
    global t_refresh

    if S_g.page == "Menu":
        print("\n\n\n\n\n\n\n\n\n### Menu: ###\n\n r: reading\n p: parameters\n q: quit")
        while S_g.page == "Menu":
            time.sleep(1)

    elif S_g.page == "Read":
        # Display mode
        print("\n\n\n\n\n", "Mode: ", "Normal" if S_g.target == None else "Target")

        # Display reading and saving
        print("\n\n", "Reading" if S_g.read else "       ", " & " if S_g.read and S_g.save else " ", "Saving" if S_g.save else "      ", "\n")

        # Display what is read
        if S_g.target == None:
            print("\n Antenna 1:\n", epcs_1, "\n\n Antenna 2: \n", epcs_2, "\n")
        else:
            print("Target = ", S_g.target, "\n")
            print("Antenna 1: ", 1 if epcs_1 else 0, "  / Antenna 2: ", 1 if epcs_2 else 0 )
            print("\n Antenna 1:\n", epcs_1, "\n\n Antenna 2: \n", epcs_2, "\n")

        while (S_g.read == False) and S_g.page == "Read" and S_g.thread:
            time.sleep(1)


def program_measure():
    global t_refresh
    global S_g

    t_scan_test = [10, 30, 50, 100, 300, 500, 1000]
    for t in t_scan_test:
        t_refresh = t

        #reset data
        data = [[],[]]

        #read mode
        S_g.page = "Read"
        S_g.read = True

        #save mode
        S_g.save = True
        start = datetime.now()

        # wait
        time.sleep(3)

        #stop
        S_g.save = False
        S_g.read = False

        # export
        name_fold = "Ant2_"+str(t_refresh) +"_2"
        export_data(data, name_fold)

    print( "\n\n\n\n\n\n ************* FINIIIIIII ******** \n\n\n\n\n\n ")


print("--- Initialization Done ---")
############################################################################################################################

S_g = states()
#page, mode, read , save , thread

data = [[],[]]
t_refresh, S_g.target = 100, None #settings()

thr = threading.Thread(target=EPCs_displayer)
thr.start()

x = None
##### Exit part #####
while x != "q":

    x = input()

    ##### Menu #####
    if x == "m":
        S_g.page = "Menu"
        S_g.read = False

    ##### Read #####
    elif x == "r":
        # start reading data or stop reading
        S_g.page = "Read"
        S_g.read = False if S_g.read else True

    elif x == "s" :
        # start saving data or stop saving
        S_g.save = False if S_g.save else True

        start = datetime.now()

    elif x == "e":
        # Export the saved data
        export_data(data)
    
    elif x == "d":
        # Delete the saved data
        data = [[],[]]
        print("data deleted")

    elif x == "show":
        # Show the saved data
        print("\n\n Last read tag:\n")
        try:
            print("Antenna 1:\n", data[0][-1])
        except:
            print("antenna 1:\n no data read")

        try:
            print("\n\nAntenna 2:\n", data[1][-1])
        except:
            print("antenna 2:\n no data read")
    
    elif x == "p":
        S_g.page = "Settings"
        S_g.read = False
        print("\n\n\n\n\n\n")
        t_refresh, S_g.target = settings(t_refresh, S_g)
        S_g.page = "Menu"

    if x == "GO":
        program_measure()
        


S_g.page = None
S_g.thread = False
time.sleep(1)
print("\ntschus")


