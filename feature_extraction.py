from os import listdir
from os.path import isfile, join
from xml.dom import minidom
from xml import parsers
import threading
import bug

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


def parse_file(file_path):
    xmldoc = None

    try:
        xmldoc = minidom.parse(file_path)
    except parsers.expat.ExpatError as e:
        print file_path, '-', e
        return

    itemlist = xmldoc.getElementsByTagName('bug')
    for item in itemlist:
        b = bug.Bug(item)
        if b is not None:
            # bugs.append(bug)
            # print b.to_csv()
            print b.to_short_desc_csv()


def multithread_parse_file(file_path):
    t = threading.Thread(target=parse_file, args=(file_path,))
    t.start()


if __name__ == '__main__':
    files = [f for f in listdir(DATA_DIRECTORY) if isfile(join(DATA_DIRECTORY, f))]
    for f in files:
        file_path = join(DATA_DIRECTORY, f)
        parse_file(file_path)
