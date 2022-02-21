"""
Created on Tuesday, 28 December 2021

@author Eloi Schlegel
"""

import os
import sys
import time
from datetime import datetime
import threading

# Important to avoid importation problems
path_code = os.path.dirname(__file__)
sys.path.append(os.path.abspath(path_code))

import mercury_functions
import toolbox

Path_general = os.path.abspath(os.path.join(path_code, os.pardir))
Path_data    = os.path.join(Path_general, "data")
Path_Demo    = os.path.join(Path_data, "Demo_Counting")

#------------------
### Parameters: ###
#------------------
THRESHOLD    = -80  # in dBm
TIME_TOO_OLD = 9    # in seconds
TIME_1_PASS  = 20    # in seconds
T_SCAN       = 100   # in ms / min 50ms

List_Tags = [b'300833B2DDD9014000000000', # BAP fat 1
             b'000000000000000000112602'] # BAP fat 2

mode = "Real"   # Real or Sim
###################

print("\n\n ************** MAKE SURE BOTH PORTS ARE CONNECTED ************** \n \n") # Confirm with 'OK' ")
mode = input("Real or Sim ?")

# structure for Flags
class states:
    Run          = False
    Save         = False
    T_start_save = datetime.now()
    Thread       = True
    Request      = "Nothing"
    Protocol     = False
    Bus          = []           # Use to exchange data between main loop and thread

Flags = states()

if mode == "Real":
    reader = mercury_functions.init_reader( epc_target= List_Tags)
    mercury_functions.reading_power_set(reader)
elif mode == "Sim":
    reader = "The_BRoT" # The Big Reader of Tags


############################## Functions defintion ##############################


def duplicate_destroyer(read_tags):
    """
    Take the list of tags detected and delete the duplicates with the lower signal to keep only the strongest

    """
    tags = read_tags.copy()
    to_delete = []
    N = len(tags)

    for i in range(N-1):

        if i in to_delete:
            continue

        for j in range( i+1, N):
            if tags[i][0] == tags[j][0]:

                diff = tags[i][1] - tags[j][1]
                if diff > 0:
                    #kepp i
                    to_delete.append(j)
                elif diff < 0:
                    #keep j
                    to_delete.append(i)
                else:
                    to_delete.append(i)
                    to_delete.append(j)

    to_delete.sort()
    to_delete.reverse()

    # Remove tags which should
    for i in to_delete:
        tags.pop(i)

    return tags


def state_update( EPCs, Tags, read_tags, Counter ):
    """
    Update the counter by evaluating new tag detected or the one to old which are out of the passage
    """

    read_tags_u = duplicate_destroyer(read_tags)

    # Stacker
    for i in range( len(read_tags_u) ):
        if read_tags_u[i][1] > THRESHOLD:

            try:
                # MaJ
                ind = EPCs.index( read_tags_u[i][0] )
                #print("\n\n\n\n\nSeen index: ", ind)
                Tags[ind][2:] = read_tags_u[i][2:]

            except:
                # Add new
                ind = None
                new = [read_tags_u[i][0],read_tags_u[i][2], 0, datetime.today()]
                Tags.append(new) # add new: epc, antenna, time
                EPCs.append(read_tags_u[i][0])
                
    # detect old tags
    ind = toolbox.outoftime_tags( Tags, limit = TIME_TOO_OLD)

    # delete old tags
    for i in ind[::-1]: # supp in a reverse a way to not generate problem of index
        Counter += (Tags[i][2] - Tags[i][1])                                                # add variable counting incoming and outcoming person
        Tags.pop(i)
        EPCs.pop(i)

    return EPCs, Tags, read_tags_u, Counter


def displayer_menu():
    """
    Display the menu with all the commands
    """
    print("\n\n\n\n\n ***** Menu *****\n")
    print(" r - Run the reader")
    print(" s - Save the data read")
    print(" e - Export saved data")
    print(" d - Delete the save data")
    print(" P - Run a protocol to analye a scenario")
    print(" m - Display this menu")
    print("\n q - Quit the program")


def displayer(Counter=0, read_tags=[], Tags=[]):
    """
    Display the information of reading ( counter, nb tag detected)
    """

    print("\n\n\n\n*** Counter - ",Counter," ***\n","nb tag detected:", len(read_tags) )
    print("\n Mode:", "Reading" if Flags.Run else "       ", "  Saving" if Flags.Save else "", "\n" )
    # print current tags
    for tag in Tags:
        print(tag)


def list_to_str( read_tags ):
    """
    Change a list into a string in the format [EPC,RSSI,Antenna,Time]
    """

    return [line[0] + "," + str(line[1]) + "," + str(line[2]) + "," + str(line[3] - Flags.T_start_save)[5::]  for line in read_tags]


def export_data(records_reading, records_counter, path = None):

    if path == None:
        print( "\n\n Name of the folder: ", end="")
        folder_name = input()
        path = os.path.join(Path_Demo, folder_name)

    toolbox.create_folder(path)

    path_file = os.path.join(path,"reading.txt")
    toolbox.data_to_txt(records_reading, path_file)
    path_file = os.path.join(path,"counter.txt")
    toolbox.data_to_txt(records_counter, path_file)


