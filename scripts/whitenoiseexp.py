from aibs.SweepStim import SweepStim
from psychopy import visual, core, event, logging, misc, monitors
import itertools
import scipy

"""
This is a sample script that sets up a basic white noise experiment.  This should be performed by the GUI eventually.
"""


#GENERIC PARAMETERS (should be passed by GUI, some of which have been read from config file)
params = {}
params['runs'] = 1 #number of runs
params['shuffle'] = True #shuffle sweep tables
params['preexpsec'] = 2 #seconds at the start of the experiment
params['postexpsec'] = 2 #seconds at the end of the experiment
params['sweeplength'] = 2/60.00 #length of sweeps
params['postsweepsec'] = 0 #black period after sweeps (foreground remains)
params['logdir'] = "C:\\ExperimentLogs\\" #where to put the log
params['backupdir'] = None #backup to network
params['mouseid'] = "Spock" #name of the mouse
params['userid'] = "derricw" #name of the user
params['task'] = "" #task type
params['stage'] = "idkwhatthismeans" #stage
params['protocol'] = "" #implemented later
params['nidevice']='Dev1' #NI device name
params['blanksweeps']=0 #blank sweep every x sweeps
params['bgcolor']='gray' #background color
params['syncsqr']=True #display a flashing square for synchronization
params['syncsqrloc']=(-600,-350)
params['script']=__file__


#SET CONSOLE OUTPUT LEVEL, INITIALIZE WINDOWS
#logging.console.setLevel(logging.DEBUG) #uncommet for diagnostics
window = visual.Window(units='norm',monitor='testMonitor', fullscr = True, screen = 0, waitBlanking=False)
window.setColor(params['bgcolor'])

#CREATE BACKGROUND STIMULUS

noise = visual.GratingStim(window,tex=None,mask="None",texRes=64,
       size=[1280,1024], ori = 0, pos = (0,0), name='box', autoLog=False, units = 'pix')    
       
#CREATE BACKGROUND FRAME PARAMETERS (what changes between frames and how much)
bgFrame = {}

#CREATE BACKGROUND SWEEP PARAMETERS (what changes between sweeps, and in what order)
bgSweep = {}

noisematrix = [(scipy.random.randint(2,size = (64,64))*2-1) for x in range(100)]

bgSweep['Tex'] = (noisematrix,0) #each texture we just generated

#CREATE FOREGROUND STIMULUS (none for basic white noise experiment)


#CREATE FOREGROUND STIMULUS FRAME PARAMETERS (what changes between frames and how much)
fgFrame = {}

#CREATE FOREGROUND SWEEP PARAMETERS (what changes between sweeps)
fgSweep = {}

#CREATE FORAGING CLASS INSTANCE
g = SweepStim(window = window, params = params, bgStim = noise, bgFrame = bgFrame, bgSweep = bgSweep, fgStim = None)
#RUN IT
g.run()