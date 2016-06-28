import unittest
import numpy as np
from assignment9 import *

class TestAssignment9(unittest.TestCase):

    def test_normalize(self):
        a1 = np.asarray([[-10, 12, 122],
                         [100, 256, 100],
                         [-3, 32, 32]])

        test_array = np.asarray([[0, 21, 126],
                                [105, 255, 105],
                                [6, 40, 40]])

        self.assertTrue(np.array_equal(normalizeImage(a1), test_array))

    def test_sample_intensities(self):

        a1 = np.asarray([[-10, 12, 122],
                         [100, 256, 100],
                         [-3, 32, 32]])

        a2 = np.asarray([[32, 31, 32],
                        [82, 182, 89],
                        [23, 182, 182]])

        a3 = np.asarray([[32, 31, 32],
                        [82, 42, 89],
                        [23, 132, 182]])

        print sampleIntensities([a1, a2, a3])
        self.assertFalse(True)

        pass


if __name__ == '__main__':
    unittest.main()
