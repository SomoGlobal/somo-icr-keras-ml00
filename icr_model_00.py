from keras.models import Sequential
from keras.layers import Conv2D

ACTIVATION = "relu"


def generate_model(imagecount, iX, iY, m, strides_per_frame, kernelfilters, attentional_depth):
    """This function creates a model that, *I hope*, takes as input an image of cancer cells
    and outputs an array of m*m vectors corresponding to image patches, each of which contains
    at most one cancer cell annotation. It is trained on real cancer cell images with
    annotations performed by humans or other systems.

    The model structure is:
    * a set of normal convolutional layers of stride 1 for feature analysis and detection
    * a transition layer converting m*m patches into an m*m-deep vector representing an output image patch
    * a set of layers that all map m*m deep layers one to another, called attentional layers because of what I hope they will do

    Args:
        imagecount (int): the number of images in the training set
        iX (int): the width of a training image
        iY (int): the height of a training image
        m (int): the width and height of an output annotation patch
        strides_per_frame (int): the number of strides that would cover an entire output patch (for the transitional layer)
        kernels: an array of kernel sizes for the feature layers. Kernels are square.
        attentional_depth: how many of the last kind of layer to have

    Returns:
        a Keras model as described above (compiled but not trained)
        """

    t_stride = m / strides_per_frame

    __model = Sequential()

    # feature layers
    __model.add(Conv2D(input_shape=(3, iX, iY), data_format="channels_first", kernel_size=kernelfilters[0][0],
                       filters=kernelfilters[0][1], activation=ACTIVATION))

    for kernelfilter in kernelfilters:
        furts = Conv2D(kernel_size=kernelfilter[0], filters=kernelfilter[1], activation=ACTIVATION)
        __model.add(furts)

    # transition layer
    __model.add(Conv2D(kernel_size=1, filters=m*m, strides=(t_stride, t_stride), activation=ACTIVATION))

    i = 0
    # attentional layers
    while i < attentional_depth:
        __model.add(Conv2D(kernel_size=1, filters=m*m))
        i += 1

    __model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])

    return __model

