import matplotlib.patches as patches
import numpy as np
from matplotlib.path import Path
from src.io_utils import print_red_terminal_message

DARK_ELLIPSE_COLOR = (0.3, 0.3, 0.3)
LIGHT_ELLIPSE_COLOR = 'lightgrey'


class BezierEllipse:
    """
     Ellipse Objects to put into the image instance and create the over all image at the end
    """

    def __init__(self, x, y, width, height, n=2, r=.2, n0=7, n1=5, color=LIGHT_ELLIPSE_COLOR):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.n = n  # number of possibly sharp edges
        self.r = r  # magnitude of the perturbation from the unit circle, should be between 0 and 1
        self.N0 = n0  # parameter for bezier shape computation
        self.N1 = n1  # parameter for bezier shape computation
        self.color = color
        self.__create_bezier_vertices_and_codes()
        self.path = Path(self.vertices, self.codes)

    def __create_bezier_vertices_and_codes(self) -> None:
        """
        Creates the bezier shape / path of the ellipse
        Bezier shape taken/inspired from https://newbedev.com/create-random-shape-contour-using-matplotlib
        There is one initial point and 3 points per cubic bezier curve.
        Thus, the curve will only pass through n points, those will be the sharp edges,
            the other 2 modify the shape of the bezier curve
        :return: nothing but manipulates / initializes the internat vertices and codes variables
        """

        N = self.n * self.N0 + self.N1  # number of points in the Path
        angles = np.linspace(0, 2 * np.pi, N)
        self.codes = np.full(N, Path.CURVE4)
        self.codes[0] = Path.MOVETO

        self.vertices = np.stack((np.cos(angles), np.sin(angles))).T * (2 * self.r * np.random.random(N) + 1 - self.r)[:, None]
        self.vertices[-1, :] = self.vertices[0, :]  # Using this instead of Path.CLOSEPOLY avoids an innecessary straight line

        # scale x- and y-coords of vertices to given width and height
        self.__scale_to_length("x")
        self.__scale_to_length("y")

        # set center of vertices to x, y
        self.vertices[:, 0] += self.x
        self.vertices[:, 1] += self.y

    def __scale_to_length(self, coord) -> None:
        """
        Scales the vertices of the ellipse to the width / height specified in the constructor
        :param coord: "x" or "y", depending on which coordinate should be scaled
        :return: nothing, but manipulates the class variable "vertices"
        """
        if coord == "x":
            index = 0
        elif coord == "y":
            index = 1
        else:
            print_red_terminal_message("Wrongly specified coordinate {}, only x and y are allowed".format(coord))

        # scale x (index = 0) or y (index=1) coordinates to given width / height
        my_max = self.vertices[:, index].max()
        my_min = self.vertices[:, index].min()
        actual_length = my_max + np.abs(my_min)

        for e, v in enumerate(self.vertices):
            ratio = np.abs(v[index]) / actual_length
            if index == 0:
                new_coord = self.width * ratio
            elif index == 1:
                new_coord = self.height * ratio

            if v[index] < 0:
                self.vertices[e][index] = -new_coord

            elif v[index] >= 0:
                self.vertices[e][index] = new_coord
            else:
                print('Problem with coordinate {} !'.format(v[index]))

    def retrieve_patch(self) -> patches.PathPatch:
        """
        Creates a matplotlib path patch according to the ellipse path
            that can be drawn onto a matplotlib figure
        :return: the according PathPatch
        """
        return patches.PathPatch(self.path, edgecolor=self.color, facecolor=self.color, lw=2)
