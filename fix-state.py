def fix_state(elem):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_state(tag):
                    if tag.attrib['v'] != 'OR':
                        print ("Fixed State: ", tag.attrib['v'], "=> 'OR'")
                        tag.attrib['v'] = 'OR'