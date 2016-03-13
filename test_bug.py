import datetime
import unittest
from bug import Bug
from long_desc import LongDesc


class TestBug(unittest.TestCase):
    def test_within_day(self):
        date1 = datetime.datetime(2000, 10, 10, 10, 10, 10, 10)
        date2 = datetime.datetime(2000, 10, 14, 10, 10, 10, 10)
        date3 = datetime.datetime(2000, 10, 15, 9, 10, 10, 10)
        date4 = datetime.datetime(2000, 10, 15, 10, 10, 10, 10)

        self.assertEqual(Bug.within_day(date1, date2, 5), True)
        self.assertEqual(Bug.within_day(date1, date3, 5), True)
        self.assertEqual(Bug.within_day(date1, date4, 5), False)

    def test_num_of_comments(self):
        bug = Bug(None)
        bug.creation_ts = datetime.datetime(2000, 10, 10, 10, 10, 10, 10)
        long_desc_1 = LongDesc(None)
        long_desc_2 = LongDesc(None)

        long_desc_1.bug_when = str(datetime.datetime(2000, 10, 15, 9, 10, 10, 10))
        long_desc_2.bug_when = str(datetime.datetime(2000, 10, 15, 10, 10, 10, 10))

        bug.long_desc = [long_desc_1, long_desc_2]

        self.assertEqual(bug.num_of_comments(5), 1)

    def test_num_of_bugs(self):
        date1 = datetime.datetime(2000, 10, 10, 10, 10, 10, 10)
        date2 = datetime.datetime(2000, 10, 14, 10, 10, 10, 10)
        date3 = datetime.datetime(2000, 10, 15, 9, 10, 10, 10)
        date4 = datetime.datetime(2000, 10, 15, 10, 10, 10, 10)

        bug_severity_list = [('S1', date1), ('S1', date2), ('S2', date3), ('S1', date4)]

        bug = Bug(None)
        bug.creation_ts = datetime.datetime(2000, 10, 10, 10, 10, 10, 10)

        self.assertEqual(bug.num_of_bugs(bug_severity_list, 5), 3)

    def test_num_of_bugs_with_severity(self):
        date1 = datetime.datetime(2000, 10, 10, 10, 10, 10, 10)
        date2 = datetime.datetime(2000, 10, 14, 10, 10, 10, 10)
        date3 = datetime.datetime(2000, 10, 15, 9, 10, 10, 10)
        date4 = datetime.datetime(2000, 10, 15, 10, 10, 10, 10)

        bug_severity_list = [('S1', date1), ('S1', date2), ('S2', date3), ('S1', date4)]

        bug = Bug(None)
        bug.bug_severity = 'S1'
        bug.creation_ts = datetime.datetime(2000, 10, 10, 10, 10, 10, 10)

        self.assertEqual(bug.num_of_bugs_with_severity(bug_severity_list, 5), 2)

    def test_same_or_higher_severity(self):
        bug = Bug(None)

        bug.bug_severity = None
        self.assertEqual(bug.same_or_higher_severity(), Bug.SEVERITY_LIST)

        bug.bug_severity = 'something random'
        self.assertEqual(bug.same_or_higher_severity(), Bug.SEVERITY_LIST)

        bug.bug_severity = 'normal'
        self.assertEqual(bug.same_or_higher_severity(), ['normal', 'major', 'critical', 'blocker'])

    def test_num_of_bugs_with_same_or_higher_severity(self):
        date1 = datetime.datetime(2000, 10, 10, 10, 10, 10, 10)
        date2 = datetime.datetime(2000, 10, 14, 10, 10, 10, 10)
        date3 = datetime.datetime(2000, 10, 15, 9, 10, 10, 10)
        date4 = datetime.datetime(2000, 10, 15, 10, 10, 10, 10)

        bug_severity_list = [('normal', date1), ('major', date2), ('blocker', date3), ('normal', date4), ('major', date4)]

        bug = Bug(None)
        bug.bug_severity = 'major'
        bug.creation_ts = datetime.datetime(2000, 10, 10, 10, 10, 10, 10)

        self.assertEqual(bug.num_of_bugs_with_same_or_higher_severity(bug_severity_list, 5), 2)

    def test_priority_of_author(self):
        bug = Bug(None)
        bug.reporter = 'someone'
        self.assertEqual(bug.priority_of_author(dict()), 0)

        author_list = dict()
        author_list[bug.reporter] = 10
        self.assertEqual(bug.priority_of_author(author_list), 10)


if __name__ == '__main__':
    unittest.main()
