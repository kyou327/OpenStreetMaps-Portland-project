def is_state(elem):
    return (elem.attrib['k'] == "addr:state")

state_types = defaultdict(int)

def audit_state(state_types, state_name):
    if state_name != 'OR':
        state_types[state_name] += 1
        print(state_name)

for event, elem in ET.iterparse(OSMFILE, events =("start",)):
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            if is_state(tag):
                audit_state(state_types, tag.attrib['v'])