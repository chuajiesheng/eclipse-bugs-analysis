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

    def test_bugs_by_author(self):
        bug1 = Bug(None)
        bug1.bug_id = '1'
        bug1.reporter = 'someone'
        bug2 = Bug(None)
        bug2.bug_id = '2'
        bug2.reporter = 'someone'
        bug3 = Bug(None)
        bug3.bug_id = '3'
        bug3.reporter = 'someone'

        bug4 = Bug(None)
        bug4.bug_id = '4'
        bug4.reporter = 'someone else'

        all_bugs = [Bug(None), bug1, bug2, bug3, bug4]
        self.assertEqual(bug1.bugs_reported_by_author(all_bugs, include_source_bug=True), [bug1, bug2, bug3])
        self.assertEqual(bug1.bugs_reported_by_author(all_bugs, include_source_bug=False), [bug2, bug3])

    def test_mean_priority_of_author(self):
        bug1 = Bug(None)
        bug1.bug_id = '1'
        bug1.priority = 'P1'
        bug1.reporter = 'someone'
        bug2 = Bug(None)
        bug2.bug_id = '2'
        bug2.priority = 'P2'
        bug2.reporter = 'someone'
        bug3 = Bug(None)
        bug3.bug_id = '3'
        bug3.priority = 'P3'
        bug3.reporter = 'someone'

        bug4 = Bug(None)
        bug4.bug_id = '4'
        bug4.priority = 'P4'
        bug4.reporter = 'someone else'

        all_bugs = [Bug(None), bug1, bug2, bug3, bug4]
        self.assertEqual(bug1.mean_priority_of_author(all_bugs), 2.0)

    def test_median_priority_of_author(self):
        bug1 = Bug(None)
        bug1.bug_id = '1'
        bug1.priority = 'P1'
        bug1.reporter = 'someone'
        bug2 = Bug(None)
        bug2.bug_id = '2'
        bug2.priority = 'P2'
        bug2.reporter = 'someone'
        bug3 = Bug(None)
        bug3.bug_id = '3'
        bug3.priority = 'P3'
        bug3.reporter = 'someone'

        bug4 = Bug(None)
        bug4.bug_id = '4'
        bug4.priority = 'P4'
        bug4.reporter = 'someone else'

        all_bugs = [Bug(None), bug1, bug2, bug3, bug4]
        self.assertEqual(bug1.median_priority_of_author(all_bugs), 2.0)

        self.assertEqual(bug1.median_priority_of_author([bug1]), 1.0)
        self.assertEqual(bug1.median_priority_of_author([]), 0.0)

    def test_bugs_reported_prior(self):
        now = datetime.datetime.now()
        one_hour_before = now.replace(hour=now.hour - 1)
        one_hour_after = now.replace(hour=now.hour + 1)

        bug1 = Bug(None)
        bug1.bug_id = '1'
        bug1.priority = 'P1'
        bug1.creation_ts = one_hour_before
        bug1.reporter = 'someone'
        bug2 = Bug(None)
        bug2.bug_id = '2'
        bug2.creation_ts = one_hour_before
        bug2.priority = 'P2'
        bug2.reporter = 'someone'
        bug3 = Bug(None)
        bug3.bug_id = '3'
        bug3.priority = 'P3'
        bug3.reporter = 'someone'
        bug3.creation_ts = one_hour_after

        bug4 = Bug(None)
        bug4.bug_id = '4'
        bug4.priority = 'P4'
        bug4.reporter = 'someone else'
        bug4.creation_ts = one_hour_before

        all_bugs = [Bug(None), bug1, bug2, bug3, bug4]
        self.assertEqual(bug3.bugs_reported_prior(all_bugs), [bug1, bug2])

if __name__ == '__main__':
    unittest.main()
