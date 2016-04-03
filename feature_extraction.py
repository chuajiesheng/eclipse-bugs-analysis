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
        self.vec = None
        self.matrix = None

    def read_into_memory(self):
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

    def filter_rows(self, op, op_col, op_val):
        col_index = self.vec.vocabulary_.get(op_col)
        filtered = self.matrix[op(self.matrix[:, col_index], op_val), :]
        return filtered

    def row_op(self, op_col, op, op_val, func, func_col):
        filtered = self.filter_rows(op, op_col, op_val)

        app_col_index = self.vec.vocabulary_.get(func_col)
        values = filtered[:, app_col_index]

        return func(values)

    def time_different(self):
        c = self.vec.get_feature_names().index('creation_ts')
        d = self.vec.get_feature_names().index('delta_ts')
        return self.matrix[:, c] - self.matrix[:, d]

    def bugs_between(self, x, col, days):
        ts = x[col]
        matching_rows = self.matrix[
            (((ts - days * ONE_DAY) < self.matrix[:, col]) &
             (self.matrix[:, col] < ts))
        ]
        return matching_rows.shape[0]

    def bugs_between_with_same_severity(self, x, col, days):
        ts = x[col]
        severity = x[self.vec.get_feature_names().index('bug_severity')]

        matching_rows = self.matrix[
            (((ts - days * ONE_DAY) < self.matrix[:, col]) &
             (self.matrix[:, col] < ts)) &
            (self.matrix[:, severity] == severity)
            ]
        return matching_rows.shape[0]

    def bugs_between_with_same_or_higher_severity(self, x, col, days):
        ts = x[col]
        severity = x[self.vec.get_feature_names().index('bug_severity')]

        matching_rows = self.matrix[
            (((ts - days * ONE_DAY) < self.matrix[:, col]) &
             (self.matrix[:, col] < ts)) &
            (self.matrix[:, severity] >= severity)
            ]
        return matching_rows.shape[0]

    def bugs_within(self, func, days):
        ts_col_index = self.vec.get_feature_names().index('creation_ts')
        row_matcher_func = (lambda x: func(x, ts_col_index, days))
        res = np.apply_along_axis(row_matcher_func, axis=1, arr=self.matrix)
        return res

    def generate_temporal_factor(self):
        tmp1 = self.time_different()
        tmp4 = self.bugs_within(self.bugs_between, 7)
        tmp5 = self.bugs_within(self.bugs_between_with_same_severity, 7)
        tmp6 = self.bugs_within(self.bugs_between_with_same_or_higher_severity, 7)
        return np.column_stack((tmp1, tmp4, tmp5, tmp6))

if __name__ == '__main__':
    f = Features()
    f.read_into_memory()
    # f.row_op('priority', (lambda x, y: x == y), 3.0, np.average, 'priority')
    f1 = f.generate_temporal_factor()

    code.interact(local=locals())

    priority_index = f.vec.get_feature_names().index('priority')
    target = np.squeeze(f.matrix[:, priority_index])
    training = np.hstack([f.matrix[:, :priority_index], f.matrix[:, priority_index + 1:]])

    sklearn.datasets.dump_svmlight_file(training, target, 'run/training.dat', zero_based=False, multilabel=False)
