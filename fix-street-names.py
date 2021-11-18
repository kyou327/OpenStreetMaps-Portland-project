%%capture

OSMFILE = "portland_oregonosm.xml"
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

                                
fix_street(elem)