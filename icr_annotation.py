from PIL import Image
import numpy

def _centre_of_mass(one_hot_array):
    """Returns the centre of mass for an image, determined as the average of moments in X and Y directions."""
    oha = numpy.asarray(one_hot_array)

    # check it's a 2-array
    if len(oha.shape) != 2:
        raise ValueError("This function requires a 2-dimensional array. This array has {} dimensions.".format(len(oha.shape)))

    X = oha.shape[0]
    Y = oha.shape[1]
    momentX = 0.0
    momentY = 0.0

    for y in range(0, Y):
        for x in range(0, X):
            if oha[x][y] > 0:
                momentX += x
                momentY += y

    mass = X * Y
    return [momentX / mass, momentY / mass]

class Annotation:
    def __init__(self, size):
        self.size = size
        self.pixels = numpy.zeros(self.size[0], self.size[1])
        self.com = []
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        self.__bboxinvalidated = False

    # difficult to find methods

    def __maybeexpandboundingbox(self, x, y):
        if self.xmin == None or x < self.xmin: self.xmin = x
        if self.xmax == None or x > self.xmax: self.xmax = x
        if self.ymin == None or y < self.ymin: self.ymin = y
        if self.ymax == None or y > self.ymax: self.ymax = y

    def __measureboundingbox(self):
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        for x in range(0, self.size[0]):
            for y in range(0, self.size[1]):
                if self.pixels[x, y] > 0:
                    self.__maybeexpandboundingbox(x, y)
        self.__bboxinvalidated = False

    # easy to find methods

    def setPixel(self, x, y, value):
        self.pixels[x][y] = value
        if value == 0:
            self.__bboxinvalidated = True
        else:
            self.__maybeexpandboundingbox(x, y)

    def centre_of_mass(self):
        self.com = _centre_of_mass(self.pixels)
        return self.com

    def boundingbox(self):
        if self.__bboxinvalidated:
            self.__measureboundingbox()
        return [self.xmin, self.ymin, self.xmax, self.ymax]




class AnnotationFactory:
#   so the aim here is to pull all the patches from an annotation image
#   we assume each source annotation is all contiguous patches and each patch is one cell
#   this function just splits them
#   first another function gets a patch
#   then the centre of mass is got and added to a collection
    def __init__(self, image):
        if not isinstance(image, Image.Image):
            raise ValueError("This constructor takes a PIL Image object. Jah Wobble!")
        self.image = image
        self.size = [self.image.width, self.image.height]
        self.pixels = numpy.zeros(self.image.width, self.image.height)
        self.flags = numpy.zeros(self.image.width, self.image.height)
        self.annotations = []
        self.patchwidth = None
        self.patchheight = None


    def __collectionpatchsize(self, box):
        patchwidth = numpy.abs(box[2] - box[0])
        patchheight = numpy.abs(box[3] - box[1])
        if self.patchwidth == None or patchwidth > self.patchwidth: self.patchwidth = patchwidth
        if self.patchheight == None or patchheight > self.patchheight: self.patchheight = patchheight


    def collectionFrom(self):
        for x in range(0, self.image.width - 1):
            for y in range(0, self.image.height - 1):
                annotation = self.visit(x, y, None)
                if annotation is not None:
                    annotation.centre_of_mass()
                    self.__collectionpatchsize(annotation.boundingbox())
                    self.annotations.append(annotation)

        return self.annotations


#    def getContiguousPatch(self, image, ):

    # using
    # https://stackoverflow.com/questions/452480/is-there-an-algorithm-to-determine-contiguous-colored-regions-in-a-grid
    # for graph traversal, which only really answers half the question but does the traversal bit fine.
    # I'm varying it by only using recursion for True pixels and assuming the recursive traversal will pick off every
    # connected pixel in a True region, so we can regard the root return of any visit as an entire patch.
    # Otherwise we just scan.

    def visit(self, x, y, annotation):

        # check for a flag
        if self.flags[x, y] > 0:
            # we've been here, so return without acting
            return None

        # set the flag. we've been here!
        self.flags[x, y] = 1

        # is this a hot pixel?
        if self.pixels[x,y] == 1:

            # if this is the top of the recursion, make an Annotation to hold the hot pixels
            if annotation is None:
                annotation = Annotation(self.size)

            # mark this hot pixel in the current annotation
            annotation.setPixel(x, y, 1)

            # try all the neighbours (recursive, uses the annotation we either received or made)
            self.maybevisit(x-1, y, self.pixels[x, y], annotation)
            self.maybevisit(x, y-1, self.pixels[x, y], annotation)
            self.maybevisit(x+1, y, self.pixels[x, y], annotation)
            self.maybevisit(x, y+1, self.pixels[x, y], annotation)

        # if this wasn't a hot pixel, we return nothing.
        # otherwise we should return a contiguous region of hot pixels.
        return annotation


    def maybevisit(self, x, y, value, annotation):
        values_equal = self.pixels[x, y] == value
        if values_equal:
            self.visit(x, y, annotation)
        return values_equal
