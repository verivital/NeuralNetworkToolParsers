#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 19:06:19 2019

@author: Musau
"""

from __future__ import division, print_function, unicode_literals
import numpy as np
import os
from src.NeuralNetParser import NeuralNetParser
import scipy.io as sio
from onnx import *

import h5py as h5
import json
from pprint import pprint
import keras
from keras import models
from keras.models import load_model
from keras.models import model_from_json
from matplotlib import pyplot as plt

#abstract class for keras printers
class kerasPrinter(NeuralNetParser):
    
    #Instantiate files and create a matfile
    def __init__(self,pathToOriginalFile, OutputFilePath, *vals):
        if not vals:
            
        pass
    def load_model(self):
        pass
    #function for creating the matfile
    def create_matfile(self):
        pass
    #function for creating an onnx model
    def create_onnx_model(self):
        pass
    
    # Load the plant with parameters included
    def load_files(self, modelfile,weightsfile):
        with open(modelfile, 'r') as jfile:
            model = model_from_json(jfile.read())
        model.load_weights(weightsfile)
        return model
    #model = load_files(modelfile,weightsfile)
    
    #Load the size of the plant
    def get_shape(self, model):
        nl = np.int64(len(model.layers)) # number of all defined layers in keras
        ni = model.get_input_shape_at(0)
        ni = np.int64(ni[1])
        no = model.get_output_shape_at(0)
        no = np.int64(no[1])
        return nl,ni,no
    #[nl,ni,no] = get_shape(model)
    
    def get_layers(self, model,nl):
        config = model.get_config()
        if type(config)==list:
            lys = [] #list of types of layers in the network
            for i in range(0,nl):
                if 'class_name' in config[i]:
                    lys.append(config[i]['class_name']) 
            lfs = [] #list of activation functions
            for i in range(0,nl):
                if 'activation' in config[i]['config']:
                    lfs.append(config[i]['config']['activation'])
        if type(config)==dict:
            l = config['layers']
            lys = []
            for i in range(0,nl):
                if 'class_name' in l[i]:
                    lys.append(l[i]['class_name'])
            lfs = []
            for i in range(0,nl):
                if 'activation' in l[i]['config']:
                    lfs.append(l[i]['config']['activation'])
        return(lys,lfs)
    #[lys,lfs] = get_layers(model,nl)   
        
    # Load the size of individual layers and total neurons
    def get_neurons(self,model,nl):
        config = model.get_config()
        if type(config)==dict:
            l = config['layers'] #get the list of layers
            lsize=[]
            for i in range(0,nl):
                if 'units' in l[i]['config']:
                    lsize.append(l[i]['config']['units']) # size of each layer
                    n = np.int64(sum(lsize)) #total number of neurons in NN
        elif type(config)==list:
            lsize=[]
            for i in range(0,nl):
                if 'units' in config[i]['config']:
                    lsize.append(config[i]['config']['units'])
                    n = np.int64(sum(lsize))
        nls = np.int64(len(lsize)) #true number of layers 
        return lsize,n,nls
    #[lsize,n,nls] = get_neurons(model,nl)
    
    # Load the weights and biases
    #def get_w_and_b(model,nls):
    #    w = model.get_weights()
    #    W=[]
    #    for i in range(0,int(nls)): #-2 due to the special case of concatenating last 3 defined layers
    #        W.append(w[2*i])
    #    b=[]
    #    for i in range(0,int(nls)): #-2 due to the special case of concatenating last 3 defined layers
    #        b.append(w[2*i+1])
    #    return W,b
    #[W,b] = get_w_and_b(model,nls)
    
    def get_parameters(self, model,nl,nls):
        [lys,lfs] = get_layers(model,nl)
        w = model.get_weights()
        W = [] #matrix of weights
        b = [] #matrix of biases
        i=0
        j=0
        while (i < nl) and (j < nls+1):
    #        while j < nls:
            if lys[i]=='Activation':
                W.append(0)
                b.append(0)
                i = i+1
            elif lys[i]=='Dense':
                W.append(np.float64(w[2*j].T))
                b.append(np.float64(w[2*j+1].T))
                j = j+1
                i = i+1
            else:
                i = i+1 
        return W,b
    #[W,b] = get_parameters(model,nl,nls)
        
    # Save the nn information in a mat file
    def save_nnmat_file(self, model,ni,no,nls,n,lsize,W,b,lys,lfs):
        nn1 = dict({'number_of_inputs':ni,'number_of_outputs':no ,'number_of_layers':nls,
                    'number_of_neurons':n,'layer_sizes':lsize,'W':W,'b':b,'types_of_layers':lys,'activation_fcns':lfs})
        sio.savemat(savefile, mdict={nn:nn1})
    #save_nnmat_file(model)
    
    # parse the nn imported from keras as json and h5 files
    def parse_nn(self, modelfile,weightsfile):
        model = load_files(modelfile,weightsfile)
        [nl,ni,no] = get_shape(model)
        [lys,lfs] = get_layers(model,nl)
        [lsize,n,nls] = get_neurons(model,nl)
        [W,b] = get_parameters(model,nl,nls)
        save_nnmat_file(model,ni,no,nls,n,lsize,W,b,lys,lfs)
        
    def parse_nn_wout_json(self, modelfile):
        model = models.load_model(modelfile)
        [nl,ni,no] = get_shape(model)
        [lys,lfs] = get_layers(model,nl)
        [lsize,n,nls] = get_neurons(model,nl)
        [W,b] = get_parameters(model,nl,nls)
        save_nnmat_file(model,ni,no,nls,n,lsize,W,b,lys,lfs)