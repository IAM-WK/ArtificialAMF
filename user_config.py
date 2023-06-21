import json
from dataclasses import dataclass, fields
from pathlib import Path

from src.io_utils import print_red_terminal_message
from src.porosity import Porosities


@dataclass(frozen=True)
class UserConfig:
    # Layer height of tracks in pixels,
    # this means distance between track-centers on the y-axis (height) of the image
    layer_height: int

    # Ratio of layer (track) width to layer height, computed by (layer_width/layer_height)
    # together with layer height it spans out the (extruder) grid
    layer_width_to_layer_height_ratio: float

    # Porosity object containing the total porosity and porosity by foam pores
    desired_porosities: Porosities

    # Directory where the generated image is saved
    output_folder: str

    @classmethod
    def load_from_file(cls, filename, output_directory=None):
        """
        Creates a UserConfig Object based on the specified values in the given file.
        All needed values have to be set in the given file - will fail ugly otherwise ;-)
        :param filename: the specified json file (including path to it)
        :param output_directory: The directory where the created image will be saved.
                              If given (not None), it overrides the output_directory specified in the given config file
        :return: the UserConfig object
        """

        # check that filename is a valid file
        filename_path = Path(filename)
        if not filename_path.is_file() or filename_path.suffix != '.json':
            print_red_terminal_message("Error! The given file name " + str(filename) + " is not a valid json file!")
            raise FileNotFoundError

        # check that the output_directory is a valid directory
        if not output_directory is None:
            output_directory_path = Path(output_directory)
            if not output_directory_path.is_dir():
                print_red_terminal_message(
                    "Error! The given directory name " + str(output_directory_path) + " is not a valid directory!")
                raise NotADirectoryError

        # open file and set values
        with open(filename_path) as json_file:
            loaded_json_file = json.load(json_file)

            # check that all needed parameters are in the file
            if not 'user_config' in loaded_json_file:
                print_red_terminal_message("Error! No user_config parameter dict found in specified config file!")
                raise RuntimeError
            else:
                user_config_dict = loaded_json_file['user_config']
                needed_params = ['layer_height', 'layer_width_to_layer_height_ratio', 'output_folder', 'desired_porosities']
                for param in needed_params:
                    if not param in user_config_dict:
                        print_red_terminal_message("Error! Parameter " + param + " was not specified in specified config file!")
                        raise RuntimeError
                needed_porosity_params = ["total", "by_foam_pores"]
                for p_param in needed_porosity_params:
                    if not p_param in user_config_dict['desired_porosities']:
                        print_red_terminal_message(
                            "Error! Parameter " + param + " was not specified in desired porosities dict of specified config file")
                        raise RuntimeError

            layer_height = user_config_dict['layer_height']
            layer_width_to_layer_height_ratio = user_config_dict['layer_width_to_layer_height_ratio']

            output_directory = user_config_dict['output_folder'] if output_directory is None else output_directory
            if not output_directory[-1] == '/' or '\\':
                output_directory += '\\'

            # setup porosity object
            desired_porosities = Porosities(total=user_config_dict['desired_porosities']['total'],
                                            by_foam_pores=user_config_dict['desired_porosities']['by_foam_pores'])

            # setup UserConfig object
            user_config = UserConfig(layer_height=layer_height,
                                     layer_width_to_layer_height_ratio=layer_width_to_layer_height_ratio,
                                     output_folder=str(output_directory),
                                     desired_porosities=desired_porosities)

            print('Loaded UserConfig from ', filename)

            return user_config

    def __str__(self):
        my_string = "UserConfig: "
        for field in fields(UserConfig):
            my_string += "\n" + field.name + ": " + str(getattr(self, field.name))

        return my_string
