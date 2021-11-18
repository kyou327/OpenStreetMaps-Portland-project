#original code in the 'data.py' file also in the lesson 11 of 'Case Study OpenStreetMap data'
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from collections import defaultdict
import unicodecsv
import csv
import codecs
import re
import pprint
import xml.etree.cElementTree as ET

# import cerberus
# Cerberus commented out because Anaconda environment refuses to accept cerberus package. 
# All validator code commented out because of this environment issue. 
# The rest of the code can still function without cerberus validator.

# import schema

OSM_PATH = "sample.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

print ("Street Names and State Codes Fixed:")
print ("\n")

# Fix Street & State Names 

#located in 'fix-street-names.py'

OSMFILE = "sample.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Plaza", "Park"]

mapping = {"St": "Street",
           "ST": "Street",
           "St.": "Street",
           "St,": "Street",
           "Street.": "Street",
           "street": "Street",
           "Sq": "Square",
           "Rd.": "Road",
           "Rd": "Road",
           "Ave": "Avenue",
           "DR.": "Drive",
           "Blvd": "Boulevard"
           }

# Auditing the street names and creating the dictionary for the fixing element to iterate through.

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
	

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osmfile, events=("start",)):

        if elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

# updates the errors against the mapping to replace the name with the correct form.

def update_name(name, mapping):
    for key, value in mapping.items():
        if re.search(key, name):
            name = re.sub(street_type_re, value, name)

    return name


def test():
    st_types = audit(OSMFILE)
    for st_type, ways in st_types.items():
        for name in ways:
            better_name = update_name(name, mapping)
            print (name, "=>", better_name)

            
# Auditing state functions to parse through for the fixing function

def is_state(elem):
    return (elem.attrib['k'] == "addr:state")

state_types = defaultdict(int)

def audit_state(state_types, state_name):
    if state_name != 'OR':
        state_types[state_name] += 1

for event, elem in ET.iterparse(OSMFILE, events =("start",)):
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            if is_state(tag):
                audit_state(state_types, tag.attrib['v'])


# fixes the street names by checking if its in the mapping and then replacing the errors to be uniform accrodingly

def fix_street(elem):

    street_types = defaultdict(set)
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            if is_street_name(tag):
                audit_street_type(street_types, tag.attrib['v'])

            for st_type, ways in street_types.items():
                for name in ways:
                    for key,value in mapping.items():
                        n = street_type_re.search(name)
                        if n:
                            street_type = n.group()
                            if street_type not in expected:
                                if street_type in mapping:
                                    better_name = name.replace(key,value)
                                    if better_name != name:
                                        print ("Fixed Street:", tag.attrib['v'], "=>", better_name)
                                        tag.attrib['v'] = better_name
                                        return
#is located in 'fix-state.py'
#This will replace the incorrect state (WA) with (OR).
                                    
def fix_state(elem):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_state(tag):
                    if tag.attrib['v'] != 'OR':
                        print ("Fixed State: ", tag.attrib['v'], "=> 'OR'")
                        tag.attrib['v'] = 'OR'
                                    
def fix_element(elem):
    fix_street(elem)
    fix_state(elem)
                                

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # Fix data issues, based on auditing results
    # runs the fix_element function which calls the fix state and fix street functions. 
    # This will replace the necessary errors.
    # The rest of shape_element will then run through the nodes and ways tags to make sure that all
    # of the elements are correct type for each row location.
    
    fix_element(element)

    if element.tag == 'node':

            for node_field in node_attr_fields:
                node_attribs[node_field] =element.attrib[node_field]

            for tag in element.iter('tag'):
                k = tag.attrib['k']

                # ignores tags containing problem characters in the k tag attribute:

                if re.search(PROBLEMCHARS,k):
                    continue
                else:
                    pass

                tag_dict = {}

                tag_dict['id'] = node_attribs['id']

                colon_find = re.split('[:]', k)

                if len(colon_find) == 1:

                    tag_dict['key'] = k
                    tag_dict['type'] = 'regular'

                elif len(colon_find) == 2:

                    tag_dict['key'] = colon_find[1]
                    tag_dict['type'] = colon_find[0]

                elif len(colon_find) > 2:

                    tag_dict['key'] = ':'.join(colon_find[1:])
                    tag_dict['type'] = colon_find[0]

                tag_dict['value'] = tag.attrib['v']

                tags.append(tag_dict)

            return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':

        for way_field in way_attr_fields:
            way_attribs[way_field] =element.attrib[way_field]

        for tag in element.iter('tag'):
            k = tag.attrib['k']

            # ignores tags containing problem characters in the k tag attribute:

            if re.search(PROBLEMCHARS,k):
                print ("Problem character found - skipping element")
                continue
            else:
                pass

            tag_dict = {}

            tag_dict['id'] = way_attribs['id']

            colon_find = re.split('[:]', k)

            if len(colon_find) == 1:

                tag_dict['key'] = k
                tag_dict['type'] = 'regular'

            elif len(colon_find) == 2:

                tag_dict['key'] = colon_find[1]
                tag_dict['type'] = colon_find[0]

            elif len(colon_find) > 2:

                tag_dict['key'] = ':'.join(colon_find[1:])
                tag_dict['type'] = colon_find[0]

            tag_dict['value'] = tag.attrib['v']

            tags.append(tag_dict)

        n = 0
        for nd in element.iter('nd'):

            nd_dict = {}

            nd_dict['id'] = way_attribs['id']
            nd_dict['node_id'] = nd.attrib['ref']
            nd_dict['position'] = n
            way_nodes.append(nd_dict)
            n+=1

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


        
# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

# Validator elements commented out because cerberus package can't be installed. See above comments.

#def validate_element(element, validator, schema=schema):
#    """Raise ValidationError if element does not match schema"""
#    if validator.validate(element, schema) is not True:
#        field, errors = next(validator.errors.items())
#        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
#        error_string = pprint.pformat(errors)
#        
#        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow(
            {
                k: (v.encode("utf-8") if isinstance(v, str) else v)
                for k, v in row.items()
            }
        )

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w', encoding='utf-8') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w', encoding='utf-8') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w', encoding='utf-8') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w', encoding='utf-8') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w', encoding='utf-8') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

    # Validator elements commented out because cerberus package can't be installed. See above comments.
        # validator = cerberus.Validator()
    
    # process_map() relies on shape_element() to iterate thru the code and parse which dict the data is parsed to
    # and then it writes it to the appropriate CSV file.

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
              #  if validate is True:
               #     validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)
    
print("Reshaping and export complete.")