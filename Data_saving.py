"""
Created on ..., .. December 2021

@author Eloi Schlegel
"""

import os
import sys
import time
from datetime import datetime
import mercury

# Important to avoid importation problems
path_code = os.path.dirname(__file__)
sys.path.append(os.path.abspath(path_code))

import mercury_functions

path_general    = os.path.abspath(os.path.join(path_code, os.pardir))
path_data       = os.path.join(path_general, "data")
path_experiment = os.path.join(path_data, "Experiments_timed_2")

reader = mercury_functions.init_reader(antenna = [2], epc_target = b'00000000000000100000042D')
#reader = mercury_functions.init_reader(antenna = [1,2])
# DogBone: E28011700000020A7B2E0163
# BAP1: 300833B2DDD9014000000000
# Wristband: b'00000000000000100000042D'


start = datetime.now()

class MessageRecorder():
    def __init__(self):
        self.messages = []

    def __call__(self, msg):
        self.messages.append(msg)


def function_generator(split_char = " "):
    '''
    Define the function to display the data
    '''
    fct = lambda tag: recorder(str(tag.epc) + split_char + str(tag.rssi) + split_char + str(tag.antenna) + split_char
                                    + str(datetime.fromtimestamp(tag.timestamp)).split()[0] + split_char
                                    + str(datetime.fromtimestamp(tag.timestamp)).split()[1] )

    return fct, split_char


def function_generator2(split_char = " "):
    '''
    Define the function to display the data
    '''
    fct = lambda tag: recorder(str(tag.epc) + split_char + str(tag.rssi) + split_char + str(tag.antenna) + split_char
                                    +  str(datetime.fromtimestamp(tag.timestamp) - start )[5::])

    return fct, split_char


def run_reading(recorder, Extractor, time_experiment=5):
    '''
    Run the data measurement
    '''
    print("\n--- Reading in progress ---")
    split_char = Extractor[1]

    recorder("EPC" + split_char + "RSSI" + split_char + "Antenna" + split_char + "Time" )

    reader.start_reading(Extractor[0])
    time.sleep(time_experiment)
    reader.stop_reading()


def export_data_txt(recorder, exp_name = "exp__", file_name = "Saved_data.txt"):
    """
    Function to export data in a txt file in a given folder
    """

    path_exp = os.path.join(path_experiment, exp_name)
    path = os.path.join(path_exp, file_name)

    # Create folder if needed
    try:
        os.mkdir(path_exp)
    except:
        print("Folder already exist")

    # Create/overwrite the file
    try:
        textfile = open( path , "w")
        for element in recorder.messages:
            textfile.write(element + "\n")
        textfile.close()
        print("\n--- Data Exported ---")
    except:
        print("\nError occured: data not exported")


def save_data(recorder):
    Data=[]
    for i in range(len(recorder.messages)):
        Data.append(recorder.messages[i].split() )

    return Data


print("--- Initialization Done ---")
############################################################################################################################3

time.sleep(2) # TIMER BEFORE THE RECORDING START

for i in range(1,6):
    input()
    start = datetime.now()

    print(i)
    recorder = MessageRecorder()

    Extractor = function_generator2(split_char = ",")

    run_reading(recorder, Extractor, time_experiment = 5 )

    export_data_txt(recorder, "Ground_3_BAP_wrist",file_name = str(i) +".txt")
    #export_data_txt(recorder)


#print(recorder.messages[0:2], "\n")

##### Treat data #####
Data = save_data(recorder)
#print( Data [0:2] )

# sudo rm -r folder