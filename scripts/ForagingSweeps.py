"""Runs a flashed Grating experiment"""

from dimstim.Constants import dc # dimstim config
from dimstim.Core import StaticParams, DynamicParams, Variable, Variables, Runs, BlankSweeps
from aibs.ForagingSweeps import ForagingSweeps
from aibs.Terrain import Terrain
from aibs.Encoder import Encoder
from aibs.Reward import Reward

s = StaticParams()
d = DynamicParams()

#===============================================================================
# Static parameters always remain constant during the entire experiment
#===============================================================================

# MOUSE ID
s.mouseid = 'test'
# pre-experiment duration to display blank screen (sec)
s.preexpSec = 1
# post-experiment duration to display blank screen (sec)
s.postexpSec = 1
# bar orientation offset (deg)
s.orioff = 0 #dc.get('Manbar0', 'orioff')
# grating width (deg)
s.widthDeg = 150 #dc.get('Manbar0', 'widthDeg')
# grating height (deg)
s.heightDeg = 120 #dc.get('Manbar0', 'heightDeg')
# mask, one of:  None, 'gaussian', or 'circle'
s.mask = None #'gaussian'
# screen gamma: None, or single value, or 3-tuple
s.gamma = None
# starting y position of terrain
s.ypos = 500
# set up wheel encoder (NIDAQ Device, Vin channel, Vsig channel)
s.encoder = Encoder('Dev1',1,2)

# set up terrain? [trainingtypes] for example ["color"]
s.terrain = Terrain(["color", "orientation"])
# define terrain parameters
s.terrain.color = s.terrain.white #(0-1) starting color
s.terrain.correctfreq = 1 #(0-1)
s.terrain.orientation = 45 # starting orientation
s.terrain.lapdistance = 1920 # distance in pixels between stimuli (should be wider than screen)
s.terrain.windowwidth = 200 # size in pixels of "correct" region
s.terrain.selectiontime = 30 # in frames 
s.terrain.speedgain = 4 # no units
s.terrain.colorrandom = True #randomize the stimulus color
s.terrain.colorcorrect = s.terrain.black #what is the correct color
s.terrain.objectwidthDeg = 20 #width of the object in degrees

#set up reward (NIDAQ device, port for Digital Out, number of lines, rewardline)
s.reward = Reward('Dev1',1,0)
#define reward paramters
s.reward.rewardtime = 0.04

#===============================================================================
# Dynamic parameters can potentially vary from one sweep to the next. If a dynamic parameter 
# is assigned multiple values in a sequence, it's treated as a Variable, and has to be added to 
# this Experiment's Variables object
#===============================================================================

# grating orientation relative to orioff (deg)
d.ori = range(0, 360, 45)
# grating x position relative to origin (deg)
d.xposDeg = 0
# grating y position relative to origin (deg)
d.yposDeg = 0
# mask diameter (deg), ignored if mask is None
d.diameterDeg = 10
# spatial frequency (cycles/deg)
d.sfreqCycDeg = [0.2,0.5,1]
# temporal frequency (cycles/sec)
d.tfreqCycSec = [1,2,3]
# grating phase to begin each sweep with (+/- deg)
d.phase0 = 0
# mean luminance (0-1)
d.ml = 0.5
# contrast (0-1), >> 1 get square grating, < 0 get contrast reversal
d.contrast = 1.5
# background brightness (0-1)
d.bgbrightness = 0.5
# sweep duration (sec)
d.sweepSec = 1
# post-sweep duration to display blank screen (sec)
d.postsweepSec = 2
# reverse the contrast?
d.contrastreverse = False
# contrast reverse freq?
d.cfreqCycSec = 2

#===============================================================================
# Variables determine the sweep table
#===============================================================================

vs = Variables()
vs.ori = Variable(vals=d.ori, dim=0, shuffle=False) # kwargs: vals, dim, shuffle, random
vs.sfreqCycDeg = Variable(vals=d.sfreqCycDeg, dim=1, shuffle=False)
#vs.phase0 = Variable(vals=d.phase0, dim=0, shuffle=False)
vs.tfreqCycSec = Variable(vals=d.tfreqCycSec, dim=2, shuffle=False)
#vs.contrast = Variable(vals=d.contrast, dim = 0, shuffle=False)
#vs.phase0 = Variable(vals=d.phase0, dim=0, shuffle = False)

#===============================================================================
# Run
#===============================================================================

runs = Runs(n=4, reshuffle=False)

bs = BlankSweeps(T=2000, sec=2, shuffle=False) # blank sweep every T sweeps for sec seconds

e = ForagingSweeps(script=__file__, # this script's file name
            static=s, dynamic=d, variables=vs,
            runs=runs, blanksweeps=bs) # create a Grating experiment
e.run() # run it
