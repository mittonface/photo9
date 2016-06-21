# ASSIGNMENT 9
# Your Name

""" Assignment 9 - Building an HDR image

This file has a number of functions that you need to fill out in order to
complete the assignment. Please write the appropriate code, following the
instructions on which functions you may or may not use.

GENERAL RULES:
    1. DO NOT INCLUDE code that saves, shows, displays, writes the image that
    you are being passed in. Do that on your own if you need to save the images
    but the functions should NOT save the image to file. (This is a problem
    for us when grading because running 200 files results a lot of images being
    saved to file and opened in dialogs, which is not ideal). Thanks.

    2. DO NOT import any other libraries aside from the three libraries that we
    provide. You may not import anything else, you should be able to complete
    the assignment with the given libraries (and in most cases without them).

    3. DO NOT change the format of this file. Do not put functions into
    classes, or your own infrastructure. This makes grading very difficult for
    us. Please only write code in the allotted region.

"""

import cv2
import logging
import numpy as np
import os
import random

from glob import glob

def normalizeImage(img, dtype=np.uint8):
    """ This function normalizes an image from any range to 0->255.

    Note: This sounds simple, but be very careful about getting this right. I
    heavily suggest you follow the steps listed below.

    1. Set 'out' equal to 'img' subtracted by the minimum of the image. For
    example, if your image range is from 10->20, subtracting the minimum will
    make the range from 0->10. The benefit of this is that if the range is from
    -10 to 10, it will set the range to be from 0->20. Since we will have to
    deal with negative values, it is important you normalize the function this
    way. We do the rounding for you so do not do any casting or rounding for
    the input values (a value like 163.92 will be cast to 163 by the return
    statement that casts everything to a uint8).

    2. Now, multiply 'out' by (255 / max) where max is the max value of 'out'.
    This max is computed after you subtract the minimum (not before).

    3. return 'out'.

    Args:
        img (numpy.ndarray): A grayscale or color image represented in a numpy
                             array. (dtype = np.float)

        dtype (numpy.dtype): (Optional) The type parameter for casting the
                             output array.

    Returns:
        out (numpy.ndarray): A grasycale or color image of dtype uint8, with
                             the shape of img, but values ranging from 0->255.
    """
    out = np.array(img.shape)
    # WRITE YOUR CODE HERE.

    # END OF FUNCTION.
    return out.astype(dtype)


def linearWeight(pixel_value, pixel_range_max=255):
    """ Linear Weighting function based on pixel location.

    1. The weighting function is a triangle; it should return
    the smaller of the two values between the current pixel
    value or pixel_range_max - pixel_value

    Args:
        pixel_value (np.uint8): A value from 0 to 255.

        pixel_range_max (np.int): (Optional) The maximum value of the image
                                  color channel depth (255 for uint8)

    Returns:
        weight: (np.float64) A value from 0.0 to pixel_range_max

    """
    pixel_range_min = 0.0
    pixel_range_mid = 0.5 * (pixel_range_min + pixel_range_max)
    weight = 0.0

    # WRITE YOUR CODE HERE.

    # END OF FUNCTION.
    return np.float64(weight)


def sampleIntensities(images, num_points):
    """ Draw samples of pixel intensity at the same location for all
    images in the exposure stack.

    The returned intensity_values is an array with one row for every possible 
    pixel value, and one column for each image in the exposure stack. The
    values in the array are filled according to the instructions below.
    The middle image of the exposure stack is used to search for
    candidate locations because it is expected to be the least likely
    image where pixels will be over- or under-exposed.

    For each possible pixel intensity level:

        1. Find the location of all pixels in the middle image that
        have the current target intensity

            a. If there are no pixels with the target intensity,
            do nothing

            b. Otherwise, use a uniform distribution to select a
            location from the candidate pixels then, set the
            current row of intensity_values to the pixel intensity
            of each image at the chosen location.

    NOTE(1): Recall that array coordinates (row, column) are in the opposite
    order of the Cartesian coordinates (x, y) we are all used to.

    Args:
        images (list): A list containing a stack of single-channel layers
                       of an HDR exposure stack

        num_points (int): The upper bound on the number of intensity values
                          to sample from the image stack (lower bound is
                          implicitly zero)

    Returns:
        intensity_values (numpy.array): An array containing a uniformly
                                        sampled intensity value from each
                                        exposure layer (should have size
                                        num_points x num_images)

    """

    num_images = len(images)
    intensity_values = np.zeros((num_points, num_images), dtype=np.uint8)

    # Choose middle image for YX locations.
    mid = np.round(num_images / 2)
    mid_img = images[mid]

    # WRITE YOUR CODE HERE.

    # END OF FUNCTION.
    return intensity_values


