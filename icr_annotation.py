from PIL import Image
import numpy

def centre_of_mass(one_hot_array):
    """Returns the centre of mass for an image, determined as the average of moments in X and Y directions."""
    oha = numpy.asarray(one_hot_array)

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


class Annotation:
    def __init__(self, image, boundingbox):
        if not isinstance(image, Image):
            raise ValueError("This constructor takes a PIL Image object. Jah Wobble!")
        self.image = image
        self.channels = self.image.getbands()
        self.size = [self.image.width, self.image.height]
        self.boundingbox = boundingbox

#   so the aim here is to pull all the patches from an annotation image
#   we assume each source annotation is all contiguous patches and each patch is one cell
#   this function just splits them
#   first another function gets a patch
#   then the centre of mass is got and added to a collection
    def collectionFrom(self, image):
        if not isinstance(image, Image):
            raise ValueError("This constructor takes a PIL Image object. Jah Wobble!")

#    def getContiguousPatch(self, image, ):