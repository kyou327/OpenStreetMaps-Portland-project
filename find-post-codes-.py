def audit_postal_code(postal_code_types, postal_code):  
    if not postal_code.isupper() or ' ' not in postal_code:
        postal_code_types['Postal Codes'].add(postal_code)
    else:
        postal_code_types['other'].add(postal_code)
    return postal_code_types

def is_postal_code(elem):
    return (elem.attrib['k'] == "addr:postcode")

def audit(filename):
    f = (filename)
    postal_code_types = defaultdict(set)
    
    for event, element in ET.iterparse(f, events=("start",)):
        if element.tag =="way":
            for tag in element.iter("tag"):
                if is_postal_code(tag):
                    audit_postal_code(postal_code_types, tag.attrib['v'])
    print(dict(postal_code_types))

if __name__ == '__main__':
    audit(OSMFILE)

## split here for part 2 ##

OSMFILE = "sample.osm"
postal_code_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["97086", "97201", "97202", "997203", "97204", "97205", "97206", "97207", 
            "97208", "97209", "97210", "97211", "97212", "97213", "97214", "97215", 
	"97216", "97217", "97218", "97219", "97220", "97221", "97222", "97223", "97224", "97225", "97226","97227", 		"97228", "97229", "97230", "97231", "97232", "97233", "97234", "97235", "97236", "97237", "97238", "97239", 			"97240", "97241", "97242", "97243", "97244", "97245", "97246", "97247", "97248", "97249", "97250", "97251", "97252", "97253", "97254", "97255", "97256", "97257", "97258", "97259", "97260", "97261", "97262", "97263", "97264", "97265", "97266", "97267", "97268", "97269", "97270", "97271", "97272", "97273", "97274", "97275", "97276", "97277", "97278", "97279", "97280", "97281", "97282", "97283", "97284", "97285", "97286", "97287", "97288", "97289", "97290", "97291", "97292", "97293", "97294", "97295", "97296", "97297", "97298"]
	


def audit_postal_code(postal_code_types, postal_codes):
    m = postal_code_type_re.search(postal_codes)
    if m:
        postal_code = m.group()
        if postal_code not in expected:
            postal_code_types[postal_code].add(postal_code)

def is_postal_code(elem):
    return (elem.attrib['k'] == "addr:postcode")


def audit():
    postal_codes = defaultdict(set)
    for event, elem in ET.iterparse(OSMFILE, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postal_code(tag):
                    audit_postal_code(postal_codes, tag.attrib['v'])
    
    print("Postal codes in data set that are not in Portland")
    pprint.pprint(dict(postal_codes))

if __name__ == '__main__':
    audit()