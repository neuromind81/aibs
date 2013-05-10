
def deletenode(nodeid):
    from config import config
    from drupal_services import DrupalServices

    
    drupal = DrupalServices(config)

    print 'Attempting to delete nodeid: %s' % nodeid
    
    drupal.call('node.delete', int(nodeid))

    print "Node %s deleted." % nodeid

if __name__ == "__main__":
	node = 1265
    deletenode(node)
