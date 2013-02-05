"""Runs a SparseNoise experiment"""

from dimstim.Constants import dc # dimstim config
from dimstim.Core import StaticParams, DynamicParams, Variable, Variables, Runs, BlankSweeps
from aibs.SparseNoise_AIBS import SparseNoise

s = StaticParams()
d = DynamicParams()

"""Static parameters always remain constant during the entire experiment"""
# experiment id (for logging)
s.expid = "TEST"
# screen distance # cm
s.distance = 11
# pre-experiment duration to display blank screen (sec)
s.preexpSec = 1
# post-experiment duration to display blank screen (sec)
s.postexpSec = 1
# grid orientation offset (deg)
s.orioff = 0 #dc.get('Manbar0', 'orioff')
# grid width (number of cells)
s.ncellswide = 10
# grid height (number of cells)
s.ncellshigh = 10
# grid width (deg)
s.widthDeg = 40#s.ncellswide * 5 #dc.get('Manbar0', 'widthDeg')
# grid height (deg)
s.heightDeg = 20#s.ncellshigh * 5 #dc.get('Manbar0', 'heightDeg')
# screen gamma: None, or single value, or 3-tuple
s.gamma = None #dc.get('Screen', 'gamma')
# sync square (for frame sync)
s.syncsq = True
# sync sqaure location
s.syncsqloc = (100,100)

"""Dynamic parameters can potentially vary from one sweep to the next. If a dynamic parameter is assigned multiple values in a sequence, it's treated as a Variable, and has to be added to this Experiment's Variables object"""

# index of cell horizontal position (origin at left)
d.xi = range(s.ncellswide)
# index of cell vertical position (origin at bottom)
d.yi = range(s.ncellshigh)
# grid orientation relative to orioff (deg)
d.ori = 0
# grid x position relative to origin (deg)
d.xposDeg = 0
# grid y position relative to origin (deg)
d.yposDeg = 0
# bar brightness (0-1)
d.brightness = [0, 1]
# background brightness (0-1)
d.bgbrightness = 0.5
# antialiase the bar?
d.antialiase = True
# sweep duration (sec)
d.sweepSec = 0.25
# post-sweep duration to display blank screen (sec)
d.postsweepSec = 0
# contrast reverse
d.contrastreverse = False
# contrast reverse Frequency
d.cfreqCycSec = 0.5

vs = Variables()
#vs.xposDeg = Variable(vals=d.xposDeg, dim=-1, shuffle=False) # kwargs: vals, dim, shuffle, random
#vs.ori = Variable(vals=d.ori, dim=-1, shuffle=False)
vs.xi = Variable(vals=d.xi, dim=0, shuffle=True) # kwargs: vals, dim, shuffle, random
vs.yi = Variable(vals=d.yi, dim=1, shuffle=True)
vs.brightness = Variable(vals=d.brightness, dim=2, shuffle=True)

runs = Runs(n=10, reshuffle=True)

#bs = BlankSweeps(T=7, sec=2, shuffle=False) # blank sweep every T sweeps for sec seconds

e = SparseNoise(script=__file__, # this script's file name
                static=s, dynamic=d, variables=vs,
                runs=runs, blanksweeps=None) # create a SparseNoise experiment
e.run() # run it
