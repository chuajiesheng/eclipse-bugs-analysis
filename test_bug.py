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

        long_desc_1.bug_when = datetime.datetime(2000, 10, 15, 9, 10, 10, 10)
        long_desc_2.bug_when = datetime.datetime(2000, 10, 15, 10, 10, 10, 10)

        bug.long_desc = [long_desc_1, long_desc_2]

        self.assertEqual(bug.num_of_comments(5), 1)


if __name__ == '__main__':
    unittest.main()
