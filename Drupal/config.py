""" 
General settings for connecting to Drupal.  The key can be set by
visiting /admin/build/services/keys on your Drupal installation).

"""


config_local = {
  'url': 'http://localhost/services/xmlrpc',
  # 'key': '22222222222222222222222222222222', 
  # 'username': 'monkey',
  # 'password': 'test',
  # 'domain': 'localhost',
}


config_alpha = {
  'url': 'http://10.71.1.67/xmlrpc',
  # 'key': '33333333333333333333333333333333',
  'username': 'admin',
  'password': 'password',
}


config = config_alpha
