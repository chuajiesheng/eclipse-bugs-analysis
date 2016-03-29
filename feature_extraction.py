from os import listdir
from os.path import isfile, join
from xml.dom import minidom
from xml import parsers
import bug
import sys
from sklearn.feature_extraction import DictVectorizer
import code

DATA_DIRECTORY = 'data/huge-eclipse-xml-reports'
run_id = '20160330-0057'


class NodeUtil:
    @staticmethod
    def getText(nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)


def parse_file(file_path):
    bugs = []
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

    return bugs


def read_files(files):
    bugs = []
    for f in files:
        print 'read', f
        file_path = join(DATA_DIRECTORY, f)
        b = parse_file(file_path)
        bugs.extend(b)

    print 'parse completed'
    return bugs


def generate_dicts(bugs):
    dicts = []
    for b in bugs:
        dicts.append(b.generate_dict())
    return dicts


if __name__ == '__main__':
    files = [f for f in listdir(DATA_DIRECTORY) if isfile(join(DATA_DIRECTORY, f))]
    files = ['bugs000001-000100.xml']
    bugs = read_files(files)
    measurements = generate_dicts(bugs)

    vec = DictVectorizer()
    matrix = vec.fit_transform(measurements)

    # code.interact(local=locals())
