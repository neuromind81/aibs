from aibs.SweepStim import SweepStim
from psychopy import visual, core, event, logging, misc, monitors
import itertools
import scipy
import os
import Image

"""
This is a sample script that sets up a basic image sequence experiment.  This should be performed by the GUI eventually.

Notes: Drops frames when switching images.  Working on a solution to this.

"""


#GENERIC PARAMETERS (should be passed by GUI, some of which have been read from config file)
params = {}
params['runs'] = 100 #number of runs
params['shuffle'] = False #shuffle sweep tables
params['preexpsec'] = 2 #seconds at the start of the experiment
params['postexpsec'] = 2 #seconds at the end of the experiment
params['sweeplength'] = 0.018 #length of sweeps
params['postsweepsec'] = 0 #black period after sweeps (foreground remains)
params['logdir'] = "C:\\ExperimentLogs\\" #where to put the log
params['backupdir'] = "" #backup to network
params['mousename'] = "Spock" #name of the mouse
params['userid'] = "derricw" #name of the user
params['task'] = "" #task type
params['stage'] = "idkwhatthismeans" #stage
params['protocol'] = "" #implemented later
params['nidevice']='Dev1' #NI device name
params['blanksweeps']=0 #blank sweep every x sweeps
params['bgcolor']='gray' #background color
params['syncsqr']=True #display a flashing square for synchronization
params['syncsqrloc']=(-600,-350)


#SET CONSOLE OUTPUT LEVEL, INITIALIZE WINDOWS
#logging.console.setLevel(logging.DEBUG) #uncommet for diagnostics
window = visual.Window(units='norm',monitor='testMonitor', fullscr = True, screen = 0, waitBlanking=False)
window.setColor(params['bgcolor'])

#CREATE BACKGROUND STIMULUS

stim = visual.ImageStim(window, size = (2.0,2.0))

path = r"C:\Users\derricw\Pictures\tifseq"

imagefiles = [os.path.join(path,f) for f in os.listdir(path) if len(f) > 4 and f[-4:] in ['.jpg','.png','.tif']]
print imagefiles
images = [Image.open(f) for f in imagefiles]

       
#CREATE BACKGROUND FRAME PARAMETERS (what changes between frames and how much)
bgFrame = {}

#CREATE BACKGROUND SWEEP PARAMETERS (what changes between sweeps, and in what order)
bgSweep = {}


bgSweep['Image'] = (images,0) #each texture we just generated

#CREATE FOREGROUND STIMULUS (none for basic white noise experiment)


#CREATE FOREGROUND STIMULUS FRAME PARAMETERS (what changes between frames and how much)
fgFrame = {}

#CREATE FOREGROUND SWEEP PARAMETERS (what changes between sweeps)
fgSweep = {}

#CREATE FORAGING CLASS INSTANCE
g = SweepStim(window = window, params = params, bgStim = stim, bgFrame = bgFrame, bgSweep = bgSweep, fgStim = None)
#RUN IT
g.run()