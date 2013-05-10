from config import config
from drupal_services import DrupalServices
import os.path, sys, xlrd,  time, mimetypes, xmlrpclib, pprint, base64
import unicodedata


drupal = DrupalServices(config)

book = xlrd.open_workbook("c:/MICE_LOG_AC_and_SD.xls")
sh = book.sheet_by_index(1)
rows=sh.nrows 
cols=sh.ncols

m=sh.cell_value(rowx=2, colx=0)
m=unicodedata.normalize('NFKD', m).encode('ascii','ignore')
datasetname = m;
#datasetname = 'Sys2_10January2013_1656_';




#datasetname = 'Sys2_10January2013_1656_'
localpath = 'C:\\' 
filename = 'CI109'
fileext = '.png'
localname = localpath + filename + fileext
remotename = filename + fileext

os.chdir(localpath)

# Create a language-neutral node, use the string 'und' to infer language-neutral node
# other languages, use other language strings

pp = pprint.PrettyPrinter()
## Load a movie file - get size, mimetype

filesize = os.stat(localname).st_size
filemime = mimetypes.guess_type(localname)
fd = open(localname, 'rb')
png_file = fd.read()
fd.close()

timestamp = str(int(time.time()))
# Create file_obj with encoded file data
file_obj = {
   'file': base64.b64encode(png_file),
    'filename': remotename,
    'filepath': 'public://' + remotename,
    #'filepath': 'sites/default/files/' + filename,
    #'filepath': filename,
    'filesize': filesize,
    'timestamp': timestamp,
  #'uid': user['uid'],
    'filemime': filemime,
}

f = drupal.call('file.create', file_obj)

imagefile = {'und': [{
    'status': '1',
     'filemime': 'image/png',
     'rdf_mapping': [],
     'uid': '4',
     'title': '',
     'timestamp': '1358411015',
     'uri': 'public://'+remotename,
     'fid': f['fid'],
     'alt': '',
     'filename': remotename
 }]}



new_node = { 'type': 'animal',
             'title': datasetname,
             'field_cover_image': imagefile,
             'language' : 'und',
#             'field_cage' : '',
#             'field_strain' : ['bla'],
#             'field_id' : 'bla',
#             'field_headpost_date' : 'bla',
#             'language' : 'und',
#             'field_id' : '', #sh.cell_value(rowx=2, colx=2),
#             'field_strain' : '', #sh.cell_value(rowx=2, colx=3),
#              'field_sex' : '', #sh.cell_value(rowx=2, colx=4),
#              'field_dob' : '', #sh.cell_value(rowx=2, colx=5),
#              'field_date_headpost' : '', #sh.cell_value(rowx=2, colx=7),
#              'field_craniotomy_location' : '', # sh.cell_value(rowx=2, colx=8),
#              'field_date_craniotomy' : '', #sh.cell_value(rowx=2, colx=9),
#              'field_surgeon': '', #sh.cell_value(rowx=2, colx=10),
#              'field_date_injection' : '', #sh.cell_value(rowx=2, colx=12),
#              'field_injection' : '', #sh.cell_value(rowx=2, colx=13),
#              'field_injection_amount' : '', #sh.cell_value(rowx=2, colx=14),
#              'field_injection_surgeon' : '', #sh.cell_value(rowx=2, colx=15),
#              'field_sac_d' : '', #sh.cell_value(rowx=2, colx=16),
#              'field_sac_comment' : '', #sh.cell_value(rowx=2, colx=17),
##              'body': { 'und' : { '0' : {'value' : datasetname } }} ,
}

node = drupal.call('node.create', new_node)
   
print 'New node id: %s' % node['nid'] 

created_node = drupal.call('node.retrieve', int(node['nid']))

drupal.call('node.update')

m=created_node (['field_cage'])

drupal.call('node.update', m)

print "Node information"
print "Node cage: %s " % m
#print "Node body: %s " % (created_node['body']['und'][0]['value'])
