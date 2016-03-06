from os import listdir
from os.path import isfile, join
from xml.dom import minidom
from xml import parsers
import code
import threading

DATA_DIRECTORY = 'data/huge-eclipse-xml-reports'
bugs = []


class LongDesc:
    who = None
    bug_when = None
    thetext = None

    def __init__(self, item):
        self.who = item.getElementsByTagName('who')[0].firstChild.nodeValue
        self.bug_when = item.getElementsByTagName('bug_when')[0].firstChild.nodeValue
        self.thetext = item.getElementsByTagName('thetext')[0].firstChild.nodeValue


class Bug:
    bug_id = None
    creation_ts = None
    short_desc = None
    delta_ts = None
    reporter_accessible = None
    cclist_accessible = None
    classification_id = None
    classification = None
    product = None
    component = None
    version = None
    rep_platform = None
    op_sys = None
    bug_status = None
    resolution = None
    priority = None
    bug_severity = None
    target_milestone = None
    dependson = []
    everconfirmed = None
    reporter = None
    assigned_to = None
    cc = []
    qa_contact = None

    long_desc = []

    def __init__(self, item):
        if item is None:
            return None

        self.bug_id = item.getElementsByTagName('bug_id')[0].firstChild.nodeValue

        if len(item.attributes) > 0 and 'error' in item.attributes.keys():
            error = item.attributes['error']
            if error is not None and (error.value == 'NotFound' or error.value == 'NotPermitted'):
                return None

        self.creation_ts = item.getElementsByTagName('creation_ts')[0].firstChild.nodeValue

        short_desc_element = item.getElementsByTagName('short_desc')
        if short_desc_element is not None and len(short_desc_element) > 0:
            self.short_desc = short_desc_element[0].firstChild.nodeValue

        self.delta_ts = item.getElementsByTagName('delta_ts')[0].firstChild.nodeValue
        self.reporter_accessible = item.getElementsByTagName('reporter_accessible')[0].firstChild.nodeValue
        self.cclist_accessible = item.getElementsByTagName('cclist_accessible')[0].firstChild.nodeValue
        self.classification_id = item.getElementsByTagName('classification_id')[0].firstChild.nodeValue
        self.classification = item.getElementsByTagName('classification')[0].firstChild.nodeValue
        self.product = item.getElementsByTagName('product')[0].firstChild.nodeValue
        self.component = item.getElementsByTagName('component')[0].firstChild.nodeValue
        self.version = item.getElementsByTagName('version')[0].firstChild.nodeValue
        self.rep_platform = item.getElementsByTagName('rep_platform')[0].firstChild.nodeValue
        self.op_sys = item.getElementsByTagName('op_sys')[0].firstChild.nodeValue
        self.bug_status = item.getElementsByTagName('bug_status')[0].firstChild.nodeValue

        resolution_element = item.getElementsByTagName('resolution')
        if resolution_element is not None and len(resolution_element) > 0:
            self.resolution = resolution_element[0].firstChild.nodeValue

        self.priority = item.getElementsByTagName('priority')[0].firstChild.nodeValue
        self.bug_severity = item.getElementsByTagName('bug_severity')[0].firstChild.nodeValue
        self.target_milestone = item.getElementsByTagName('target_milestone')[0].firstChild.nodeValue

        dependson_elements = item.getElementsByTagName('dependson')
        self.dependson = []
        if dependson_elements is not None and len(dependson_elements) > 0:
            for dependson_element in dependson_elements:
                self.dependson.append(dependson_element.firstChild.nodeValue)

        self.everconfirmed = item.getElementsByTagName('everconfirmed')[0].firstChild.nodeValue
        self.reporter = item.getElementsByTagName('reporter')[0].firstChild.nodeValue
        self.assigned_to = item.getElementsByTagName('assigned_to')[0].firstChild.nodeValue

        cc_elements = item.getElementsByTagName('cc')
        if cc_elements is not None and len(cc_elements) > 0:
            self.cc = []
            for cc in cc_elements:
                self.cc.append(cc.firstChild.nodeValue)

        qa_contact_element = item.getElementsByTagName('qa_contact')
        if qa_contact_element is not None and len(qa_contact_element) > 0:
            self.qa_contact = qa_contact_element[0].firstChild.nodeValue

        self.long_desc = []
        for desc in item.getElementsByTagName('long_desc'):
            self.long_desc.append(LongDesc(desc))


def parse_file(file_path):
    xmldoc = None

    try:
        xmldoc = minidom.parse(file_path)
    except parsers.expat.ExpatError as e:
        print file_path, '-', e
        return

    itemlist = xmldoc.getElementsByTagName('bug')
    for item in itemlist:
        bug = Bug(item)
        bugs.append(bug)

if __name__ == '__main__':
    files = [f for f in listdir(DATA_DIRECTORY) if isfile(join(DATA_DIRECTORY, f))]
    for f in files:
        file_path = join(DATA_DIRECTORY, f)
        t = threading.Thread(target=parse_file, args=(file_path,))
        t.start()



