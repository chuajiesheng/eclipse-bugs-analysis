from os import listdir
from os.path import isfile, join
from xml.dom import minidom
from xml import parsers
import bug
import sys

DATA_DIRECTORY = 'data/huge-eclipse-xml-reports'
run_id = '20160330-0057'
bugs = []

class NodeUtil:
    @staticmethod
    def getText(nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)


def parse_file(file_path):
    xmldoc = None

    try:
        xmldoc = minidom.parse(file_path)
    except parsers.expat.ExpatError as e:
        str = '{} - {}'.format(file_path, e)
        print >> sys.stderr, str
        return

    itemlist = xmldoc.getElementsByTagName('bug')
    for item in itemlist:
        b = bug.Bug(item)
        if b is not None and not b.error:
            bugs.append(b)


if __name__ == '__main__':
    files = [f for f in listdir(DATA_DIRECTORY) if isfile(join(DATA_DIRECTORY, f))]
    # files = ['bugs000001-000100.xml']
    for f in files:
        print 'read', f
        file_path = join(DATA_DIRECTORY, f)
        parse_file(file_path)

    print 'parse completed'
