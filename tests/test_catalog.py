# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Validator/blob/master/LICENSE.md
#
# Unit tests for RedfishServiceValidator.py
#

import unittest
import sys

sys.path.append('../')

import common.catalog as catalog

class TestCatalog(unittest.TestCase):
    def test_fuzzy(self):
        val = catalog.get_fuzzy_property('PropertyA', {'Name': 'Payload', 'PropertyB': False})
        self.assertEqual(val, 'PropertyB')
        val = catalog.get_fuzzy_property('PropertyA', {'Name': 'Payload', 'PropertyB': False, 'PropertyA': False})
        self.assertEqual(val, 'PropertyA')
        val = catalog.get_fuzzy_property('PropertyA', {'Name': 'Payload'}, [])
        self.assertEqual(val, 'PropertyA')
        val = catalog.get_fuzzy_property('PropertyA', {'Name': 'Payload'}, ['PropertyB'])
        self.assertEqual(val, 'PropertyA')

    def test_catalog(self):
        my_catalog = catalog.SchemaCatalog('./tests/testdata/schemas/')

        my_schema_doc = my_catalog.getSchemaDocByClass('Example')

        self.assertRaises(catalog.MissingSchemaError, my_catalog.getSchemaDocByClass, 'NotExample')

        my_schema = my_catalog.getSchemaInCatalog('Example.v1_0_0')
        my_schema = my_catalog.getSchemaInCatalog('Example.v1_0_0')

        my_type = my_catalog.getTypeInCatalog('Example.v1_7_0.Example')
        my_type = my_catalog.getTypeInCatalog('Example.v1_2_0.Links')
    
    def test_schema_doc(self):
        my_catalog = catalog.SchemaCatalog('./tests/testdata/schemas/')
        with open('./tests/testdata/schemas/Example_v1.xml') as f:
            my_doc = catalog.SchemaDoc(f.read(), my_catalog, 'Example_v1.xml')
        
        ref = my_doc.getReference('ExampleResource')
        ref = my_doc.getReference('ExampleResource.v1_0_0')
        ref = my_doc.getReference('ExampleResource.v1_0_1')
        ref = my_doc.getReference('ExampleResource.v1_9_9')
        ref = my_doc.getReference('Redfish')
        ref = my_doc.getReference('RedfishExtension.v1_0_0')
    
        my_type = my_doc.getTypeInSchemaDoc('Example.v1_0_0.Example')
        my_type = my_doc.getTypeInSchemaDoc(my_type)
        my_type = my_doc.getTypeInSchemaDoc('Example.v1_9_9.Example')
        my_type = my_doc.getTypeInSchemaDoc('Example.v1_0_0.Actions')
        my_type = my_doc.getTypeInSchemaDoc('ExampleResource.v1_0_0.ExampleResource')
        self.assertRaises(catalog.MissingSchemaError, my_doc.getTypeInSchemaDoc, 'NoExample.v1_0_0.NoExample')

    def test_schema_class(self):
        my_catalog = catalog.SchemaCatalog('./tests/testdata/schemas/')
        my_doc = my_catalog.getSchemaDocByClass('Example.v1_0_0')
        my_schema = my_catalog.getSchemaInCatalog('Example.v1_0_0')
    
    def test_basic_properties(self):
        prop = catalog.RedfishProperty("Edm.Int").populate(1)
        prop = catalog.RedfishProperty("Edm.Decimal").populate(1.1)
        prop = catalog.RedfishProperty("Edm.Guid").populate("123")
        prop = catalog.RedfishProperty("Edm.Guid").populate(catalog.REDFISH_ABSENT)
        obj = prop.as_json()
        obj = prop.getLinks()

    def test_basic_properties_check(self):
        prop = catalog.RedfishProperty("Edm.Int").populate(1, check=True)
        prop = catalog.RedfishProperty("Edm.Int").populate(1.1, check=True)
        prop = catalog.RedfishProperty("Edm.Int").populate("1", check=True)
        prop = catalog.RedfishProperty("Edm.Decimal").populate(1.1, check=True)
        prop = catalog.RedfishProperty("Edm.Decimal").populate("1.1", check=True)
        prop = catalog.RedfishProperty("Edm.String").populate("1")
        prop = catalog.RedfishProperty("Edm.String").populate(1)
        prop = catalog.RedfishProperty("Edm.Guid").populate("123", check=True)
        prop = catalog.RedfishProperty("Edm.Guid").populate(catalog.REDFISH_ABSENT, check=True)
    
    def test_object(self):
        my_catalog = catalog.SchemaCatalog('./tests/testdata/schemas/')
        my_schema_doc = my_catalog.getSchemaDocByClass("ExampleResource.v1_0_0.ExampleResource")
        my_type = my_schema_doc.getTypeInSchemaDoc("ExampleResource.v1_0_0.ExampleResource")
        object = catalog.RedfishObject( my_type )
        dct = object.as_json()
        dct = object.getLinks()
        object = catalog.RedfishObject( my_type ).populate({"Id": None, "Description": None})
        dct = object.as_json()
        dct = object.getLinks()


if __name__ == '__main__':
    unittest.main()