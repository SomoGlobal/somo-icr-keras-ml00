from PIL import Image
import numpy


def _centre_of_mass(one_hot_array):
    """Returns the centre of mass for an image, determined as the average of moments in X and Y directions."""
    oha = numpy.asarray(one_hot_array)

    # check it's a 2-array
    if len(oha.shape) != 2:
        raise ValueError("This function requires a 2-dimensional array. This array has {} dimensions.".format(len(oha.shape)))

    x = oha.shape[0]
    y = oha.shape[1]
    moment_x = 0.0
    moment_y = 0.0

    for y in range(0, y):
        for x in range(0, x):
            if oha[x][y] > 0:
                moment_x += x
                moment_y += y

    mass = x * y
    return [moment_x / mass, moment_y / mass]


class Patch:
    def __init__(self, size):
        self.size = size
        self.pixels = numpy.zeros((self.size[0], self.size[1]))
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

    def set_pixel(self, x, y, value):
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


class PatchFactory:
    # so the aim here is to pull all the patches from an annotation image
    # we assume each source annotation is all contiguous patches and each patch is one cell
    # this function just splits them
    # first another function gets a patch
    # then the centre of mass is got and added to a collection
    def __init__(self, image):
        if not isinstance(image, Image.Image):
            raise ValueError("This constructor takes a PIL Image object. Jah Wobble!")
        self.image = image
        self.size = [self.image.width, self.image.height]
        self.px = self.image.load()
        self.pixels = numpy.zeros((self.image.width, self.image.height))
        self.flags = numpy.zeros((self.image.width, self.image.height))
        self.annotations = []
        self.patchwidth = None
        self.patchheight = None
        self.threshold = 150 #self.otsu()
        self.__exactequality = False
        print("threshold " + str(self.threshold))

    def otsu(self):
        histogram = self.image.histogram()
        pxtotal = self.size[0] * self.size[1]

        sum0 = 0
        sqr0 = 0
        sum1 = pxtotal
        sqr1 = self.sqr1_256(histogram)
        min = -1
        minthreshold = -99

        for threshold in range(256):
            print("sum0^2 " + str(sum0 * sum0) + " sqr0 " + str(sqr0))

            sum0 += histogram[threshold]
            sum1 -= histogram[threshold]
            sqr = histogram[threshold] * histogram[threshold]
            sqr0 += sqr
            sqr1 -= sqr
            vars = sum0 * (sqr0 - (sum0 * sum0)) + sum1 * (sqr1 - (sum1 * sum1))

            print("sum0^2 " + str(sum0 * sum0) + " sqr0 " + str(sqr0))
            print("sum1^2 " + str(sum1 * sum1) + " sqr1 " + str(sqr1))
            print("vars " + str(vars) + " min " + str(min))
            print("minthreshold " + str(minthreshold))

            if vars < min or min == -1:
                min = vars
                minthreshold = threshold

        return minthreshold

    def sqr1_256(self, histogram):
        sqr1 = 0
        for i in range(256):
            sqr1 += histogram[i] * histogram[i]

        return sqr1


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
                    print("annotation added")
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

    def visit(self, x, y, patch):

        # check for a flag
        if self.flags[x, y] > 0:
            # we've been here, so return without acting
            return None

        # set the flag. we've been here!
        self.flags[x, y] = 1

        # is this a hot pixel?
        if self.px[x, y][0] > self.threshold:

            # if this is the top of the recursion, make an Annotation to hold the hot pixels
            if patch is None:
                patch = Patch(self.size)

            # mark this hot pixel in the current annotation
            patch.set_pixel(x, y, 1)

            # try all the neighbours in bounds (recursive, uses the annotation we either received or made)
            if x >= 1:
                self.maybevisit(x-1, y, self.pixels[x, y], patch)
            if y >= 1:
                self.maybevisit(x, y-1, self.pixels[x, y], patch)
            if x < self.size[0]:
                self.maybevisit(x+1, y, self.pixels[x, y], patch)
            if y < self.size[1]:
                self.maybevisit(x, y+1, self.pixels[x, y], patch)

        # if this wasn't a hot pixel, we return nothing.
        # otherwise we should return a contiguous region of hot pixels.
        return patch

    def maybevisit(self, x, y, value, annotation):
        values_match = self.__match(self.pixels[x, y], value)
        if values_match:
            self.visit(x, y, annotation)
        return values_match

    def __match(self, a, b):
        if self.__exactequality:
            return a == b
        else:
            return not (a > self.threshold) ^ (b > self.threshold)

    def write(self, path, format):
        output = Image.new("1", self.size, 0)
        pixels = output.load()
        for annotation in self.annotations:
            for x in range(self.size[0]):
                for y in range(self.size[1]):
                    if annotation.pixels[x, y] > 0:
                        pixels[(x, y)] = 1

        output.save(path, format)


im = Image.open("./data/feets.tif")
pf = PatchFactory(im)
patches = pf.collectionFrom()
print("number of patches " + str(patches.__len__()))
pf.write("./data/farts.png", "PNG")