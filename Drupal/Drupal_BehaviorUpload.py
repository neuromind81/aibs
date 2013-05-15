from pylab import *
import numpy
import math
import scipy.io as sio
import os, datetime
from config import config
from drupal_services import DrupalServices
import sys, time, mimetypes, xmlrpclib, pprint, base64
from aibs.Analysis.StimulusTools import StimulusMatFile

def uploadlog(path, contentType):
    """
    Uploads information from a behavior log to server.
        path is log path.
        contentType is which tab.
    """
    drupal = DrupalServices(config)

    rel = getBehaviorInfo(path)

    ''' EXAMPLE
    new_node = { 'language' : 'und',
                 'type': contentType,
                 'title': datasetname,
                 'field_clearing' : {'und' : { '0' : {'value': cleared}}},
                 'field_test_data' : { 'und' : { '0' : {'value' : testdata } }},
                 'field_id' : { 'und' : { '0' : {'value' : Id } }},
                 'field_date_headpost' : { 'und' : { '0' : {'value' : headpost } }},
                 'body': { 'und' : { '0' : {'value' : datasetname } }} ,
    }
    '''
    #CREATE A NEW NODE OBJECT OF KEY-VALUE PAIRS
    new_node = { 'language' : 'und',
                 'type': contentType,
                 'title': rel["logname"],
                 'field_id' : { 'und' : { '0' : { 'value' : rel['mouseid']}}},
                 'field_logpath' : { 'und' : { '0' : { 'value' : rel['logpath']}}},
                 'field_traveldistance' : { 'und' : { '0' : { 'value' : round(rel['traveldistance'],3)}}},
                 'field_rewardsperminute' : { 'und' : { '0' : { 'value' : round(rel['rewardsperminute'],3)}}},
                 'field_correctpercent' : { 'und' : { '0' : { 'value' : rel['correctpercent']}}},
                 'field_protocol' : { 'und' : { '0' : { 'value' : rel['protocol']}}},
    }

    #PUSH NODE
    node = drupal.call('node.create', new_node)

    print 'New node id: %s' % node['nid']

    #RECALL NODE
    created_node = drupal.call('node.retrieve', int(node['nid']))

    #PRINT INFORMATION
    print "Node information"
    print "Node title: %s " % (created_node['title'])
    #print "Node body: %s " % (created_node['body']['und'][0]['value'])

def getBehaviorInfo(path):

  matfile = StimulusMatFile(path)

  relevant["rewardsperminute"] = matfile.getRewardsPerMinute()
  relevant["traveldistance"] = matfile.getDistanceTraveled()
  relevant["correctpercent"] = matfile.getCorrectPercent()
  relevant["logpath"] = path
  relevant["logname"] = str(matfile.filename)
  relevant["protocol"] = str(matfile.protocol)
  relevant["data"] = None #get from file later
  relevant["mouseid"] = str(matfile.mouseid[0])

  print relevant
  return relevant



if __name__ == "__main__":

    logdir = r"\\aibsdata\neuralcoding\Neural Coding\Behavior"
    files = os.listdir(logdir)
    for f in files:
      name,ext = os.path.splitext(f)
      if ext in ".mat":
        path = os.path.join(logdir,f)


    #uploadlog(path,'behavior')