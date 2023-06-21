import argparse
from pathlib import Path
from src import draw_routine
from src.io_utils import create_dir
from src.parameters import Parameters
from src.user_config import UserConfig

repo_root = Path(__file__).parent.parent.parent
CONFIG_FILE = str(repo_root / "configs" / "config_014.json")
OUTPUT_DIRECTORY = str(repo_root / "output")


"""
    This script generates an image based on a given config file. 
    The config file can be given via command line argument or via adapting 
        the default paths in this file.
    The config file is a json file that was most likely (and recommended)
        created by an earlier image generation. It can of course be created manual by hand as well 
        (although for this case the create_from_scratch script is rather recommend).  
    The image will be saved in the specified output folder 
        (also specified via command line argument or in the variables 
        at the beginning of this script) 
"""

if __name__ == '__main__':

    # Accept named command line arguments or use defaults provided at the beginning of this file
    # This means that you can use this script either via your favorite command line / terminal
    #   or via your favorite IDE (e.g. PyCharm)
    #   - just adapt (if needed) the paths either here or via command line
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f',
                        help='The (path and name of the) config json-file',
                        type=str,
                        default=CONFIG_FILE)
    parser.add_argument('--output', '-o',
                        help='The output directory for the created image',
                        type=str,
                        default=OUTPUT_DIRECTORY)
    args = parser.parse_args()

    # create the output directory if it does not exist
    create_dir(args.output)

    # Create Config Object
    # validity of json-file and output folder will be checked on creation of the Config Object
    user_config = UserConfig.load_from_file(filename=args.file, output_directory=args.output)

    # Create Parameter Object
    params = Parameters.load_from_file(args.file)

    # Adapt the margins of allowed porosities
    # Since the generation of the images uses a lot of randomness it is not untypical,
    # that the same configuration can lead to slightly different porosity results.
    # Thus, if you want to create an image with exactely this config, just increase the allowed margin.
    # This will prevent the iterative adaption of the config to match the specified porosities exactely.
    params.porosity_foam_pore_margin += 2
    params.total_porosity_margin += 2

    # Generate an image
    draw_routine.generate_image(user_config, params)
