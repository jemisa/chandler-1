
__revision__  = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2002 Open Source Applications Foundation"
__license__   = "http://osafoundation.org/Chandler_0.1_license_terms.htm"


from model.item.Item import Item
from model.item.ItemRef import RefDict
from model.util.Path import Path


class Kind(Item):

    def __init__(self, name, parent, kind):

        super(Kind, self).__init__(name, parent, kind)

        # recursion avoidance
        self._values['notFoundAttributes'] = []
        refDict = self._refDict('inheritedAttributes',
                                'inheritingKinds', False)
        self._references['inheritedAttributes'] = refDict

    def _fillItem(self, name, parent, kind, **kwds):

        super(Kind, self)._fillItem(name, parent, kind, **kwds)

        # recursion avoidance
        self._values['notFoundAttributes'] = []
        refDict = self._refDict('inheritedAttributes',
                                'inheritingKinds', False)
        self._references['inheritedAttributes'] = refDict

    def newItem(self, name, parent):
        """Create an item of this kind.

        The python class instantiated is taken from the Kind's classes
        attribute if it is set. The Item class is used otherwise."""
        
        return self.getItemClass()(name, parent, self)

    def newKind(self, name, parent, superKind=None):
        """Create a new kind, programmatically.

        The superKind of the kind created defaults to the Item kind at
        //Schema/Core/Item."""

        if superKind is None:
            superKind = self._kind.getItemParent().getItemChild('Item')
        
        kind = Kind(name, parent, self.kind)
        kind.addValue('superKinds', superKind)

        return kind

    def getItemClass(self):
        """Return the class used to create items of this Kind.

        By default, the Item class is returned."""

        return self.getAttributeValue('classes').get('python', Item)

    def resolve(self, name):

        child = self.getItemChild(name)
        if child:
            return child.getUUID()
        
        if self.hasAttributeValue('attributes', _attrDict=self._references):
            return self.attributes.resolveAlias(name)

        return None

    def getAttribute(self, name):

        uuid = self.resolve(name)
        if uuid is not None:
            attribute = self.getValue('attributes', uuid,
                                      _attrDict=self._references)
        else:
            attribute = None
            
        if attribute is None:
            uuid = self.inheritedAttributes.resolveAlias(name)
            if uuid is not None:
                attribute = self.getValue('inheritedAttributes', uuid,
                                          _attrDict=self._references)
            else:
                attribute = self.inheritAttribute(name)

        return attribute

    def hasAttribute(self, name):

        uuid = self.resolve(name)
        if uuid is not None:
            if self.hasValue('attributes', uuid, _attrDict=self._references):
                return True
        elif self.inheritedAttributes.resolveAlias(name):
            return True
        else:
            return self.inheritAttribute(name) is not None

    def inheritAttribute(self, name):

        if self.hasValue('notFoundAttributes', name):
            return None
        
        inheritingKinds = self._getInheritingKinds()
        if inheritingKinds is not None:
            cache = True
            for inheritingKind in inheritingKinds:
                if inheritingKind is not None:
                    attribute = inheritingKind.getAttribute(name)
                    if attribute is not None:
                        self.addValue('inheritedAttributes', attribute,
                                      alias=name)
                        return attribute
                else:
                    cache = False
                    
            if cache:
                self.addValue('notFoundAttributes', name)

        return None

    def _getInheritingKinds(self):

        if self.hasAttributeValue('superKinds'):
            return self.superKinds

        raise ValueError, 'No superKind for %s' %(self.getItemPath())

    def _xmlRefs(self, generator, withSchema, mode):

        for attr in self._references.items():
            if self.getAttributeAspect(attr[0], 'persist', default=True):
                attr[1]._xmlValue(attr[0], self, generator, withSchema, mode)

    def isAlias(self):
        return False

    def recognizes(self, value):
        raise NotImplementedError, "Kind.recognizes()"


class ItemKind(Kind):

    def _getInheritingKinds(self):

        return None


class SchemaRoot(Item):
    pass
