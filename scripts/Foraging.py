"""Runs a Foraging experiment"""

from dimstim.Core import StaticParams
from dimstim.Constants import dc # dimstim config
from aibs.ManBar_Foraging import ManBar
from aibs.Terrain import Terrain
from aibs.Reward import Reward
from aibs.Encoder import Encoder

p = StaticParams()

# Foraging experiment parameters, all must be scalars

# Mouse ID
p.mouseid = 'test'
# background brightness (0-1)
p.bgbrightness = 0.5
# antialiase the bar?
p.antialiase = True
# screen gamma: None, or single value, or 3-tuple
p.gamma = dc.get('Screen', 'gamma')
# flash the stimulus?
p.flash = False
# duration of each flash cycle (on and off) (sec)
p.flashSec = 1
# starting y position
p.ypos = 540 #540 is center on 1080 pixel wide monitor
# print vsync histogram?
p.printhistogram = False
# display on how many screens?
p.nscreens = 2
# set up wheel encoder (NIDAQ Device, Vin, Vsig)
p.encoder = Encoder(1,1,2)
# set up terrain? [possible orientations], correct orientation]
p.terrain = Terrain(['color','orientation'])
# define terrain parameters
p.terrain.oriarray = [0,45]
p.terrain.oricorrect = 0
p.terrain.color = p.terrain.white #initial color state
p.terrain.correctfreq = 1 #(0-1)
p.terrain.orientation = 45 # starting orientation
p.terrain.lapdistance = 1920 # distance in pixels between stimuli (should be wider than screen)
p.terrain.windowwidth = 200 # size in pixels of "correct" region
p.terrain.selectiontime = 30 # in frames 
p.terrain.speedgain = 5 # pixels/degree
p.terrain.colorrandom = True #randomize the stimulus color
p.terrain.colormatters = True #does the correct color matter
p.terrain.colorcorrect = p.terrain.black #what is the correct color
p.terrain.objectwidthDeg = 25 #width of the object in degrees
#set up reward (NIDAQ device, port for DO, lines, rewardline)
p.reward = Reward(1,1,4,0)
#define reward paramters
p.reward.rewardtime = 0.03


e = ManBar(script=__file__, # this script's file name
           params=p) # create a ManBar experiment
e.run() # run it
