import datetime
import unittest
from bug import Bug


class TestBug(unittest.TestCase):
    def test_within_day(self):
        date1 = datetime.datetime(2000, 10, 10, 10, 10, 10, 10)
        date2 = datetime.datetime(2000, 10, 14, 10, 10, 10, 10)
        date3 = datetime.datetime(2000, 10, 15, 9, 10, 10, 10)
        date4 = datetime.datetime(2000, 10, 15, 10, 10, 10, 10)

        self.assertEqual(Bug.within_day(date1, date2, 5), True)
        self.assertEqual(Bug.within_day(date1, date3, 5), True)
        self.assertEqual(Bug.within_day(date1, date4, 5), False)


if __name__ == '__main__':
    unittest.main()
