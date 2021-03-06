# -*- coding: utf-8 -*-
"""
Created on Wed May 08 11:02:28 2013

@author: saskiad
"""

from pylab import *
import scipy as sp
import numpy as np
import os, sys

def BehaviorMetrics(logpath):
    '''pulls out simple behavior metrics from a single run, creates/saves a figure with plots and metrics'''
    '''currently only cares about color, not orientation'''
    f = open(logpath, 'r')
    exec(f.read())
    f.close()
    
    '''terrain parameters'''
    numparams = 0
    for i in range(len(terrain['params'])):
        if terrain['params'][i]['relevance']:
            iname = 'param' + str(i) + 'name'
            icorrect = 'param' + str(i) + 'correct'
            vars()[iname] = terrain['params'][i]['name']
            vars()[icorrect] = terrain['params'][i]['correct']

            numparams += 1
            print iname, vars()[iname]
            print icorrect, vars()[icorrect]

    '''terrainlog parameters'''
    correcttup = []
    for i in range(numparams):
        icorrect = 'param' + str(i) + 'correct'
        correcttup = correcttup + vars()[icorrect]
    
    expectedrewards = 0
    expectedincorrect = 0
    correcttrials = []
    incorrecttrials = []
    for i in range(len(terrainlog)):
        if terrainlog[i] == correcttup:
            expectedrewards += 1
            correcttrials = append(correcttrials, i)
        else:
            expectedincorrect += 1
            incorrecttrials = append(incorrecttrials, i)
    print expectedrewards
    print expectedincorrect
    print incorrecttrials
    sys.exit()
    
    '''correct'''
    numberrewards = len(rewards)    
    percentcorrect =  (numberrewards/expectedrewards) * 100
    totalwater = numberrewards * 0.005
    
    rewardsframe = np.empty((len(rewards),1))
    for i in range(len(rewards)):
        rewardsframe[i] = rewards[i][1]
    rewardsy = range(len(rewardsframe))
    
    '''false positives'''
    falsepositive = 0
    temp = np.where(terraincolor != colorcorrect)    
    incorrecttrials = temp[0][:]
    expectedincorrect = len(incorrecttrials)
    
    for i in range(expectedincorrect):
        frameswindow = 0
        lapframes = range(laps[i-1][1], laps[i][1])
        for ti in lapframes:
            if (-1 * terrain['windowwidth']/2) < posx[ti] <= (terrain['windowwidth']/2):
                frameswindow += 1
        if frameswindow >= terrain['selectiontime']:
            falsepositive += 1
    percentfp = (falsepositive/float(expectedincorrect)) * 100
    
    '''distance run'''
    distance = []
    y = 0.0
    for i in dx:
        y += i
        distance.append(y)
    distance = array(distance) 
    distancecm = (distance/360) * 10.16 *pi
    totaldistance = int(distancecm[len(distancecm)-1])
    '''assuming mouse at 2/3 of 3" radius wheel'''
    
    '''make figure'''
    figure()
    subplot(2,2,1)
    plot(rewardsframe, rewardsy, '.')
    ylabel("Reward Number", fontsize=12)
    xlabel("Stimulus Frame", fontsize=12)
    subplot(2,2,2)
    plot(distancecm)
    ylabel("Distance (cm)", fontsize=12)
    xlabel("Stimulus Frame", fontsize=12)
    tight_layout()
    subplots_adjust(top=0.9)
    suptitle(mousename, fontsize=14)
    figtext(0.2, 0.05, startdatetime)
    figtext(0.2, 0.15, "number of false positives:")
    figtext(0.5, 0.15, str(falsepositive))
    figtext(0.2, 0.1, "percent of incorrect trials:")
    figtext(0.5, 0.1, str(percentfp))
    figtext(0.2, 0.25, "number of rewards:")
    figtext(0.5, 0.25, str(numberrewards))
    figtext(0.2, 0.2, "percent of correct rewards:")
    figtext(0.5, 0.2, str(percentcorrect))
    figtext(0.2, 0.35, "total distance run (cm):")
    figtext(0.5, 0.35, totaldistance)
    figtext(0.2, 0.3, "total water (mL):")
    figtext(0.5, 0.3, totalwater)
    
    fname = mousename +'.png'
    fullfilename = os.path.join(savepath, fname)
    savefig(fullfilename)    
    show()
    return
    
if __name__=='__main__':
    logpath = r'C:\Users\saskiad\Documents\130502161139-S32T2.log'    
    savepath = r'C:\Users\saskiad\Documents\test'    
    BehaviorMetrics(logpath)