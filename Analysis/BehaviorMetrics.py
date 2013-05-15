# -*- coding: utf-8 -*-
"""
Created on Wed May 08 11:02:28 2013

@author: saskiad
"""

from pylab import *
import scipy as sp
import numpy as np
import os

def BehaviorMetrics(logpath):
    '''pulls out simple behavior metrics from a single run, creates/saves a figure with plots and metrics'''
    '''assumes all parameters have relevance = True'''
    '''also assume if false, only one parameter is false'''
    f = open(logpath, 'r')
    exec(f.read())
    f.close()
    
    '''terrain parameters'''
    numparams = 0
    correcttup = []
    for i in range(len(terrain['params'])):
        if terrain['params'][i]['relevance']:
            iname = 'param' + str(i) + 'name'
            icorrect = 'param' + str(i) + 'correct'
            ifalse = 'param' + str(i) + 'false'
            vars()[iname] = terrain['params'][i]['name']
            vars()[icorrect] = terrain['params'][i]['correct']
            vars()[ifalse] = 0
            numparams += 1
            correcttup = correcttup + vars()[icorrect]
            print iname, vars()[iname]
            print icorrect, vars()[icorrect] 
    
    '''correct & incorrect trials'''
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
    
    '''correct rewards'''
    numberrewards = len(rewards)    
    percentcorrect =  (numberrewards/float(expectedrewards)) * 100
    totalwater = numberrewards * 0.005
    
    rewardsframe = np.empty((len(rewards),1))
    for i in range(len(rewards)):
        rewardsframe[i] = rewards[i][1]
    rewardsy = range(len(rewardsframe))
    
    '''false positives & which parameter is false'''
    falsepositive = 0    
    lap = laps
    lap.insert(0, [0.0, 0])
    for i in range(expectedincorrect):
        frameswindow = 0
        lapi = int(incorrecttrials[i])
        lapframes = range(lap[lapi][1], lap[lapi+1][1])
        for ti in lapframes:
            if (-1 * terrain['windowwidth']/2) < posx[ti] <= (terrain['windowwidth']/2):
                frameswindow += 1
        test = []
        if frameswindow >= terrain['selectiontime']:
            falsepositive += 1 
            test = [(j == k) for j, k in zip(terrainlog[lapi], correcttup)]
            for ip in range(numparams):
                ifalse = 'param' + str(ip) + 'false'
                if test[ip] == False:
                    vars()[ifalse] += 1

    percentfp = round((falsepositive/float(expectedincorrect)) * 100,3)
    
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
    suptitle(mouseid, fontsize=14)
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
    for i in range(numparams):
        iname = 'param' + str(i) + 'name'
        ifalse = 'param' + str(i) + 'false'
        figtext(0.7, (0.1+(i*0.05)), "False" + vars()[iname])
        figtext(0.85, (0.1+(i*0.05)), vars()[ifalse])

    fname = mouseid +'.png'
    fullfilename = os.path.join(savepath, fname)
    savefig(fullfilename)    
    show()
    return
    
if __name__=='__main__':
    logpath = r'C:\Users\saskiad\Documents\130502161139-S32T2.log'    
    savepath = r'C:\Users\saskiad\Documents\test'    
    BehaviorMetrics(logpath)