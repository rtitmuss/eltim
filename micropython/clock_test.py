from clock import Clock
import unittest


class TestClockMethods(unittest.TestCase):

    def test_str(self):
        self.assertEqual(str(Clock(0)), '0:00')
        self.assertEqual(str(Clock(10)), '10:00')
        self.assertEqual(str(Clock(23)), '23:00')
        self.assertEqual(str(Clock(24)), '0:00')
        self.assertEqual(str(Clock(0, 1)), '0:01')
        self.assertEqual(str(Clock(0, 0, 1)), '0:00:01')

    def test_eq(self):
        self.assertEqual(Clock(0), Clock(0))
        self.assertNotEqual(Clock(0), Clock(1))
        self.assertNotEqual(Clock(0), Clock(0, 1))
        self.assertNotEqual(Clock(0), Clock(0, 0, 1))

    def test_add(self):
        self.assertEqual(Clock(0).add(hour=1), Clock(1))
        self.assertEqual(Clock(0).add(minute=1), Clock(0, 1))
        self.assertEqual(Clock(0).add(second=1), Clock(0, 0, 1))
        self.assertEqual(Clock(0).add(minute=60), Clock(1))
        self.assertEqual(Clock(0).add(second=3600), Clock(1))

    def test_diff(self):
        self.assertEqual(Clock(0).diff(Clock(0)), Clock(0))
        self.assertEqual(Clock(0).diff(Clock(1)), Clock(1, 0))
        self.assertEqual(Clock(0, 1).diff(Clock(1)), Clock(0, 59))
        self.assertEqual(Clock(13).diff(Clock(48)), Clock(35, 0))

    def test_round_up(self):
        self.assertEqual(Clock(0).round_up(), 60 * 10)
        self.assertEqual(Clock(0, 0, 1).round_up(), (60 * 10) - 1)
        self.assertEqual(Clock(0, 1, 0).round_up(), 60 * 9)
        self.assertEqual(Clock(0, 1, 1).round_up(), (60 * 9) - 1)

        self.assertEqual(Clock(19, 40).round_up(), 60 * 10)
        self.assertEqual(Clock(19, 40, 1).round_up(), (60 * 10) - 1)
        self.assertEqual(Clock(19, 41).round_up(), 60 * 9)
        self.assertEqual(Clock(19, 41, 1).round_up(), (60 * 9) - 1)

        self.assertEqual(Clock(0).round_up(15), 60 * 15)
        self.assertEqual(Clock(0, 0, 1).round_up(15), (60 * 15) - 1)
        self.assertEqual(Clock(0, 1, 0).round_up(15), 60 * 14)
        self.assertEqual(Clock(0, 1, 1).round_up(15), (60 * 14) - 1)


if __name__ == '__main__':
    unittest.main()
