# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 11:40:12 2013

@author: derricw
"""
from psychopy import visual,event
import os
import Image
import cProfile

def run(window,imagefiles,stim):
    for i in range(20): #run it 20 times
        for f in imagefiles:
            img = Image.open(f) #open image
            stim.setImage(img) #set image to texture
            stim.draw() #draw
            window.flip() #flip      
    window.close()
 

window = visual.Window(units='norm',monitor='testMonitor', fullscr = True, screen = 0, waitBlanking=False)
window.setColor('grey')

stim = visual.ImageStim(window, size = (2.0,2.0))

path = r"C:\Users\derricw\Pictures\sequence"

imagefiles = [os.path.join(path,f) for f in os.listdir(path) if len(f) > 4 and f[-4:] in ['.jpg','.png','.tif']]
print imagefiles
#images = [Image.open(f) for f in imagefiles]
window.setRecordFrameIntervals()

cProfile.run('run(window,imagefiles,stim)')