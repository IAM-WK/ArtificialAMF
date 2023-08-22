from dataclasses import dataclass, fields
from typing import Callable
import numpy as np
import json

from src.io_utils import print_red_terminal_message
from src.porosity import calculate_porosity_w_mean, Porosities, calculate_porosity_w_median_plus_1
from src.user_config import UserConfig


@dataclass()
class Parameters:
    """
    This is a data class that sets the parameters for the image synthesis.
    All parameters have reasonable default values but some parameters are adapted to the UserConfig
    (other parameters set by the user) on creation with the respective function.
    See more details to that in the adapt_to_config method
    """

    """ Image parameters """
    image_width: int = 1360   # in pixel
    image_height: int = 1024  # in pixel

    """ 
    Porosity (calculation) parameters
    The two margin parameters describe how much the calculated porosity is allowed to derieve from the desired porosity
       this has an influence on the decision in the iterative algorithm if the current image is suitable for the given
       user parameters or if a new one is generated, e.g. if the desired porosity is 30% and the margin in 1.0 then
       all images with porosity in 29..31 are ok and don't require a new iteration.
    """
    total_porosity_margin: float = 1.0      # in percent (0..100)
    porosity_foam_pore_margin: float = 2.0  # in percent (0..100)

    """ 
    The adaption of the parameters in the iterative generation of the image is also dependent of the difference in
       the foam pore porosity (between desired and actual). And based on this difference, either the amount or the size
       of the foam pores is adapted. For this distinction, a porosity threshold is needed which is this parameter.
       For more details on the influence of this parameter, check the adapt_parameters function
    """
    foam_pore_amount_adaption_threshold: float = 3.0  # in percent (0..100)

    """
    The function to calculate the porosity
       use calculate_porosity_w_median_plus_1 for calculation with the median 
    """
    porosity_function: Callable[[np.ndarray, bool], float] = calculate_porosity_w_mean

    """ 
    General Object Creation Parameters
    The offsets move the firsts track centers (and everything else in the image) away from the image borders 
    """
    x_offset: int = 25   # in pixel
    y_offset: int = 10   # in pixel

    """
    Track Parameters
    The parameters that determine the details of the track synthesis
    """
    track_mean_width: int = 50  # in pixel
    track_width_variation: float = 0.2  # in percent (0..1)
    track_mean_height: int = 40  # in pixel
    track_height_variation: float = 0.08  # in percent (0..1)

    """
    scaling factors to scale track centers around the grid intersections
    check the exact influence in the draw routine
    """
    randomized_track_x_factor: int = 5
    randomized_track_y_factor: int = 4

    """
    Foam Pore Parameters
    The parameters that determine the details of the foam pore synthesis
    """
    foam_pores_center_scaling_factor: int = track_mean_width / 3.0
    mean_diameter_of_foam_pores: int = 5  # in pixel
    mean_foam_pores_per_track: int = 8  # absolute number
    variation_of_foam_pores_per_track: int = 4  # absolute number
    foam_pore_variation_of_diameter = 0.8  # in each direction in percent

    def __post_init__(self):
        print('Initialzed Parameters')

    @classmethod
    def adapt_to_config(cls, user_config: UserConfig):
        """
        Factory method (static method that creates an object of the class)
        that creates a Parameter Object based on the given UserConfig.
        :param user_config: The UserConfig Object
        :return: The created Parameters object
        """

        params = Parameters()

        layer_width = user_config.layer_height * user_config.layer_width_to_layer_height_ratio

        # estimate approx. track and foam porosities to initialize the parameters accordingly
        amount_columns = params.image_width / layer_width
        amount_rows = params.image_height / user_config.layer_height
        volume_of_tack = layer_width * user_config.layer_height * 0.6  # account for ellipse shape and adjusted widths
        total_volume_of_tracks = amount_columns * amount_rows * volume_of_tack
        total_volume_of_image = params.image_height * params.image_width
        estimated_porosity_by_tracks = 100 - ((100 / total_volume_of_image) * total_volume_of_tracks)

        volume_of_foam_pore = params.mean_diameter_of_foam_pores * params.mean_diameter_of_foam_pores * 0.7  # account for ellipse
        total_volume_by_foam_pores = amount_rows * amount_columns * volume_of_foam_pore * params.mean_foam_pores_per_track
        estimated_porosity_by_foam_pores = (100 / total_volume_of_image) * total_volume_by_foam_pores * 0.7  # account for overlaps
        estimated_proosity_total = estimated_porosity_by_foam_pores + estimated_porosity_by_tracks * 0.9  # account for overlap

        print('I estimated these porosities to update the initial default parameters: total: {:.2f}, foam: {:.2f}'.format(estimated_proosity_total, estimated_porosity_by_foam_pores))

        # adjust parameters according to estimate
        if estimated_porosity_by_foam_pores < user_config.desired_porosities.by_foam_pores:
            # User wants more foam pore porosity, so increase size of foam pores
            params.mean_diameter_of_foam_pores += 2
            if (user_config.desired_porosities.by_foam_pores - estimated_porosity_by_foam_pores) > 5:
                # if the discrepancy is really high, increase the amount of pores and even more increase the diameter
                params.mean_foam_pores_per_track += 1
                params.mean_diameter_of_foam_pores += 2
                print('I initialized the mean diameter of foam pores with {} and the mean amount of foam pores with {}'.format(params.mean_diameter_of_foam_pores, params.mean_foam_pores_per_track))

            if estimated_proosity_total > user_config.desired_porosities.total:
                # there should be more foam pore porosity but less total porosity
                # so let's set track width and height to large values
                params.track_mean_width = np.round(layer_width * 0.99)
                params.track_mean_height = np.round(user_config.layer_height * 0.96)
            else:
                # total porosity should be fine, so let's set track width medium/small
                # to account for the decrease in total porosity by foam porosity
                params.track_mean_width = np.round(layer_width * 0.8)
                params.track_mean_height = np.round(user_config.layer_height * 0.8)
            print('I initialized the track mean width to {} and the track mean height to {}'.format(
                params.track_mean_width, params.track_mean_height))
        else:
            # user wants less foam pore porosity, so let's decrease their size
            params.mean_diameter_of_foam_pores -= 2
            if (estimated_porosity_by_foam_pores - user_config.desired_porosities.by_foam_pores) > 5:
                # if the discrepancy is really high, decrease the amount of pores
                params.mean_foam_pores_per_track -= 1
                print('I initialized the mean diameter of foam pores to {} and the mean amount of foam pores to {}'.format(
                    params.mean_diameter_of_foam_pores, params.mean_foam_pores_per_track
                ))

            if estimated_proosity_total > user_config.desired_porosities.total:
                # there should be more total porosity and we have to account that foam pore porosity will be smaller
                # so set track width and height high
                params.track_mean_width = np.round(layer_width * 0.85)
                params.track_mean_height = np.round(user_config.layer_height * 0.9)
            else:
                # there should be less total porosity and foam porosity will increase as well,
                # so set the track width and height medium
                params.track_mean_width = np.round(layer_width * 0.8)
                params.track_mean_height = np.round(user_config.layer_height * 0.8)
            print('I initialized the track mean width to {} and the track mean height to {}'.format(
                params.track_mean_width, params.track_mean_height))

        return params

    @classmethod
    def load_from_file(cls, filename):
        """
        Initializes the parameter values based on a given json file.
        :param filename: The json file (including the path to the file)
        :return: The generated parameteters object.
        """
        with open(filename) as json_file:
            parameter_file = json.load(json_file)['parameters']
            params = Parameters()

            # set porosity_function
            if parameter_file['porosity_function'] == "calculate_porosity_w_mean":
                params.porosity_function = calculate_porosity_w_mean
            elif parameter_file['porosity_function'] == "calculate_porosity_w_median":
                params.porosity_function = calculate_porosity_w_median_plus_1
            else:
                print_red_terminal_message('The given porosity function is not supported in this loading process')

            params.image_width = parameter_file['image_width']
            params.image_height = parameter_file['image_height']

            params.total_porosity_margin = parameter_file['total_porosity_margin']
            params.porosity_foam_pore_margin = parameter_file['porosity_foam_pore_margin']
            params.foam_pore_amount_adaption_threshold = parameter_file['foam_pore_amount_adaption_threshold']

            params.x_offset = parameter_file['x_offset']
            params.y_offset = parameter_file['y_offset']

            params.track_mean_width = parameter_file['track_mean_width']
            params.track_width_variation = parameter_file['track_width_variation']
            params.track_mean_height = parameter_file['track_mean_height']
            params.track_height_variation = parameter_file['track_height_variation']

            params.randomized_track_x_factor = parameter_file['randomized_track_x_factor']
            params.randomized_track_y_factor = parameter_file['randomized_track_y_factor']

            params.foam_pores_center_scaling_factor = parameter_file['foam_pores_center_scaling_factor']
            params.mean_diameter_of_foam_pores = parameter_file['mean_diameter_of_foam_pores']
            params.mean_foam_pores_per_track = parameter_file['mean_foam_pores_per_track']
            params.variation_of_foam_pores_per_track = parameter_file['variation_of_foam_pores_per_track']

            if "foam_pore_variation_of_diameter" in parameter_file:
                params.foam_pore_variation_of_diameter = parameter_file["foam_pore_variation_of_diameter"]
            else:
                params.foam_pore_variation_of_diameter = 1.0  # in each direction in percent

            print('Successfully loaded parameters from ', filename)
            return params

    def adapt_parameters(self, desired_porosities: Porosities, actual_porosities: Porosities) -> None:
        """
        Adjust the parameters with regard to the actual and desired porosities.
        Adapts some but not neccessarily all of the following parameters:
            track mean width, track mean height
            mean diameter of foam pores, mean foam pores per track
             as well as the variation of foam pores per track

        :param actual_porosities: The porosity object containing the porosities of the currently generated image
        :param desired_porosities: The porosity object containing the desired porosities, specified by the user.
        :return: nothing, update the parameter object itself.
        """

        if desired_porosities.by_foam_pores - self.porosity_foam_pore_margin < actual_porosities.by_foam_pores < desired_porosities.by_foam_pores + self.porosity_foam_pore_margin:
            # Foam pore porosity is in margin
            if np.abs(actual_porosities.total - desired_porosities.total) > 7:
                if actual_porosities.total > desired_porosities.total:
                    self.track_mean_width += 3
                    self.track_mean_height += 2
                else:
                    self.track_mean_width -= 3
                    self.track_mean_height -= 2
            elif actual_porosities.total > desired_porosities.total:
                self.track_mean_width += 1
                self.track_mean_height += 0.5
            else:
                self.track_mean_width -= 1
                self.track_mean_height -= 0.5
        else:
            if np.abs(actual_porosities.total - desired_porosities.total) > 10:
                if actual_porosities.total > desired_porosities.total:
                    self.track_mean_width += 3
                    self.track_mean_height += 2
                else:
                    self.track_mean_width -= 3
                    self.track_mean_height -= 2
            elif actual_porosities.total > desired_porosities.total:
                self.track_mean_width += 1
                self.track_mean_height += 0.5
            else:
                self.track_mean_width -= 1
                self.track_mean_height -= 0.5

        difference_in_foam_porosity = actual_porosities.by_foam_pores - desired_porosities.by_foam_pores

        if np.abs(difference_in_foam_porosity) > self.porosity_foam_pore_margin:
            # not in margin
            if difference_in_foam_porosity > 0:
                # calculated current porosity is too high -> less / smaller foam pores
                if difference_in_foam_porosity < self.foam_pore_amount_adaption_threshold and self.mean_foam_pores_per_track < 10:
                    # adapt size of pores
                    self.mean_diameter_of_foam_pores -= 1
                    if self.mean_diameter_of_foam_pores <= 0:
                        self.mean_diameter_of_foam_pores = 1
                else:
                    # adapt amount of pores
                    self.mean_foam_pores_per_track -= 1
                    if self.mean_foam_pores_per_track <= 0:
                        self.mean_foam_pores_per_track = 1
                        self.variation_of_foam_pores_per_track -= 1
                        if self.variation_of_foam_pores_per_track < 0:
                            self.variation_of_foam_pores_per_track = 0

            else:
                # calculated current porosity is too low -> lower
                if np.abs(difference_in_foam_porosity) < self.foam_pore_amount_adaption_threshold:
                    # adapt size of pores
                    self.mean_diameter_of_foam_pores += 1
                else:
                    # adapt amount of pores
                    self.mean_foam_pores_per_track += 1
        if desired_porosities.by_foam_pores == 0:
            self.mean_foam_pores_per_track = 0

        self.foam_pores_center_scaling_factor = int(np.round(self.track_mean_width/3.0))

    def __str__(self):
        my_string = "Parameters:"

        for field in fields(Parameters):
            my_string += "\n" + field.name + ": " + str(getattr(self, field.name))

        return my_string
