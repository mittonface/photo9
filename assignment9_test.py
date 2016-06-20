import sys
import numpy as np
import cv2

import assignment9

def test_normalizeImage():
    """ This script will robustly test the normalizeImage function.
    """
    matrix = np.array([[  0,   0],
                       [128, 128]], dtype=np.float)
    ans = np.array([[  0,   0],
                    [255, 255]], dtype=np.uint8)
    solution = assignment9.normalizeImage(matrix)

    type_and_shape_test(solution, ans, "normalizeImage")

    return True


def test_linearWeight():
    """ This script will perform a unit test on the linear weight function.
    """

    test_input = 127
    print "Evaluating linearWeight."

    weight = assignment9.linearWeight(test_input)
    if type(weight) != np.float64:
        raise ValueError(
            ("Error - weight has type {}." +
             " Expected type is {}.").format(type(weight), np.float64))

    print "type test passed for linearWeight.\n"
    return True


def test_sampleIntensities():
    """ This script will perform a unit test on the sample intensities function.
    """

    num_points = 256
    layer = np.arange(num_points, dtype=np.uint8).reshape(16, 16)
    images = [layer, layer]
    solution = assignment9.sampleIntensities(images, num_points)
    ans = np.zeros((num_points, 2), dtype=np.uint8)

    type_and_shape_test(solution, ans, "sampleIntensities")

    return True


def test_computeResponseCurve():

    num_points = 256
    img = np.arange(num_points * 2, dtype=np.uint8)
    np.random.shuffle(img)
    pixels = img.reshape(256, 2)
    exposures = np.log(np.float64([1 / 160.0, 1 / 80.0]))
    solution = assignment9.computeResponseCurve(pixels, exposures, 100,
                                                lambda x: 1,
                                                intensity_range=255)
    ans = np.zeros((256), dtype=np.float64)

    type_and_shape_test(solution, ans, "computeResponseCurve")

    return True


def test_computeRadianceMap():

    num_points = 256
    img1 = np.arange(num_points, dtype=np.uint8)
    np.random.shuffle(img1)
    img2 = np.arange(num_points, dtype=np.uint8)
    np.random.shuffle(img2)
    images = [img1.reshape(16, 16), img2.reshape(16, 16)]
    exposures = np.log(np.float64([1 / 160.0, 1 / 80.0]))
    response = np.ones(img1.shape, dtype=np.float64)
    solution = assignment9.computeRadianceMap(images, exposures, response,
                                  lambda x: 1, max_pixel=255)
    ans = np.zeros((16,16), dtype=np.float64)

    type_and_shape_test(solution, ans, "computeRadianceMap")

    return True


def type_and_shape_test(solution, ans, function_name):

    print "Evaluating {}.".format(function_name)

    # Test for type
    if type(solution) is not type(ans):
      raise ValueError("Error - {} output type is {}. " +
                  "Expected type is {}.").format(function_name,
                                                 type(solution),
                                                 type(ans))
    # Test for shape
    if solution.shape != ans.shape:
      raise ValueError(("Error - {} output shape is {}. " +
                     "Expected shape is {}.").format(function_name,
                                                     solution.shape,
                                                     ans.shape))

    # Test for type of values in matrix
    if solution.dtype.type is not ans.dtype.type:
      raise ValueError(("Error - {} output values have type {}. " +
                  "Expected type is {}.").format(function_name,
                                                 solution.dtype.type,
                                                 ans.dtype.type))

    print "type_and_shape_test passed for {}.\n".format(function_name)

if __name__ == "__main__":
    print "Performing unit test.\n"
    if not test_normalizeImage():
        print "normalizeImage function failed. Halting testing."
        sys.exit()
    if not test_linearWeight():
        print "linearWeight function failed. Halting testing."
        sys.exit()
    if not test_sampleIntensities():
        print "sampleIntensities function. Halting testing."
        sys.exit()
    if not test_computeResponseCurve():
        print "computeResponseCurve function failed. Halting testing."
        sys.exit()
    if not test_computeRadianceMap():
        print "ccomputeRadianceMap function failed. Halting testing."
        sys.exit()

    print "Unit tests passed."
    print "Generating HDR from sample images. (This may take a while.)"

    image_dir = "input"
    output_dir = "output"
    exposure_times = np.float64([1/160.0, 1/125.0, 1/80.0, 1/60.0, 1/40.0,
                                 1/15.0])
    log_exposure_times = np.log(exposure_times)

    np.random.seed()
    small_images = assignment9.readImages(image_dir)
    hdr = assignment9.computeHDR(small_images, log_exposure_times)
    print u"Expected avg pixel value for the test images is 125\u00B1" + u"1.",
    print "Your value was {}.".format(int(np.average(hdr)))
    if not (124 <= int(np.average(hdr)) <= 126):
        print "Please check your code for errors and inspect your output."
    cv2.imwrite(output_dir + "/hdr.jpg", hdr)
