# -*- coding: utf-8 -*-



"""MAKING A MAT FILE """

import scipy.io as sio

#create empty dictionary, this will contain all data you want to write to mat file
data = {}

#some data we want to save to .mat file
somestuff = range(100)

#add stuff to dictionary. give it whatever name you want
data['nameofstuff'] = somestuff

#save the mat file
sio.savemat('filename.mat',data)
