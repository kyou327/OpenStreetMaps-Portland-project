import xml.etree.cElementTree as ET
import pprint

tags={}
def count_tags(filename):
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag in tags.keys():
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
        print(tags)
    return tags
    
def test():

    tags = count_tags('example.osm')
    pprint.pprint(tags)
    assert tags == {'bounds': 1,
                     'member': 3,
                     'nd': 4,
                     'node': 20,
                     'osm': 1,
                     'relation': 1,
                     'tag': 7,
                     'way': 1}
    

if __name__ == "__main__":
    test()