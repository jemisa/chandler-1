#!bin/env python

"""Model object for PersonItems in Chandler
"""

__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2002 Open Source Applications Foundation"
__license__ = "OSAF"

from persistence.dict import PersistentDict

from RdfRestriction import RdfRestriction
from RdfNamespace import chandler

from EntityItem import EntityItem
from PersonName import PersonName

class PersonItem(EntityItem):

    rdfs = PersistentDict()

    rdfs[chandler.name] = RdfRestriction(PersonName, 1)

    def __init__(self):
        EntityItem.__init__(self)




    