def computeResponseCurve(intensity_samples, log_exposures, smoothing_lambda,
                         weighting_function, intensity_range=255):
    """ Find camera response curve for one color channel.

    The response curve is obtained by finding the least-squares solution
    to an overdetermined set of constraint equations (i.e., solve for x
    in Ax=b).

    The first step is to fill in mat_A and mat_b with the constraints
    described in section 2.1 of the research paper, "Recovering High Dynamic
    Range Radiance Maps from Photographs" by Debevec & Malik (available in
    the course resources materail on T-Square). We recommend that you break
    the process up into three steps: filling in data-fitting constraints,
    filling in smoothing constraints, and adding the color curve adjustment
    constraint. The steps required are described in detail below.

    PART 1: Constraints

        In this part, you will fill in mat_A and mat_b with values from the
        weighting function. Each row of mat_A is a constraint equation for
        the response curve.

        WHAT TO DO?
        1a. Data-Fitting Constraints

            Data-fitting constraints correspond to observed intensity values
            in the image stack - these constraints ensure that the response
            curve should correctly predicts the observed data.

            For each row i and column j in the intensity_samples array:

                i.   Set mat_A at the (idx_ctr, pixel_value) to the value
                     of the weighting function (wij)
                ii.  Set mat_A at the (idx_ctr, pix_range + i) to the
                     negative value of the weighting function (-wij)
                iii. Set mat_b at (idx_ctr, 0) to the product of the value
                     of the weighting function and the log of exposure j
                     (wij * log_exposure[j])

                     *  pixel_value is the value in intensity_samples at i, j
                     ** idx_ctr should start at zero, and should increase
                        by 1 each time the inner loop executes
                     *** wij is the value of the weighting function for the 
                         pixel intensity value at (i,j)  
                         (wij = weighting_function(intensity_samples[i, j])

        1b. Smoothing Constraints

            Smoothing constraints ensure that the response curve is smooth
            by restricting (penalizing) changes in the second derivative of
            the function. The constraints in this section are all equations
            that equal zero, so there is no need to set any values in mat_b.

            For each value idx in the range (1...intensity_range - 1):

                i.   Set mat_A at (offset + idx - 1, idx - 1) to the product
                     of the smoothing lambda parameter and the value of the
                     weighting function for idx.
                     (smoothing_lambda * weighting_function(idx))
                ii.  Set mat_A at (offset + idx - 1, idx) to -2 times the
                     product of the smoothing lambda parameter and the value
                     of the weighting function for idx.
                     (-2 * smoothing_lambda * weighting_function(idx))
                iii. Set mat_A at (offset + idx - 1, idx + 1) to the product
                     of the smoothing lambda parameter and the value of the
                     weighting function for idx.
                     (smoothing_lambda * weighting_function(idx))

        1c. Color curve constraint

            This constraint corresponds to the assumption that middle value
            pixels have unit exposure. This constraint is an equation that
            is equal to zero, so there is no need to set any values in mat_b.

            Set the value of mat_A in the last row and middle column
            (mat_A.shape[0], intensity_range / 2) to the constant 1.


    PART 2: Solving the system

        In this part we do some simple linear algebra. We are solving the
        function Ax=b. We want to solve for x. We have A and b.

        Ax = b.
        A^-1 * A * x = b.   (Note: the * multiply is the dot product here, but
                             in Python it performs an element-wise
                             multiplication so don't use it). What we want is
                             something like: my_mat.dot(other_mat)
        x = A^-1 * b.

        Pretty simple: x is the inverse of A dot b. Now, it gets a little bit
        more difficult because we can't obtain the inverse of a matrix that is
        not square (there are more constraint equations than unknown variables
        because the system is overdetermined). We can however use a different
        method to find the least-squares fit.

        This method is called the Moore-Penrose Pseudoinverse of a Matrix.

        WHAT TO DO?
        1a. Get the pseudoinverse of A. Numpy has an implementation of the
            Moore-Penrose Pseudoinverse, so this is just a function call.

        1b. Multiply that psuedoinverse -- dot -- b. This becomes x. Make sure
            x is of the size 512 x 1.

    Note(1): For those of you unfamiliar with Python and getting to learn it
    this semester, this will have something "weird". weighting_function is not
    a value, but rather a function. This means we pass in the name of a
    function and then within the computeResponseCurve function you can use it
    to compute the weight (so you can do weighting_function(10) and it will
    return a value for the weight). Feel free to ask questions on Piazza if
    the concept doesn't click in.

    Args:
        intensity_samples (numpy.ndarray): Stack of single channel input values
                                           (num_samples x num_images)

        log_exposures (numpy.ndarray): Log exposure times (size == num_images)

        smoothing_lambda (numpy.int): The smoothness constant.

        weighting_function: (Callable) Function that computes the weights.

        intensity_range (int): The differece between the maximum possible pixel
                               intensity value and the minimum possible pixel
                               intensity value (i.e., 255 for uint8 images)

    Returns:
        g(numpy.ndarray): log exposure corresponding to pixel value z
                          (num_samples x 1)

    """
    # We sample all intensities, otherwise intensity range would be the
    # difference between the biggest and smallest possible pixel values
    num_samples = intensity_samples.shape[0]
    num_images = len(log_exposures)
    offset = num_samples * num_images

    # NxP + [(Zmax-1) - (Zmin + 1)] + 1 constraints; N + 256 columns
    mat_A = np.zeros((num_images * num_samples + intensity_range,
                      num_samples + intensity_range + 1), dtype=np.float64)
    mat_b = np.zeros((mat_A.shape[0], 1), dtype=np.float64)

    # PART 1a: WRITE YOUR CODE HERE
    # Create data-fitting constraints

    # PART 1b: WRITE YOUR CODE HERE
    # Apply smoothing constraints throughout the pixel range

    # PART 1c: WRITE YOUR CODE HERE
    # Adjust color curve by adding a constraint for the middle pixel value

    # PART 2: WRITE YOUR CODE HERE
    # Solve the system using x = A^-1 * b

    # STOP WRITING CODE HERE.

    # Assuming that you set up your equation so that the first elements of
    # x correspond to g(z); otherwise change to match your constraints
    g = x[0:intensity_range + 1]

    return g[:, 0]


