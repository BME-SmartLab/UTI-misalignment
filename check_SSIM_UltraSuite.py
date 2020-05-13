'''
Written by Tamas Gabor Csapo <csapot@tmit.bme.hu>
First version Jan 20, 2020
restructured for ultrasound Feb 4, 2020
restructured for inversion/UltraSuite April, 2020
resturctured for transducer misalignment detection May 13, 2020

Keras implementation of 
Tamas Gabor Csapo, Kele Xu,
,,Transducer Misalignment Detection in Ultrasound Tongue Imaging'', submitted to Interspeech 2020.
-> this script is for measuring SSIM on the UltraSuite data
'''

# disable pandas FutureWarning
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import numpy as np
import glob
import pickle
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import pandas as pd
import os
import random
import skimage

# https://github.com/UltraSuite/ultrasuite-tools
import sys
sys.path.append('../ultrasuite-tools/')
from ustools.read_core_files import parse_parameter_file,read_ultrasound_file

# pip3 install pyssim
from PIL import Image
from ssim import SSIM
from ssim.utils import get_gaussian_kernel

# SSIM
gaussian_kernel_sigma = 1.5
gaussian_kernel_width = 11
gaussian_kernel_1d = get_gaussian_kernel(gaussian_kernel_width, gaussian_kernel_sigma)



# TODO: modify this according to your data path
dir_base = "/shared/UltraSuite/core-uxtd/core/"

# parameters of ultrasound data
NumVectors = 63
PixPerVector = 412

# data from UltraSuite, https://ultrasuite.github.io/download/
# 2 male and 2 female speakers 
# speakers = ['01M', '02M', '03F', '06F']

speakers = []
if os.path.isdir(dir_base):
    for sp in sorted(os.listdir(dir_base)):
        if os.path.isdir(dir_base + sp):
            speakers += [sp]

print(speakers)

for speaker in speakers:
    if not os.path.exists('measures/' + speaker + '_SSIM_avg.pkl'):
        dir_ult = os.path.join(dir_base, speaker)
        
        # load all .ULT file
        files_ult = dict()
        ult = dict()
        melspec = dict()
        files_ult['all'] = []
        if os.path.isdir(dir_ult):
            for file in sorted(os.listdir(dir_ult)):
                if file.endswith('.ult'):
                    files_ult['all'] += [file[:-4]]
        
        ult_all = dict()
        
        for basefile in files_ult['all']:
            print('start loading ultrasound data: ', speaker, basefile)
            
            # NumVectors=63
            # PixPerVector=412
            # ZeroOffset=50
            # BitsPerPixel=8
            # Angle=0.038
            # Kind=0
            # PixelsPerMm=10.000
            # FramesPerSec=121.486
            # TimeInSecsOfFirstFrame=0.49265
            params = parse_parameter_file(os.path.join(dir_ult, basefile + '.param'))
            
            assert int(params['NumVectors'].value) == NumVectors
            assert int(params['PixPerVector'].value) == PixPerVector
            
            # load ultrasound data
            ult_data = read_ultrasound_file(os.path.join(dir_ult, basefile + '.ult'))
            ult_data_3d = ult_data.reshape((-1, NumVectors, PixPerVector))
            
            ult_data_3d_mean = np.mean(ult_data_3d, axis=0)
            
            # save mean image
            # plt.imshow(ult_data_3d_mean, cmap='gray')
            # plt.savefig('figs/' + speaker + '_' + basefile + '_mean.png')
            # plt.close()
            
            ult_all[speaker + '-' + basefile] = ult_data_3d_mean
        
        # now all ult files are loaded
        
        SSIM_all = np.zeros((len(ult_all), len(ult_all)))
        
        # calculate SSIM utterance by utterance
        ult_keys = list(sorted(ult_all.keys()))
        for i in range(len(ult_all)):
            for j in range(len(ult_all)):
                print('calc SSIM', speaker, i, j, '      ', end='\r')
                SSIM_all[i, j] = SSIM( \
                    Image.fromarray(ult_all[ult_keys[i]].reshape(NumVectors, PixPerVector), 'L'), \
                    gaussian_kernel_1d).ssim_value( \
                    Image.fromarray(ult_all[ult_keys[j]].reshape(NumVectors, PixPerVector), 'L'))
        print('calc SSIM', speaker, 'done')
        
        # serialize results to file
        pickle.dump(SSIM_all, open('measures/' + speaker + '_SSIM_avg.pkl', 'wb'))
    else:
        SSIM_all = pickle.load(open('measures/' + speaker + '_SSIM_avg.pkl', 'rb'))

    print(speaker, ', len:', len(SSIM_all), ', SSIM min/max: ', np.min(SSIM_all), np.max(SSIM_all))
    
    # visualize results
    # vmax set according to manual checking 
    plt.imshow(SSIM_all, cmap='Greys_r', vmin=0., vmax=0.5)
    plt.title('SSIM, ' + speaker)
    plt.xlabel('Time (utterance no.)')
    plt.ylabel('Time (utterance no.)')
    plt.savefig('figs/' + speaker + '_SSIM_matrix.png')
    plt.close()











