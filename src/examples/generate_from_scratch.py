import argparse
from pathlib import Path

from src.draw_routine import generate_image
from src.parameters import Parameters
from src.user_config import UserConfig
from src.porosity import Porosities

LAYER_HEIGHT = 40
LAYER_WIDTH_TO_LAYER_HEIGHT_RATIO = 1.25
TOTAL_POROSITY = 50
FOAM_POROSITY = 40
OUTPUT_DIRECTORY = str(Path(__file__).parent.parent.parent / "output/")

"""
    This script generates an image "from scratch", meaning without any loaded config file 
        but with the specified (and default) configs and parameters.
    You can specify the later immutable parameters of the so called UserConfig via command line / terminal 
        arguments or by adapting the variables at the beginning of this script.
    For more details parameter settings, you have to add a few easy lines of code :-). 
"""

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--layer_height', '-l',
                        help='layer height of tracks in pixels, '
                             'this means distance between track-centers on the y-axis (height) of the image',
                        type=int,
                        default=LAYER_HEIGHT)
    parser.add_argument("--ratio", "-r",
                        help="Ratio of layer width to layer height, computed by (layer_width/layer_height) "
                             "together with layer height it spans out the (extruder) grid",
                        type=float,
                        default=LAYER_WIDTH_TO_LAYER_HEIGHT_RATIO)
    parser.add_argument('--total_poro', '-t',
                        help="The desired, overall porosity in % (0..100)",
                        type=int,
                        default=TOTAL_POROSITY)
    parser.add_argument('--foam_poro', '-f',
                        help="Porosity by foam pores (in the image: small black pores within the white tracks) "
                             "in % (0..100)",
                        type=int,
                        default=FOAM_POROSITY)
    parser.add_argument('--output', '-o',
                        help='The output directory for the created imag',
                        type=str,
                        default=OUTPUT_DIRECTORY)
    args = parser.parse_args()

    # Setup (immutable) User Config with values given via command line arguments
    # or with the defaults specified at the beginning of this file
    user_config = UserConfig(
        # Layer height of tracks in pixels,
        # this means distance between track-centers on the y-axis (height) of the image
        layer_height=args.layer_height,
        # Ratio of layer width to layer height, computed by (layer_width/layer_height)
        # together with layer height it spans out the (extruder) grid
        layer_width_to_layer_height_ratio=args.ratio,
        desired_porosities=Porosities(
                           # Overall porosity in %
                           total=args.total_poro,
                           # Porosity by foam pores (in the image: small black pores) in %
                           by_foam_pores=args.foam_poro),
        # directory where image is saved
        output_folder=args.output
    )

    # Setup mutable Parameters
    # The are created and adapted to the user config to adjust e.g. the mean diameter of the small foam pores
    parameters = Parameters.adapt_to_config(user_config)
    # If you need to change some of these parameters manually, you can do this by accessing
    #   them after the object creation (but before calling the image generation method).
    #   e.g. here with: parameters.total_porosity_margin = 1.5

    # Generate the image, this is most likely an iterative process
    #   (except if your porosity margin is huge
    #   or you are a wizard and can exactly predict the parameters you need for your desired porosities).
    generate_image(user_config, parameters)