def computeRadianceMap(images, log_exposure_times, response_curve,
                       weighting_function, min_pixel=0.0, max_pixel=255.0):
    """ Use the response curve to calculate the radiance map for each pixel
    in the current color layer

    Once you have the response curve, you can use it to recover the radiance
    of each pixel in the scene. The process is described below:

    1. Initialize every pixel of the output layer to 0.0

    2. For each location i, j in the image:

        a. Get the pixel value from each image in the exposure stack at
           the current location (i, j)

        b. Calculate the weight of pixel[i][j] in each image from the
           exposure stack using the weighting_function

        c. Calculate the sum of all weights at (i, j)

        d. If the sum of the weights is > 0.0, set the value of the output
           array at location (i, j) equal to the weighted sum of the
           difference between the response curve evaluated for the pixel
           value from each image in the exposure stack and the log of the
           exposure time for that image, divided by the sum of the weights
           for the current location

           output[i][j] =
           sum(response_curve[pixel_vals] - log_exposure_times) / sum_weights

    Args:
        images (list): list containing a single color layer from each image in
                       exposure stack. (size == num_images)

        log_exposure_times (numpy.ndarray): Log exposure times.
                                            (size == num_images)

        response_curve (numpy.ndarray): Least-squares fitted log exposure
                                        corresponding to pixel value z.

        weighting_function (callable): Function that computes the weights.

        min_pixel (np.int): (Optional) Minimum pixel value for all images.

        max_pixel (np.int): (Optional) Maximum pixel value for all images.

    Returns:

        img_rad_map (numpy.ndarray): The (log) radiance map.


    """
    img_shape = images[0].shape
    img_rad_map = np.ones(img_shape, dtype=np.float64)

    # WRITE YOUR CODE HERE

    # STOP WRITING CODE HERE.
    return img_rad_map


