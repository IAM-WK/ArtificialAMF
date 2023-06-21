from matplotlib import pyplot as plt

from src.parameters import Parameters
from src.user_config import UserConfig
from src.porosity import Porosities, porosity_in_margin
from src.utils import convert_plt_to_greyscale_array, border_correction, setup_figure_w_axes, \
    generate_objects, \
    save_files

"""
    This is the main routine to calculate an artificial image of foam porosities.
    The main config with the most impacting parameters can be set and found in the main methods.
    For smaller adjustments, check out the parameters in PARAMETERS in file parameters.
    
    This routine will calculate images iteratively until the desired porosity values are matched 
    and only save the last, matching image as png and the according configuration file as jpg.
"""


def generate_image(user_config: UserConfig, parameters: Parameters, save=True):

    actual_porosities = Porosities(0.0, 0.0)  # initialize Porosities Object

    while (True):

        # setup pyplot
        ax, fig = setup_figure_w_axes(parameters)

        # generate tracks (white in image) and foam pores (black small images within tracks)
        track_objects, foam_pore_objects = generate_objects(parameters, user_config)

        # plot tracks
        for track in track_objects:
            ax.add_patch(track.retrieve_patch())

        # convert to numpy array
        img_grey = convert_plt_to_greyscale_array(fig)

        # border correction because matplotlib creates a black (0) border around the image
        img_grey = border_correction(img_grey)
        # file_name = 'my_image_now' + str(np.random.randint(1, 100))
        # cv2.imwrite(file_name + '_t.png', img_grey)

        # calculate porosity of tracks
        actual_porosities.by_tracks = parameters.porosity_function(img_grey.flatten(), False)

        # add foam pores to image
        for pore in foam_pore_objects:
            ax.add_artist(pore.retrieve_patch())

        # convert to numpy array
        img_grey_sp = convert_plt_to_greyscale_array(fig)
        # cv2.imwrite(file_name + '_f.png', img_grey_sp)

        # border correction because matplotlib creates a black (0) border around the image
        img_grey_sp = border_correction(img_grey_sp)

        # calculate total porosity and porosity by foam pores
        actual_porosities.total = parameters.porosity_function(img_grey_sp.flatten(), False)
        actual_porosities.by_foam_pores = actual_porosities.total - actual_porosities.by_tracks

        # check if computed porosity is close enough to desired porosity
        porosity_total_in_margin = porosity_in_margin(user_config.desired_porosities.total,
                                                      actual_porosities.total,
                                                      parameters.total_porosity_margin)
        porosity_foam_pores_in_margin = porosity_in_margin(user_config.desired_porosities.by_foam_pores,
                                                           actual_porosities.by_foam_pores,
                                                           parameters.porosity_foam_pore_margin)

        if porosity_total_in_margin and porosity_foam_pores_in_margin:
            if save:
                save_files(img_grey_sp, parameters, actual_porosities, user_config)
            return actual_porosities
            # break
        else:
            # Porosity values of generated image are not close enough of desired ones.
            # Therefore adapt draw parameters and generate new
            plt.close('all')
            del fig
            del ax
            parameters.adapt_parameters(user_config.desired_porosities, actual_porosities)
            print('lets do it again! total: is {:.2f}, should {:.2f}, foam pores: is {:.2f}, should {:.2f}'
                  .format(actual_porosities.total, user_config.desired_porosities.total,
                          actual_porosities.by_foam_pores, user_config.desired_porosities.by_foam_pores))

