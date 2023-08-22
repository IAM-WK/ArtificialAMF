import io
import json
import os.path
import random
from dataclasses import asdict

import cv2
import numpy as np
from matplotlib import pyplot as plt

from src.parameters import Parameters
from src.user_config import UserConfig
from src.ellipse import DARK_ELLIPSE_COLOR, BezierEllipse
from src.porosity import Porosities


def draw_random_normal_int(low: int, high: int) -> int:
    """
    Generates a randomly drawn integer,
    roughly normally distributed in the set range (low, high)
    :param low: lower range
    :param high: upper range
    :return: the drawn integer
    """
    # generate a random normal number (float)
    normal = np.random.normal(loc=0, scale=1, size=1)

    # clip to -3, 3 (where the bell with mean 0 and std 1 is very close to zero
    normal = -3 if normal < -3 else normal
    normal = 3 if normal > 3 else normal

    # scale range of 6 (-3..3) to range of low-high
    scaling_factor = (high-low) / 6
    normal_scaled = normal * scaling_factor

    # center around mean of range of low high
    normal_scaled += low + (high-low)/2

    # then round and return
    return np.round(normal_scaled)


def border_correction(img_grey):
    """
    After converting the pyplot figure to a numpy array, the image has a small black border.
    Allthough it's to small to see without zooming in, it  screws with the porosity computation.
    Thus it can be corrected using this function.
    :param img_grey:
    :return:
    """
    width = img_grey.shape[0]
    height = img_grey.shape[1]

    for xi in range(0, width):
        for yi in range(0, height):
            if img_grey[xi][yi] == 0:
                x_new = width - 2 if xi == width - 1 else xi + 1
                y_new = height - 2 if yi == height - 1 else yi + 1
                img_grey[xi][yi] = img_grey[x_new][y_new]
    return img_grey


def convert_plt_to_greyscale_array(fig):
    """
        Convert the matplotlib pyplot figure to a greyscale numpy array
        Code taken from https://stackoverflow.com/questions/7821518/matplotlib-save-plot-to-numpy-array
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    buf.close()
    img = cv2.imdecode(img_arr, 1)
    img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img_grey


def setup_figure_w_axes(parameters: Parameters):
    """
        Setup pyplot figure with desired width and height, axes and background color
    """
    fig, ax = plt.subplots(subplot_kw={'aspect': 'equal'},
                           figsize=(parameters.image_width / 100,
                                    parameters.image_height / 100),
                           frameon=False)
    ax = fig.add_axes([0., 0., 1., 1.])
    ax.set_facecolor(DARK_ELLIPSE_COLOR)
    ax.set_xlim(0, parameters.image_width)
    ax.set_ylim(0, parameters.image_height)
    return ax, fig


def generate_objects(parameters: Parameters, user_config: UserConfig):
    """
    Generate track and pore objects according to the given parameters and user config
    Does not draw the objects anywhere!
    :param
    :return: two lists containing the track objects and foam pore objects
    """
    track_objects = []
    foam_pore_objects = []

    # generate track and foam pore objects
    # span up the grid with layer-height and width parameter
    layer_width = int(np.round(user_config.layer_height * user_config.layer_width_to_layer_height_ratio))

    if not layer_width > 0:
        raise ValueError(
            'Layer width must not be zero or smaller! Check user config. Layer_width: {}'.format(layer_width))
    if not user_config.layer_height > 0:
        raise ValueError('Layer height must not be zero or smaller! Check user config! Layer_height: {}'.format(
            user_config.layer_height))

    for x in range(0, parameters.image_width, layer_width):
        for y in range(0, parameters.image_height, user_config.layer_height):

            absolute_track_width_variation = parameters.track_mean_width * parameters.track_width_variation
            generated_width = np.random.randint(
                low=(np.floor(parameters.track_mean_width - absolute_track_width_variation)),
                high=(np.ceil(parameters.track_mean_width + absolute_track_width_variation)))

            absolute_track_height_variation = parameters.track_mean_height * parameters.track_height_variation
            generated_height = np.random.randint(
                low=(np.floor(parameters.track_mean_height - absolute_track_height_variation)),
                high=(np.ceil(parameters.track_mean_height + absolute_track_height_variation)))

            randomized_x = parameters.x_offset + x + np.random.normal() * parameters.randomized_track_x_factor
            randomized_y = parameters.y_offset + y + np.random.normal() * parameters.randomized_track_y_factor

            track_pore = BezierEllipse(randomized_x, randomized_y,
                                       width=generated_width, height=generated_height)
            track_objects.append(track_pore)

            if not user_config.desired_porosities.by_foam_pores == 0:
                for i in range(0, np.random.randint(
                        low=parameters.mean_foam_pores_per_track - parameters.variation_of_foam_pores_per_track,
                        high=parameters.mean_foam_pores_per_track + parameters.variation_of_foam_pores_per_track)):
                    deviation_from_diameter = np.round(
                        parameters.mean_diameter_of_foam_pores * parameters.foam_pore_variation_of_diameter)
                    low_foam_pore = parameters.mean_diameter_of_foam_pores - deviation_from_diameter
                    high_foam_pore = parameters.mean_diameter_of_foam_pores + deviation_from_diameter

                    generated_width_foam_pore = draw_random_normal_int(low=low_foam_pore, high=high_foam_pore)
                    generated_height_foam_pore = draw_random_normal_int(low=low_foam_pore, high=high_foam_pore)

                    randomized_x_foam = parameters.x_offset + x + np.random.normal() * parameters.foam_pores_center_scaling_factor
                    randomized_y_foam = parameters.y_offset + y + np.random.normal() * parameters.foam_pores_center_scaling_factor

                    a_foam_pore = BezierEllipse(x=randomized_x_foam, y=randomized_y_foam,
                                                width=generated_width_foam_pore, height=generated_height_foam_pore,
                                                color=DARK_ELLIPSE_COLOR)
                    foam_pore_objects.append(a_foam_pore)

    return track_objects, foam_pore_objects


def save_files(img_grey_sp, parameters: Parameters, actual_porosities: Porosities, user_config: UserConfig):

    if not os.path.isdir(user_config.output_folder):
        os.mkdir(user_config.output_folder)

    # save image
    random_no = str(random.randint(1, 100)).zfill(3)
    file_name_sp = user_config.output_folder + "/" + 'img' + random_no + '_' + str(int(actual_porosities.total)) + '_' + \
                   str(int(actual_porosities.by_foam_pores)) + '.png'
    result = cv2.imwrite(file_name_sp, img_grey_sp)
    print("cv2 result", result)
    # dump json config
    # add results to conifg file
    # replace function in parameters with function name for saving of config
    parameters.porosity_function = parameters.porosity_function.__name__
    config_to_dump = {'user_config': asdict(user_config),
                      'parameters': asdict(parameters),
                      'porosity_results': asdict(actual_porosities)}
    config_file_name = user_config.output_folder + "/" + 'config_' + random_no + '.json'

    with open(config_file_name, 'w') as fp:
        json.dump(config_to_dump, fp)

    print('saved', file_name_sp, 'and', config_file_name)
    print('Porosities: total: is {:.2f}, should {:.2f}, foam pores: is {:.2f}, should {:.2f}'
          .format(actual_porosities.total, user_config.desired_porosities.total,
                  actual_porosities.by_foam_pores, user_config.desired_porosities.by_foam_pores))


