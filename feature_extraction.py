from os import listdir
from os.path import isfile, join
from xml.dom import minidom
from xml import parsers
import code
import threading

DATA_DIRECTORY = 'data/huge-eclipse-xml-reports'
bugs = []

class NodeUtil:
    @staticmethod
    def getText(nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)


class LongDesc:
    who = None
    bug_when = None
    thetext = None

    def __init__(self, item):
        self.who = NodeUtil.getText(item.getElementsByTagName('who')[0].childNodes)
        self.bug_when = NodeUtil.getText(item.getElementsByTagName('bug_when')[0].childNodes)

        thetext_element = item.getElementsByTagName('thetext')
        self.thetext = NodeUtil.getText(thetext_element[0].childNodes)


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

        self.bug_id = NodeUtil.getText(item.getElementsByTagName('bug_id')[0].childNodes)

        if len(item.attributes) > 0 and 'error' in item.attributes.keys():
            error = item.attributes['error']
            if error is not None and (error.value == 'NotFound' or error.value == 'NotPermitted'):
                return None

        self.creation_ts = NodeUtil.getText(item.getElementsByTagName('creation_ts')[0].childNodes)

        short_desc_element = item.getElementsByTagName('short_desc')
        if short_desc_element is not None and len(short_desc_element) > 0:
            self.short_desc = NodeUtil.getText(short_desc_element[0].childNodes)

        self.delta_ts = NodeUtil.getText(item.getElementsByTagName('delta_ts')[0].childNodes)
        self.reporter_accessible = NodeUtil.getText(item.getElementsByTagName('reporter_accessible')[0].childNodes)
        self.cclist_accessible = NodeUtil.getText(item.getElementsByTagName('cclist_accessible')[0].childNodes)
        self.classification_id = NodeUtil.getText(item.getElementsByTagName('classification_id')[0].childNodes)
        self.classification = NodeUtil.getText(item.getElementsByTagName('classification')[0].childNodes)
        self.product = NodeUtil.getText(item.getElementsByTagName('product')[0].childNodes)
        self.component = NodeUtil.getText(item.getElementsByTagName('component')[0].childNodes)
        self.version = NodeUtil.getText(item.getElementsByTagName('version')[0].childNodes)
        self.rep_platform = NodeUtil.getText(item.getElementsByTagName('rep_platform')[0].childNodes)
        self.op_sys = NodeUtil.getText(item.getElementsByTagName('op_sys')[0].childNodes)
        self.bug_status = NodeUtil.getText(item.getElementsByTagName('bug_status')[0].childNodes)

        resolution_element = item.getElementsByTagName('resolution')
        if resolution_element is not None and len(resolution_element) > 0:
            self.resolution = NodeUtil.getText(resolution_element[0].childNodes)

        self.priority = NodeUtil.getText(item.getElementsByTagName('priority')[0].childNodes)
        self.bug_severity = NodeUtil.getText(item.getElementsByTagName('bug_severity')[0].childNodes)
        self.target_milestone = NodeUtil.getText(item.getElementsByTagName('target_milestone')[0].childNodes)

        dependson_elements = item.getElementsByTagName('dependson')
        self.dependson = []
        if dependson_elements is not None and len(dependson_elements) > 0:
            for dependson_element in dependson_elements:
                self.dependson.append(NodeUtil.getText(dependson_element.childNodes))

        self.everconfirmed = NodeUtil.getText(item.getElementsByTagName('everconfirmed')[0].childNodes)
        self.reporter = NodeUtil.getText(item.getElementsByTagName('reporter')[0].childNodes)
        self.assigned_to = NodeUtil.getText(item.getElementsByTagName('assigned_to')[0].childNodes)

        cc_elements = item.getElementsByTagName('cc')
        if cc_elements is not None and len(cc_elements) > 0:
            self.cc = []
            for cc in cc_elements:
                self.cc.append(NodeUtil.getText(cc.childNodes))

        qa_contact_element = item.getElementsByTagName('qa_contact')
        if qa_contact_element is not None and len(qa_contact_element) > 0:
            self.qa_contact = NodeUtil.getText(qa_contact_element[0].childNodes)

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



