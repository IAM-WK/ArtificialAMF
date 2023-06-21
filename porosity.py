from dataclasses import dataclass, fields

import numpy as np

"""
This class contains the porosity (container-)class and different functions to calculate the porosity 
"""

@dataclass()
class Porosities:
    """
        This is basically just a data container
    """
    total: float
    by_foam_pores: float
    by_tracks: float = None

    def __str__(self):
        my_string = "Porosities: "
        for field in fields(Porosities):
            my_string += "\t" + (field.name + ": " + str(getattr(self, field.name)))
        return my_string


def calculate_porostiy(pixel_below_threshold, flat_grayscale_image, verbose=False):
    all_pixel = flat_grayscale_image.size
    percentage_below_threshold = 100 / all_pixel * pixel_below_threshold
    if verbose:
        print('Absolute: \t below threshold {:,} \t total: {:,} \nRelative: \t below threshold {:.2f}% (POROSITY)'.format(pixel_below_threshold, all_pixel, percentage_below_threshold))
    return percentage_below_threshold


def calculate_porosity_w_mean(flat_grayscale_image, verbose=False):
    mean = np.mean(flat_grayscale_image)
    return calculate_porosity_w_threshold(flat_grayscale_image, threshold=mean, verbose=verbose)


def calculate_porosity_w_mean_flatten(grayscale_image, dummy_param=0, verbose=False):
    flat_grayscale_image = grayscale_image.flatten()
    mean = np.mean(flat_grayscale_image)
    return calculate_porosity_w_threshold(flat_grayscale_image, threshold=mean, verbose=verbose)


def calculate_porosity_w_threshold(flat_grayscale_image, threshold=200, verbose=False) -> float:
    # white is high, black is low

    pixel_below_threshold = np.where(flat_grayscale_image < threshold)[0].size
    return calculate_porostiy(pixel_below_threshold, flat_grayscale_image, verbose)


def calculate_porosity_w_median_plus_1(flat_grayscale_image, verbose=False):
    median = np.median(flat_grayscale_image)
    return calculate_porosity_w_threshold(flat_grayscale_image, threshold=median + 1, verbose=verbose)


def calculate_porosity_w_median_plus_1_flatten(grayscale_image, dummy_param=0, verbose=False):
    flat_grayscale_image = grayscale_image.flatten()
    median = np.median(flat_grayscale_image)
    return calculate_porosity_w_threshold(flat_grayscale_image, threshold=median + 1, verbose=verbose)


def porosity_in_margin(desired_porosity: float, actual_porosity: float, porosity_margin: float) -> bool:
    """
    Check if porosity is in desired porosity margin
    :param desired_porosity: The set, desired porosity
    :param actual_porosity:  The currently measured, calculated porosity
    :param porosity_margin:  The margin in each direction
    :return: If porosity is in that margin or not.
    """
    return desired_porosity + porosity_margin \
           >= actual_porosity >= desired_porosity - porosity_margin