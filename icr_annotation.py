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
        self.size = [self.image.width, self.image.height]
        self.boundingbox = boundingbox
        self.pixels =

#   so the aim here is to pull all the patches from an annotation image
#   we assume each source annotation is all contiguous patches and each patch is one cell
#   this function just splits them
#   first another function gets a patch
#   then the centre of mass is got and added to a collection
    def collectionFrom(self, image):
        if not isinstance(image, Image):
            raise ValueError("This constructor takes a PIL Image object. Jah Wobble!")

#    def getContiguousPatch(self, image, ):

    # using
    # https://stackoverflow.com/questions/452480/is-there-an-algorithm-to-determine-contiguous-colored-regions-in-a-grid
    # for graph traversal, which only really answers half the question but does the traversal bit fine.
    # I'm varying it by only using recursion for True pixels and assuming the recursive traversal will pick off every
    # connected pixel in a True region, so we can regard the root return of any visit as an entire patch.
    # Otherwise we just scan.

    def visit(self, x, y):
        if self.pixels[x, y].marked:
            return
        self.pixels[x, y].marked = True
        if self.pixels[x,y].value == True:
            self.maybevisit(x-1, y, self.pixels[x, y].value)
            self.maybevisit(x, y-1, self.pixels[x, y].value)
            self.maybevisit(x+1, y, self.pixels[x, y].value)
            self.maybevisit(x, y+1, self.pixels[x, y].value)

    def maybevisit(self, x, y, value):
        values_equal = self.pixels[x, y].value == value
        if values_equal:
            self.visit(x, y)
        return values_equal
