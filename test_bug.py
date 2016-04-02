import datetime
import unittest
from bug import Bug
from feature_extraction import Features
from sklearn.feature_extraction import DictVectorizer
import numpy as np
import code


class TestBug(unittest.TestCase):

    def test_bugs_reported_prior(self):
        objs = [{'creation_ts': 86400, 'something': 1}, # t+1
                {'creation_ts': (2 * 86400) - 1, 'something': 1}, # t+1
                {'creation_ts': 2 * 86400, 'something': 1}, # t+2
                {'creation_ts': 3 * 86400, 'something': 1}] # t+3

        f = Features()
        f.vec = DictVectorizer()
        f.matrix = f.vec.fit_transform(objs).toarray()

        res = f.bugs_within(f.bugs_between, 1)
        expected = np.array([0, 1, 1, 0])
        self.assertTrue((res == expected).all())

if __name__ == '__main__':
    unittest.main()