def export_sumup(records_count_p, counter_p, path):
    global Flags

    path_file = os.path.join(path,"Sumup.txt")

    records_count_p.append("----------------" )
    records_count_p.append("Total count: " + str(counter_p))
    records_count_p.append("" )
    records_count_p.append("Parameters:" )
    records_count_p.append(" THRESHOLD    = " + str(THRESHOLD) + " dBm")
    records_count_p.append(" TIME_TOO_OLD = " + str(TIME_TOO_OLD) + " s")
    records_count_p.append(" TIME_1_PASS  = " + str(TIME_1_PASS) + " s")
    records_count_p.append(" T_SCAN       = " + str(T_SCAN) + " ms" )
    records_count_p.append("")
    records_count_p.append("Experience details:")
    records_count_p.append(Flags.Bus[0])
    records_count_p.append(Flags.Bus[1])
    records_count_p.append(Flags.Bus[2])

    toolbox.data_to_txt(records_count_p, path_file)

    Flags.Protocol = False


def thread_reading( ):
    """
    Function in charge to constantly read and collect data
    """
    global Flags

    Tags = [] # EPC, first antenna, last antenna, time last detection
    EPCs = [] # list of the epc of all the detected tags

    Counter = 0
    n_round = 0
    counter_p = 0

    records_reading = ["EPC, RSSI, Antenna , Time"]
    records_counter = ["Counter, Time"]
    records_count_p = ["Round, Counter"]

    displayer_menu()
    while Flags.Thread:
        
        read_tags = []

        # Reading step
        if Flags.Run:
            read_tags = mercury_functions.get_read_data(reader, T_SCAN, mode)
            #read_tags = mercury_functions.get_read_data2(reader, T_SCAN, List_Tags, mode )                        # must be test !!!!!!!!!!!!!
            EPCs, Tags, read_tags_u, Counter = state_update( EPCs, Tags, read_tags, Counter )

            displayer( Counter, read_tags_u, Tags )
            print("\n\n", read_tags)                                                                                # temp

            if Flags.Save == True:
                records_reading.extend( list_to_str( read_tags ) )
                records_counter.append(str(Counter) + "," + str(datetime.now() - Flags.T_start_save)[5:])
        
        if Flags.Request == "e":        # Export data
            Flags.Request = "Nothing"
            export_data(records_reading, records_counter)
            displayer()

        if Flags.Request[:3] == "exp":  # Export data
            path_exp = Flags.Request[3:]
            export_data(records_reading, records_counter, path_exp)

            if Flags.Protocol == True:
                n_round += 1
                counter_p += Counter
                sgn = "+" if Counter>-1 else "" 
                records_count_p.append( " " + str(n_round) + "    , " + sgn + str(Counter) )

            Flags.Request = "Nothing"

        if Flags.Request == "d":        # Delete data
            records_reading = ["EPC, RSSI, Antenna , Time"]
            records_counter  = ["Counter, Time"]
            Counter = 0
            Flags.Request = "Nothing"

        if Flags.Request[:14] == "Sumup_protocol":
            path = Flags.Request[14:]
            export_sumup(records_count_p, counter_p, path)
            Flags.Request = "Nothing"

        if Flags.Protocol == False:
            records_count_p = ["Round, Counter"]
            n_round = 0
            counter_p = 0


# EPCs = list of the epc of all the detected tags
# Tags = states of each detected tags [EPC, first antenna, last antenna, last time]


def the_protocol():
    global Flags

    Flags.Run = False

    print("\n\n\n\n\n *** Protocol launched ***\n\n")
    name_exp        = input("Name experiment: ")
    nb_passage      = int(input("Nb passage: "))
    antenna_type    = "Antenna type:  " + input("Type of antenna/position: ")
    antenna_space   = "Antenna space: " + input("Space between antenna [cm]: ") + " cm"
    tag_type        = "Type of tag:   " + input("Type of tag: ")
    Flags.Bus       = [antenna_type, antenna_space, tag_type]

    path_situ = os.path.join(Path_Demo, name_exp)
    toolbox.create_folder(path_situ)

    ######################################
    # v # The Protocol: Change below # v #
    ######################################

    Flags.Save = True
    for i in range(nb_passage):

        time.sleep(0.5)
        input("* "+ str(i+1))

        Flags.Run  = True
        Flags.Request = "d"
        Flags.T_start_save = datetime.now()
        time.sleep(TIME_1_PASS)
    
        Flags.Run  = False
        path_pass  = os.path.join(path_situ, "Pass" + str(i+1))
        Flags.Request = "exp" + path_pass       # pass the path of the folder in the Request

    time.sleep(0.5)
    Flags.Request = "Sumup_protocol" + path_situ

    ######################################
    # ^ # End of the Protocol        # ^ #
    ######################################

    print("\n\n\n\n\n *** End of the protocol ***\n\n")


def main():
    global Flags

    thr = threading.Thread(target = thread_reading )
    thr.start()

    while Flags.Thread:

        request = input()
        Flags.Request = request

        if request == "q":
            Flags.Thread = False

        if request == "r":
            Flags.Run = not Flags.Run

        if request == "s":
            Flags.Save = not Flags.Save
            if Flags.Save:
                Flags.T_start_save = datetime.now()        

        if request == "e":
            time.sleep(1)

        if request == "d":
            time.sleep(1)

        if request == "P":
            time.sleep(1)
            Flags.Protocol = True
            the_protocol()
            time.sleep(1)
            displayer_menu()

        if request == "m":
            displayer_menu()


if __name__ == '__main__':

    main()

    print('file executed')