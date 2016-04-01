from os import listdir
from os.path import isfile, join
from xml.dom import minidom
from xml import parsers
import bug
import sys
from sklearn.feature_extraction import DictVectorizer
import scipy
import sklearn
import numpy as np
import code

DATA_DIRECTORY = 'data/huge-eclipse-xml-reports'
ONE_DAY = 86400
run_id = '20160330-0057'


class NodeUtil:
    @staticmethod
    def getText(nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)


class Features:
    vec = None
    matrix = None

    def __init__(self):
        files = [f for f in listdir(DATA_DIRECTORY) if isfile(join(DATA_DIRECTORY, f))]
        files = ['bugs000001-000100.xml']
        bugs = self.read_files(files)
        measurements = self.generate_dicts(bugs)

        self.vec = DictVectorizer()
        self.matrix = self.vec.fit_transform(measurements)
        self.matrix[np.isnan(self.matrix.todense())] = 0

        self.matrix = self.matrix.toarray()

    @staticmethod
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

    @staticmethod
    def read_files(files):
        bugs = []
        for f in files:
            print 'read', f
            file_path = join(DATA_DIRECTORY, f)
            b = Features.parse_file(file_path)
            if b is not None:
                bugs.extend(b)

        print 'parse completed'
        return bugs

    @staticmethod
    def generate_dicts(bugs):
        dicts = []
        for b in bugs:
            dicts.append(b.generate_dict())
        return dicts

    def row_op(self, op_col, op, op_val, func, func_col):
        col_index = self.vec.vocabulary_.get(op_col)
        filtered = self.matrix[op(self.matrix[:, col_index], op_val), :]

        app_col_index = self.vec.vocabulary_.get(func_col)
        values = filtered[:, app_col_index]

        return func(values)

if __name__ == '__main__':
    f = Features()
    f.row_op('priority', (lambda x, y: x == y), 3.0, np.average, 'priority')

    code.interact(local=locals())

    priority_index = f.vec.vocabulary_.get('priority')
    target = np.squeeze(np.asarray(f.matrix[:, priority_index].todense()))
    training = scipy.sparse.hstack([f.matrix[:, :priority_index], f.matrix[:, priority_index + 1:]])

    sklearn.datasets.dump_svmlight_file(training, target, 'run/training.dat', zero_based=False, multilabel=False)