def computeHDR(images, log_exposure_times, pixel_range_max=255.0,
               smoothing_lambda=100):
    """ This function does the actual HDR computation.

    Note: This brings together all of the functions above. Don't modify this.

    The basic overview is to do the following for each channel:

    1. Sample pixel intensities from random locations through the image stack
    2. Compute response curves (Note: We pass in the weight function here)
    3. Build image radiance map from response curves.
    4. Apply tone mapping to fit the high dynamic range values into a limited
       range for a specific print or display medium (Note: we don't do this
       part - but you're free to experiment.)

    Args:
        images (list): A list of images (numpy.ndarray)

        log_exposure_times (numpy.ndarray): The log exposure times.

        pixel_range_max (float): The highest value that a single pixel can
                                 contain for the bit depth of the image.
                                 (Default 255.0 for uint8 images.)

        smoothing_lambda (np.int): (Optional) A constant lambda value.

    Returns:
        hdr_image(numpy.ndarray): The HDR image.

    """
    num_points = int(pixel_range_max + 1)
    num_channels = images[0].shape[2]

    hdr_image = np.zeros(images[0].shape, dtype=np.float64)

    for channel in range(num_channels):

        # collect the current layer of each input image
        layer_stack = [img[:, :, channel] for img in images]

        # Sample image intensities
        intensity_samples = sampleIntensities(layer_stack, num_points)

        # Compute Response Curves
        response_curve = computeResponseCurve(intensity_samples,
                                              log_exposure_times,
                                              smoothing_lambda,
                                              linearWeight)

        # Build radiance maps
        img_rad_map = computeRadianceMap(layer_stack,
                                         log_exposure_times,
                                         response_curve,
                                         linearWeight)

        # Compose HDR image
        hdr_image[..., channel] = img_rad_map

    # We don't do tone mapping, but here is where it would happen. Some
    # methods work on each layer, others work on the whole image at once;
    # feel free to experiment.
    output = np.zeros(hdr_image.shape, dtype=np.uint8)
    for i in range(3):
        output[..., i] = normalizeImage(hdr_image[..., i])

    return output


def readImages(image_dir, ext_list=[], resize=False):
    """ This function reads in input images from a image directory

    Note: This is implemented for you since its not really relevant to
    computational photography (+ time constraints).

    Args:
        image_dir (str): The image directory to get images from.

        ext_list (list): (Optional) List of additional image file extensions
                         to read from the input folder. (The function always
                         returns images with extensions: bmp, jpeg, jpg, png,
                         tif, tiff)

        resize (bool): (Optional) If True, downsample the images by 1/4th.

    Returns:
        images(list): List of images in image_dir. Each image in the list is of
                      type numpy.ndarray.

    """
    # The main file extensions. Feel free to add more if you want to test an
    # image format of yours that is not listed (Make sure OpenCV can read it).
    extensions = ["bmp", "jpeg", "jpg", "png", "tif", "tiff"] + ext_list
    search_paths = [os.path.join(image_dir, '*.' + ext) for ext in extensions]
    image_files = reduce(list.__add__, map(glob, search_paths))
    images = [cv2.imread(f, cv2.IMREAD_UNCHANGED | cv2.IMREAD_COLOR)
              for f in image_files]

    if resize:
        images = [img[::4, ::4] for img in images]

    return images


if __name__ == "__main__":
    # Test code to run the function.
    np.random.seed()
    image_dir = "input"
    images = readImages(image_dir, resize=False)
    exposure_times = np.float64([1 / 160.0, 1 / 125.0, 1 / 80.0,
                                 1 / 60.0, 1 / 40.0, 1 / 15.0])
    log_exposure_times = np.log(exposure_times)
    hdr = computeHDR(images, log_exposure_times)
    cv2.imwrite("hdr.jpg", hdr)
