"""
Unit tests literal attributes
"""

__revision__  = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2003 Open Source Applications Foundation"
__license__   = "http://osafoundation.org/Chandler_0.1_license_terms.htm"

import RepositoryTestCase, os, unittest


from repository.item.Item import Item
from repository.schema.Attribute import Attribute

class LiteralAttributesTest(RepositoryTestCase.RepositoryTestCase):
    """ Test Literal Attributes """

    def testLiteralAttributes(self):
        """Test basic features of literal attributes"""
        kind = self.rep.find('//Schema/Core/Kind')
        itemKind = self.rep.find('//Schema/Core/Item')
        self.assert_(itemKind is not None)

        item1 = Item('item1', self.rep, kind)
        self.assert_(item1 is not None)

        item2 = Item('item2', self.rep, itemKind)
        self.assert_(item2 is not None)

        #Test hasAttributeAspect and getAttributeAspect
        self.assert_(item1.hasAttributeAspect('attributes','cardinality') and
                     item1.getAttributeAspect('attributes','cardinality') == 'list')

        self.assert_(item1.hasAttributeAspect('superKinds','cardinality') and
                     item1.getAttributeAspect('superKinds','cardinality') == 'list')

        self.assert_(item1.hasAttributeAspect('classes','cardinality') and
                     item1.getAttributeAspect('classes','cardinality') == 'dict')

        self.assert_(item1.hasAttributeAspect('notFoundAttributes','persist') and
                     item1.getAttributeAspect('notFoundAttributes','persist') == False)

        # up to here displayName is an unset Chandler attribute
        self.failUnlessRaises(AttributeError, lambda x: item2.displayName, None)
        # now set the attribute
        item2.setAttributeValue('displayName','myName')
        self.assertEquals(item2.displayName,'myName')
        #test __getattr__ and getAttributeValue() access
        self.assertEquals(item2.displayName,item2.getAttributeValue('displayName'))
        # now remove attribute value
        item2.removeAttributeValue('displayName')
        self.failUnlessRaises(AttributeError, lambda x: item2.displayName, None)
        #TODO need a test for list valued literal attribute

        # test dict valued literal attribute
        self.assert_(kind.classes['python'] is not None)

    def testListMultis(self):
        """Test list valued literal attributes """

        def verifyItem(i):
            """verify that a list valued literal attribute has the right values"""
            # verify list length
            self.assertEquals(len(i.strings),4)
    
            # test to see that there is a key at every position
            self.assert_(i.hasKey('strings',0))
            self.assert_(i.hasKey('strings',1))
            self.assert_(i.hasKey('strings',2))
            self.assert_(i.hasKey('strings',3))
                                         
            # test to see that every value is in the attribute
            self.assert_(i.hasValue('strings','Goofy'))
            self.assert_(i.hasValue('strings','Donald'))
            self.assert_(i.hasValue('strings','Minnie'))
            self.assert_(i.hasValue('strings','Mickey'))
    
            # verify list contents using getValue() method
            self.assertEquals(i.getValue('strings',0),'Mickey')
            self.assertEquals(i.getValue('strings',1),'Minnie')
            self.assertEquals(i.getValue('strings',2),'Donald')
            self.assertEquals(i.getValue('strings',3),'Goofy')
    
            # verify list contents using python list notation
            self.assertEquals(i.strings[0],'Mickey')
            self.assertEquals(i.strings[1],'Minnie')
            self.assertEquals(i.strings[2],'Donald')
            self.assertEquals(i.strings[3],'Goofy')
            
        
        kind = self.rep.find('//Schema/Core/Kind')                
        itemKind = self.rep.find('//Schema/Core/Item')            
        myKind = kind.newItem('listKind', self.rep)
                                                                  
        # create an attribute with cardinality list and add to the kind
        attrKind = itemKind.getAttribute('kind').kind             
        multiAttribute = Attribute('strings', myKind, attrKind)   
        multiAttribute.setAttributeValue('cardinality','list')    
        myKind.addValue('attributes', multiAttribute)             
                                                                  
        # create an item of the new kind
        item = myKind.newItem('item', self.rep)                   

        # add to the list attribute
        item.setValue('strings','Mickey')                         
        item.addValue('strings','Minnie')                         
        item.addValue('strings','Donald')                         
        item.addValue('strings','Goofy')                          
        verifyItem(item)
        
        # now write what we've done and read it back
        self._reopenRepository()
        item = self.rep.find('//item')
        verifyItem(item)

        #test removeValue by removing values and checking
        #that value is removed and length has decreased
        item.removeValue('strings',0)
        self.failIf(item.hasValue('strings','Mickey'))
        self.assertEquals(len(item.strings),3)
        item.removeValue('strings',2)
        self.failIf(item.hasValue('strings','Goofy'))
        self.assertEquals(len(item.strings),2)
        item.removeValue('strings',1)
        self.failIf(item.hasValue('strings','Donald'))
        self.assertEquals(len(item.strings),1)
        item.removeValue('strings',0)
        self.failIf(item.hasValue('strings','Minnie'))
        self.assertEquals(len(item.strings),0)

        # now write what we've done and read it back
        self._reopenRepository()
        item = self.rep.find('//item')
        self.failIf(item.hasValue('strings','Mickey'))
        self.failIf(item.hasValue('strings','Goofy'))
        self.failIf(item.hasValue('strings','Donald'))
        self.failIf(item.hasValue('strings','Minnie'))
        self.assertEquals(len(item.strings),0)

    def testDictMultis(self):
        """Test dictionary valued literal attributes"""

        def verifyItem(i):
            """ verify that a dictionayr value literal attribute contains the right data"""
            self.assertEquals(len(i.strings),4)
    
            # test to see that all keys were inserted
            self.assert_(i.hasKey('strings','Mickey'))
            self.assert_(i.hasKey('strings','Minnie'))
            self.assert_(i.hasKey('strings','Donald'))
            self.assert_(i.hasKey('strings','Goofy'))
                                         
            # test to see that every value is in the attribute
            self.assert_(i.hasValue('strings','Mouse'))
            self.assert_(i.hasValue('strings','Mouse'))
            self.assert_(i.hasValue('strings','Duck'))
            self.assert_(i.hasValue('strings','Dog'))
    
            # verify dict contents using getValue() method
            self.assertEquals(i.getValue('strings','Mickey'),'Mouse')
            self.assertEquals(i.getValue('strings','Minnie'),'Mouse')
            self.assertEquals(i.getValue('strings','Donald'),'Duck')
            self.assertEquals(i.getValue('strings','Goofy'), 'Dog')
    
            # verify dict contents using python dict notation
            self.assertEquals(i.strings['Mickey'],'Mouse')
            self.assertEquals(i.strings['Minnie'],'Mouse')
            self.assertEquals(i.strings['Donald'],'Duck')
            self.assertEquals(i.strings['Goofy'], 'Dog')

        
        kind = self.rep.find('//Schema/Core/Kind')                
        itemKind = self.rep.find('//Schema/Core/Item')            
        myKind = kind.newItem('dictKind', self.rep)
                                                                  
        # create an attribute with cardinality dict and add to the kind
        attrKind = itemKind.getAttribute('kind').kind             
        multiAttribute = Attribute('strings', myKind, attrKind)   
        multiAttribute.setAttributeValue('cardinality','dict')    
        myKind.addValue('attributes', multiAttribute)             
                                                                  
        # create an item of the new kind
        item = myKind.newItem('item', self.rep)                   
        item.setValue('strings','Mouse','Mickey')                         
        item.addValue('strings','Mouse','Minnie')                         
        item.addValue('strings','Duck','Donald')                         
        item.addValue('strings','Dog','Goofy')                          
        verifyItem(item)
        
        # now write what we've done and read it back
        self._reopenRepository()
        item = self.rep.find('//item')
        verifyItem(item)

        #test removeValue by removing values and checking
        #that value is removed and length has decrease
        item.removeValue('strings','Mickey')
        self.assert_(item.hasValue('strings','Mouse'))
        self.assertEquals(len(item.strings),3)
        item.removeValue('strings','Goofy')
        self.failIf(item.hasValue('strings','Dog'))
        self.assertEquals(len(item.strings),2)
        item.removeValue('strings','Donald')
        self.failIf(item.hasValue('strings','Duck'))
        self.assertEquals(len(item.strings),1)
        item.removeValue('strings','Minnie')
        self.failIf(item.hasValue('strings','Mouse'))
        self.assertEquals(len(item.strings),0)

        # now write what we've done and read it back
        self._reopenRepository()
        item = self.rep.find('//item')
        self.failIf(item.hasValue('strings','Dog'))
        self.failIf(item.hasValue('strings','Duck'))
        self.failIf(item.hasValue('strings','Mouse'))
        self.assertEquals(len(item.strings),0)

if __name__ == "__main__":
#    import hotshot
#    profiler = hotshot.Profile('/tmp/TestItems.hotshot')
#    profiler.run('unittest.main()')
#    profiler.close()
    unittest.main()
