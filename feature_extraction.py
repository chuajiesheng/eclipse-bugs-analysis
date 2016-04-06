from os import listdir
from os.path import isfile, join
from xml.dom import minidom
from xml import parsers
import bug
import sys
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
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
    bugs = None
    vec = None
    matrix = None

    def __init__(self):
        self.bugs = None
        self.vec = None
        self.matrix = None

    def read_into_memory(self):
        files = [f for f in listdir(DATA_DIRECTORY) if isfile(join(DATA_DIRECTORY, f))]
        # files = ['bugs000001-000100.xml', 'bugs000101-000200.xml',
        #          'bugs000201-000300.xml', 'bugs000301-000400.xml']
        self.bugs = sorted(self.read_files(files))
        measurements = self.generate_dicts(self.bugs)

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

    def apply_over(self, col, func, val):
        ts_col_index = self.vec.get_feature_names().index(col)
        row_matcher_func = (lambda x: func(x, ts_col_index, val))
        res = np.apply_along_axis(row_matcher_func, axis=1, arr=self.matrix)
        return res

    def generate_temporal_factor(self):
        tmp1 = self.time_different()

        reported_within = 7

        tmp4 = self.apply_over('creation_ts', self.bugs_between, reported_within)
        tmp5 = self.apply_over('creation_ts', self.bugs_between_with_same_severity, reported_within)
        tmp6 = self.apply_over('creation_ts', self.bugs_between_with_same_or_higher_severity, reported_within)

        reported_within = 30

        tmp7 = self.apply_over('creation_ts', self.bugs_between, reported_within)
        tmp8 = self.apply_over('creation_ts', self.bugs_between_with_same_severity, reported_within)
        tmp9 = self.apply_over('creation_ts', self.bugs_between_with_same_or_higher_severity, reported_within)

        reported_within = 1

        tmp10 = self.apply_over('creation_ts', self.bugs_between, reported_within)
        tmp11 = self.apply_over('creation_ts', self.bugs_between_with_same_severity, reported_within)
        tmp12 = self.apply_over('creation_ts', self.bugs_between_with_same_or_higher_severity, reported_within)

        reported_within = 3

        tmp13 = self.apply_over('creation_ts', self.bugs_between, reported_within)
        tmp14 = self.apply_over('creation_ts', self.bugs_between_with_same_severity, reported_within)
        tmp15 = self.apply_over('creation_ts', self.bugs_between_with_same_or_higher_severity, reported_within)

        return np.column_stack((tmp1,
                                tmp4, tmp5, tmp6,
                                tmp7, tmp8, tmp9,
                                tmp10, tmp11, tmp12,
                                tmp13, tmp14, tmp15))

    def bugs_reported_by_author(self):
        author_factor = scipy.sparse.lil_matrix((self.matrix.shape[0], 2))
        assert author_factor.shape == (self.matrix.shape[0], 2)
        related_authors = [f for f in self.vec.get_feature_names() if 'reporter' in f]
        for author in related_authors:
            assert author is not None

            # find index to apply to
            reported_col = self.vec.get_feature_names().index(author)
            applicable_rows = np.where(self.matrix[:, reported_col] == 1)

            author_email = author[author.index('=') + 1:]

            # find assigned_to bugs
            fix_col_name = 'assigned_to=' + author_email

            if fix_col_name in self.vec.get_feature_names():
                fix_col_num = self.vec.get_feature_names().index(fix_col_name)
                bugs_author_fixed = self.matrix[(self.matrix[:, fix_col_num] == 1)]
                assert bugs_author_fixed.shape[1] == self.matrix.shape[1]

                # get feature
                priority_col = self.vec.get_feature_names().index('priority')
                avg_priority = np.average(bugs_author_fixed[:, priority_col])  # aut1
                median_priority = np.median(bugs_author_fixed[:, priority_col])  # aut2
            else:
                avg_priority = 0
                median_priority = 0

            author_factor[applicable_rows, 0] = avg_priority
            author_factor[applicable_rows, 1] = median_priority
        return author_factor

    def median_priority_of_bugs_prior(self, x, ts_col, pri_col):
        ts = x[ts_col]

        pri_feature_name = [f for f in self.vec.get_feature_names()
                            if (pri_col in f) and
                            (x[self.vec.get_feature_names().index(f)] == 1)][0]
        assert pri_feature_name is not None
        pri_feature = self.vec.get_feature_names().index(pri_feature_name)

        priority_col = self.vec.get_feature_names().index('priority')
        matching_rows = self.matrix[(self.matrix[:, pri_feature] == 1) & (self.matrix[:, ts_col] < ts)]

        if matching_rows.shape[0] == 0:
            return 0

        return np.mean(matching_rows[:, priority_col])

    def mean_priority_of_bugs_prior(self, x, ts_col, pri_col):
        ts = x[ts_col]

        pri_feature_name = [f for f in self.vec.get_feature_names()
                            if (pri_col in f) and
                            (x[self.vec.get_feature_names().index(f)] == 1)][0]
        assert pri_feature_name is not None
        pri_feature = self.vec.get_feature_names().index(pri_feature_name)

        priority_col = self.vec.get_feature_names().index('priority')
        matching_rows = self.matrix[
            (self.matrix[:, pri_feature] == 1) &
            (self.matrix[:, ts_col] < ts)
        ]

        if matching_rows.shape[0] == 0:
            return 0

        return np.nan_to_num(np.median(matching_rows[:, priority_col]))

    def no_of_bugs_prior(self, x, ts_col, pri_col):
        ts = x[ts_col]

        pri_feature_name = [f for f in self.vec.get_feature_names()
                            if (pri_col in f) and
                            (x[self.vec.get_feature_names().index(f)] == 1)][0]
        assert pri_feature_name is not None
        pri_feature = self.vec.get_feature_names().index(pri_feature_name)

        matching_rows = self.matrix[(self.matrix[:, pri_feature] == 1) & (self.matrix[:, ts_col] < ts)]
        return matching_rows.shape[0]

    def generate_author_factor(self):
        author_factor = self.bugs_reported_by_author().toarray()

        aut3 = self.apply_over('creation_ts', self.mean_priority_of_bugs_prior, 'reporter')
        aut3 = aut3.reshape(aut3.shape[0], 1)

        aut4 = self.apply_over('creation_ts', self.median_priority_of_bugs_prior, 'reporter')
        aut4 = aut3.reshape(aut4.shape[0], 1)

        aut5 = self.apply_over('creation_ts', self.no_of_bugs_prior, 'reporter')
        aut5 = aut5.reshape(aut5.shape[0], 1)

        return np.concatenate((author_factor, aut3, aut4, aut5), axis=1)

    def generate_report_factor(self):
        documents = [item.to_short_desc() for item in self.bugs]
        assert len(documents) == self.matrix.shape[0]
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
        cosine_similarities = cosine_similarity(tfidf_matrix, tfidf_matrix)
        cosine_similarities = np.argsort(cosine_similarities, axis=1)
        
        priorities = np.array([int(b.priority[1:]) for b in self.bugs])
        assert len(documents) == priorities.shape[0]

        related_docs_matrix = cosine_similarities.argsort()[::-1][:, :20]
        assert related_docs_matrix.shape[1] == 20

        res = priorities[related_docs_matrix]
        assert res.shape[1] == 20
        rep3 = np.mean(res, axis=1)
        rep4 = np.median(res, axis=1)

        res = res[:, :10]
        assert res.shape[1] == 10
        rep5 = np.mean(res, axis=1)
        rep6 = np.median(res, axis=1)

        res = res[:, :5]
        assert res.shape[1] == 5
        rep7 = np.mean(res, axis=1)
        rep8 = np.median(res, axis=1)

        res = res[:, :3]
        assert res.shape[1] == 3
        rep9 = np.mean(res, axis=1)
        rep10 = np.median(res, axis=1)

        res = res[:, :1]
        assert res.shape[1] == 1
        rep11 = np.mean(res, axis=1)
        rep12 = np.median(res, axis=1)

        report_factor = np.column_stack((rep3, rep4, rep5, rep6, rep7, rep8, rep9, rep10, rep11, rep12))
        assert report_factor.shape == (self.matrix.shape[0], 10)

        return report_factor

    def no_of_bugs_with_same_severity_prior(self, x, ts_col, pri_col):
        ts = x[ts_col]
        severity = x[self.vec.get_feature_names().index('bug_severity')]

        pri_feature_name = [f for f in self.vec.get_feature_names()
                            if (pri_col in f) and
                            (x[self.vec.get_feature_names().index(f)] == 1)][0]
        assert pri_feature_name is not None
        pri_feature = self.vec.get_feature_names().index(pri_feature_name)

        matching_rows = self.matrix[
            ((self.matrix[:, pri_feature] == 1) &
             (self.matrix[:, ts_col] < ts)) &
            (self.matrix[:, severity] == severity)
            ]
        return matching_rows.shape[0]

    def no_of_bugs_with_same_or_higher_severity_prior(self, x, ts_col, pri_col):
        ts = x[ts_col]
        severity = x[self.vec.get_feature_names().index('bug_severity')]

        pri_feature_name = [f for f in self.vec.get_feature_names()
                            if (pri_col in f) and
                            (x[self.vec.get_feature_names().index(f)] == 1)][0]
        assert pri_feature_name is not None
        pri_feature = self.vec.get_feature_names().index(pri_feature_name)

        matching_rows = self.matrix[
            ((self.matrix[:, pri_feature] == 1) &
             (self.matrix[:, ts_col] < ts)) &
            (self.matrix[:, severity] >= severity)
            ]
        return matching_rows.shape[0]

    def distribution_of_bugs_prior(self, x, ts_col, pri_col):
        ts = x[ts_col]
        priority_col = self.vec.get_feature_names().index('priority')

        pri_feature_name = [f for f in self.vec.get_feature_names()
                            if (pri_col in f) and
                            (x[self.vec.get_feature_names().index(f)] == 1)][0]
        assert pri_feature_name is not None
        pri_feature = self.vec.get_feature_names().index(pri_feature_name)

        matching_rows = self.matrix[
            ((self.matrix[:, pri_feature] == 1) &
             (self.matrix[:, ts_col] < ts))
            ]

        if matching_rows.shape[0] == 0:
            return np.array([0, 0, 0, 0, 0])
        assert matching_rows.shape[0] > 0

        return np.array([
            (matching_rows[:, priority_col] == 1).sum(),
            (matching_rows[:, priority_col] == 2).sum(),
            (matching_rows[:, priority_col] == 3).sum(),
            (matching_rows[:, priority_col] == 4).sum(),
            (matching_rows[:, priority_col] == 5).sum()
        ])

    def generate_product_factor(self):
        pro2 = self.apply_over('creation_ts', self.no_of_bugs_prior, 'product')
        pro2 = pro2.reshape(pro2.shape[0], 1)
        assert pro2.shape == (self.matrix.shape[0], 1)

        pro3 = self.apply_over('creation_ts', self.no_of_bugs_with_same_severity_prior, 'product')
        pro3 = pro3.reshape(pro3.shape[0], 1)
        assert pro3.shape == (self.matrix.shape[0], 1)

        pro4 = self.apply_over('creation_ts', self.no_of_bugs_with_same_or_higher_severity_prior, 'product')
        pro4 = pro4.reshape(pro4.shape[0], 1)
        assert pro4.shape == (self.matrix.shape[0], 1)

        pro5 = self.apply_over('creation_ts', self.distribution_of_bugs_prior, 'product')
        assert pro5.shape == (self.matrix.shape[0], 5)

        pro10 = self.apply_over('creation_ts', self.mean_priority_of_bugs_prior, 'product')
        assert pro10.shape == (self.matrix.shape[0],)

        pro11 = self.apply_over('creation_ts', self.median_priority_of_bugs_prior, 'product')
        assert pro11.shape == (self.matrix.shape[0],)

        # component factor
        pro12 = self.apply_over('creation_ts', self.no_of_bugs_prior, 'component')
        pro12 = pro12.reshape(pro12.shape[0], 1)
        assert pro12.shape == (self.matrix.shape[0], 1)

        pro13 = self.apply_over('creation_ts', self.no_of_bugs_with_same_severity_prior, 'component')
        pro13 = pro13.reshape(pro13.shape[0], 1)
        assert pro13.shape == (self.matrix.shape[0], 1)

        pro14 = self.apply_over('creation_ts', self.no_of_bugs_with_same_or_higher_severity_prior, 'component')
        pro14 = pro14.reshape(pro14.shape[0], 1)
        assert pro14.shape == (self.matrix.shape[0], 1)

        pro15 = self.apply_over('creation_ts', self.distribution_of_bugs_prior, 'component')
        assert pro15.shape == (self.matrix.shape[0], 5)

        pro20 = self.apply_over('creation_ts', self.mean_priority_of_bugs_prior, 'component')
        assert pro20.shape == (self.matrix.shape[0],)

        pro21 = self.apply_over('creation_ts', self.median_priority_of_bugs_prior, 'component')
        assert pro21.shape == (self.matrix.shape[0],)

        product_factor = np.column_stack((pro2, pro3, pro4, pro5, pro10, pro11))
        assert product_factor.shape == (self.matrix.shape[0], 10)
        component_factor = np.column_stack((pro12, pro13, pro14, pro15, pro20, pro21))
        assert component_factor.shape == (self.matrix.shape[0], 10)

        return np.column_stack((product_factor, component_factor))

if __name__ == '__main__':
    f = Features()
    f.read_into_memory()
    f1 = f.generate_temporal_factor()
    f2 = f.generate_author_factor()
    f3 = f.generate_report_factor()
    f4 = f.generate_product_factor()

    priority_index = f.vec.get_feature_names().index('priority')
    target = np.squeeze(f.matrix[:, priority_index])
    training = np.hstack([f.matrix[:, :priority_index], f.matrix[:, priority_index + 1:], f1, f2, f3, f4])

    sklearn.datasets.dump_svmlight_file(training, target, 'run/training.dat', zero_based=False, multilabel=False)
