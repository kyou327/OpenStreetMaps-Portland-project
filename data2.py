# coding: utf-8

# ## Audit The Data
# 
# In this section we will iterate over the street names and zip codes. We will check for uniformity in the data against an expected dictionary of values.

# In[32]:


import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import re
import xml.etree.cElementTree as ET
import csv
import codecs

osm_file = open("sample.osm", "r")

#

#########################################

# Search for all unexpected street types

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)



# List of expected street name values
expected = ["Street", "Avenue", "Lane", "Way", "Boulevard",  
"Drive", "Court", "Place", "Square", "Road", "Trail", "Parkway", "Commons", "North", "South", "West", "East"]

# Here we add any street name that isn't in our expected dictionary
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
    return street_types

# Here we create a dictionary of our postal codes
def audit_postal_code(postal_code_types, postal_code):  
    if not postal_code.isupper() or ' ' not in postal_code:
        postal_code_types['case_whitespace_problems'].add(postal_code)
    else:
        postal_code_types['other'].add(postal_code)
    return postal_code_types



def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_postal_code(elem):
    return (elem.attrib['k'] == "addr:postcode")


def audit(filename):
    f = (filename)
    street_types = defaultdict(set)
    postal_code_types = defaultdict(set)
    
    for event, element in ET.iterparse(f, events=("start",)):
        if element.tag == "node" or element.tag =="way":
            for tag in element.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                if is_postal_code(tag):
                    audit_postal_code(postal_code_types, tag.attrib['v'])
                    
    f.close()
    return dict(street_types), dict(postal_code_types)


# need to fix the street and postal code data 

# ## Fixing Street Names and Postal Codes
# use the mapping to replace the errors with uniform types.




mapping = { "St": "Street",
            "St.": "Street",
            "Ave" : "Avenue",
            "Ave.": "Avenue",
            "Rd.": "Road",
            "Rd": "Road",
            "E" : "East",
            "W" : "West",
            "S" : "South",
            "N" : "North"
            }

# Here we iterate over each name and update it in regards 
# to the mapping

def update_name(street_name, mapping):
    street_name = street_name.replace(' ', ' ')
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        street_type2 = ' '.join(street_name.split()[0:])
        if street_type in mapping.keys():
            #print 'Before: ' , name
            street_name = re.sub(street_type, mapping[street_type],street_name)
            #print 'After: ', name
        
    return street_name

# Here we iterate over the postal codes making them a 
# uniform 5 digit number

def update_postal_code(postal_code):
    postal_code = postal_code.upper()
    if ' ' not in postal_code:
        if len(postal_code) != 5:
            postal_code = postal_code[0:5]
    return postal_code


def street_test():
    
    st_types = audit(osm_file)[0]
    print ""
    for st_types, st_names in st_types.iteritems():
        for name in st_names:
            better_name = update_name(name, mapping)
            print name, "->", better_name
            
def postal_code_test():
    postcode_types = audit(osm_file)[1]
    #pprint(postcode_types)
    print ""
    
    for postcode_type, postcodes in postcode_types.iteritems():
        for postcode in postcodes:
            better_postcode = update_postal_code(postcode)
            print postcode, "=>", better_postcode
        


# The main portion of the code is the Shape_element and process_map
# which will clean the xml data and write it out to CSV files.


OSM_PATH = "sample.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+\/&<>;\'"\?%#$@\,\. \t\r\n]')


# Make sure the fields order in the csvs matches the 
# column order in the sql table schema

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']



# The function 'make_tag_dict()' takes an element and a child tag, and then creates a dictionary with keys 'id', 'key', 'value', 'type'
# according to the rules specified in the problem

def make_tag_dict(element, tag):
    tag_attribs = {}                           
    tag_attribs['id'] = element.attrib['id']
    
    if is_street_name(tag):
        tag_attribs['value'] = update_name(tag.attrib['v'], mapping)  
    elif is_postal_code(tag):
        tag_attribs['value'] = update_postal_code(tag.attrib['v'])              # update street names and postal codes
                                                                                
    else:
        tag_attribs['value'] = tag.attrib['v']
    
	# checking the k attribute to split it by type on the : sign.
	
    k_attrib = tag.attrib['k']
    if not PROBLEMCHARS.search(k_attrib):
        if LOWER_COLON.search(k_attrib):         
            key = k_attrib.split(':', 1)[1]     
            tipe = k_attrib.split(':', 1)[0]    
            tag_attribs['key'] = key
            tag_attribs['type'] = tipe
        else:
            tag_attribs['key'] = k_attrib
            tag_attribs['type'] = 'regular'
        
    return tag_attribs


def shape_element(element):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

 # Populate the 'node_attribs' dict with the keys from NODE_FIELDS and the values from the 'element.attrib' dictionary
 # Call the function make_tag_dict() that creates a dictionary of attributes.  Then append this dict to the tags list.
 # ELIF Do the same for Ways.
 
    if element.tag == 'node':
        for item in NODE_FIELDS:                      
            node_attribs[item] = element.attrib[item] 
        for tag in element.iter('tag'):
            if tag.attrib['v'] == "" or tag.attrib['v'] == None:
                continue
            tag_attribs = make_tag_dict(element, tag) 
            tags.append(tag_attribs)                  
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        for item in WAY_FIELDS:                       
            way_attribs[item] = element.attrib[item]  
        for tag in element.iter('tag'):
            if tag.attrib['v'] == "" or tag.attrib['v'] == None:
                continue
            tag_attribs = make_tag_dict(element, tag) 
            tags.append(tag_attribs)                  
            
        position = 0
        for tag in element.iter('nd'):
            nd_attribs = {}                           
            nd_attribs['id'] = element.attrib['id']   
            nd_attribs['node_id'] = tag.attrib['ref']
            nd_attribs['position'] = position
            position += 1
            way_nodes.append(nd_attribs)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
    

# ================================================== #
#              Other Helper Functions                #
# ================================================== #


def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()





class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

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

        

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                
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