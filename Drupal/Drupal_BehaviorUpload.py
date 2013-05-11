from pylab import *
import numpy
import math
import os.path, datetime
from config import config
from drupal_services import DrupalServices
import sys, time, mimetypes, xmlrpclib, pprint, base64

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

  info = {}
  relevant = {}
  f = open(path)
  for line in f.readlines():
    param = line.split(" = ")
    if not "#" in line:
      try:
        info[param[0]] = eval(param[1])
        exec(line)
      except:
        info[param[0]] = param[1]
  for k,v in info.iteritems():
    pass

  totalseconds = (stoptime-starttime).total_seconds()
  totalminutes = totalseconds/60.0
  relevant["rewardsperminute"] = len(rewards)/totalminutes
  relevant["traveldistance"] = sum(dx)/360*(2*numpy.pi*1.5)/12
  relevant["correctpercent"] = round(float(len(rewards))/float((len(terrainlog))-1)*100.000,3)
  relevant["logpath"] = r"Y:\Behavior\CA153\130119173855-sweep.log" #get from file later
  relevant["logname"] = "130119173855-sweep.log" #get from file later
  relevant["protocol"] = "Virtual Foraging" #get from file later
  relevant["data"] = None #get from file later
  relevant["mouseid"] = "CA153" #need to fix log parsing to get this from file

  print relevant
  return relevant



if __name__ == "__main__":
    import os

    logdir = r"C:\Users\derricw\Documents\PythonProjects"
    filename = "130119173855-sweep.log"
    path = os.path.join(logdir,filename)

    uploadlog(path,'behavior')