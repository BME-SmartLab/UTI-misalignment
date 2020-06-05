'''
Written by Tamas Gabor Csapo <csapot@tmit.bme.hu>
First version Jan 20, 2020
restructured for ultrasound Feb 4, 2020
restructured for inversion/UltraSuite April, 2020
resturctured for transducer misalignment detection May 13, 2020
resturctured for easier use with other databases June 5, 2020


Python implementation of 
Tamas Gabor Csapo, Kele Xu, Andrea Deme, Tekla Etelka Graczi, Alexandra Marko,
,,Transducer Misalignment in Ultrasound Tongue Imaging'', submitted to Interspeech 2020 Show & Tell.
-> this script is for measuring MSE and plotting the MSE matrix
'''

import numpy as np
import glob
import pickle
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import pandas as pd
import os
import random
import skimage

from optparse import OptionParser

# read_ult reads data from raw scanline *.ult file of AAA
def read_ult(filename, NumVectors, PixPerVector):
    # read binary file
    ult_data = np.fromfile(filename, dtype='uint8')
    ult_data = np.reshape(ult_data, (-1, NumVectors, PixPerVector))
    return ult_data

# read_meta reads in *.txt ult metadata file from AAA
def read_meta(filename):    
    NumVectors = 0
    PixPerVector = 0
    # read metadata from txt
    for line in open(filename):
        # 1st line: NumVectors=64
        if "NumVectors" in line:
            NumVectors = int(line[11:])
        # 2nd line: PixPerVector=842
        if "PixPerVector" in line:
            PixPerVector = int(line[13:])
        # 3rd line: ZeroOffset=210
        if "ZeroOffset" in line:
            ZeroOffset = int(line[11:])
        # 5th line: Angle=0,025
        if "Angle" in line:
            Angle = float(line[6:].replace(',', '.'))
        # 8th line: FramesPerSec=82,926
        # Warning: this FramesPerSec value is usually not real, use calculate_FramesPerSec function instead!
        if "FramesPerSec" in line:
            FramesPerSec = float(line[13:].replace(',', '.'))
            
    return (NumVectors, PixPerVector, ZeroOffset, Angle, FramesPerSec)


def calc_and_plot_MSE(dir_ult):
    speaker = os.path.basename(os.path.normpath(dir_ult))
    
    if not os.path.exists('measures/' + speaker + '_MSE_avg.pkl'):
        
        # list all .ULT file
        print('listing .ULT files in', dir_ult)
        files_ult = dict()
        ult = dict()
        files_ult['all'] = []
        if os.path.isdir(dir_ult):
            for file in sorted(os.listdir(dir_ult)):
                if file.endswith('.ult'):
                    files_ult['all'] += [file[:-4]]
        
        ult_all = dict()
        
        # default values of raw ultrasound metadata
        NumVectors = 64
        PixPerVector = 842
        ZeroOffset = 210
        Angle = 0.025
        FramesPerSec = 120.0 
        
        # UltraSuite database: metadata is in *.PARAM file
        if os.path.isfile(os.path.join(dir_ult, basefile + '.param')):
            (NumVectors, PixPerVector, ZeroOffset, Angle, FramesPerSec) = \
                read_meta(os.path.join(dir_ult, basefile + '.param'))
        
        # Hungarian ultrasound database: metadata is in *US.txt file
        if os.path.isfile(os.path.join(dir_ult, basefile + 'US.txt')):
            (NumVectors, PixPerVector, ZeroOffset, Angle, FramesPerSec) = \
                read_meta(os.path.join(dir_ult, basefile + 'US.txt'))
        
        for basefile in files_ult['all']:
            print('start loading ultrasound data: ', basefile)
            
            # load ultrasound data
            ult_data_3d = read_ult(os.path.join(dir_ult, basefile + '.ult'), \
                NumVectors, PixPerVector)
            
            # calculate mean ultrasound image for current utterance
            ult_data_3d_mean = np.mean(ult_data_3d, axis=0)
            
            ult_all[speaker + '-' + basefile] = ult_data_3d_mean
        
        # now all ult files are loaded
        
        MSE_all = np.zeros((len(ult_all), len(ult_all)))
        
        # calculate MSE utterance by utterance
        ult_keys = list(sorted(ult_all.keys()))
        for i in range(len(ult_all)):
            for j in range(len(ult_all)):
                print('calc MSE', speaker, i, j, '      ', end='\r')
                MSE_all[i, j] = mean_squared_error(
                               ult_all[ult_keys[i]].reshape(NumVectors * PixPerVector),
                               ult_all[ult_keys[j]].reshape(NumVectors * PixPerVector))
        print('calc MSE', speaker, 'done')
        
        # serialize results to file
        pickle.dump(MSE_all, open('measures/' + speaker + '_MSE_avg.pkl', 'wb'))
        pickle.dump(ult_all, open('measures/' + speaker + '_ult_mean_all.pkl', 'wb'))
    else:
        MSE_all = pickle.load(open('measures/' + speaker + '_MSE_avg.pkl', 'rb'))
        # ult_all = pickle.load(open('measures/' + speaker + '_ult_mean_all.pkl', 'rb'))

    print(speaker, ', len:', len(MSE_all), ', MSE min/max: ', np.min(MSE_all), np.max(MSE_all))
    
    # visualize results, MSE
    # vmax set according to manual checking 
    plt.imshow(MSE_all, cmap='viridis', vmin=0., vmax=800.)
    plt.title('MSE, ' + speaker)
    plt.xlabel('Time (utterance no.)')
    plt.ylabel('Time (utterance no.)')
    plt.colorbar()
    plt.show()
    plt.savefig(speaker + '_MSE_matrix_color.png')
    plt.close()




# command line argument
op = OptionParser()
(option, arg) = op.parse_args()
if (len(arg) < 1):
    print('This is a command line tool for checking ')
    print('Transducer Misalignment in Ultrasound Tongue Imaging,')
    print('   and can be used with raw ultrasound scanline data')
    print("   (e.g. 'Micro' system of Articulate Instruments Ltd.)")
    print('Need 1 argument:')
    print('   please provide a directory containing the raw .ULT files')
    
else:
    # dir_ult = "y:/shared/UltraSuite/core-uxtd/core/"
    dir_ult = arg[0]
    
    print('Start checking ')
    print('Transducer Misalignment in Ultrasound Tongue Imaging,')
    print('on dir: ', dir_ult)
    
    calc_and_plot_MSE(dir_ult)
    
    

