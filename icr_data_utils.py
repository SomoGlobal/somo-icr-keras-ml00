import numpy as np

def centre_of_mass(one_hot_array):
    """Returns the centre of mass for an image, determined as the average of moments in X and Y directions."""
    oha = np.asarray(one_hot_array)

    # check it's a 2-array
    if len(oha.shape) != 2:
        raise ValueError("This function requires a 2-dimensional array. This array has {} dimensions.".format(len(oha.shape)))

    X = oha.shape[0]
    Y = oha.shape[1]
    momentX = 0.0;
    momentY = 0.0;

    for y in range(0, Y):
        for x in range(0, X):
            if oha[x][y] > 0:
                momentX += x
                momentY += y

    mass = X * Y
    return [momentX / mass, momentY / mass]

# def patch_distribute(iX, iY, patches)
