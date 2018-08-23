# somo-icr-keras-ml00
First attempt at a Keras model for ICR
ICR have come to us with an imaging problem, roughly, that of isolating cells from a surrounding image. This project attempts to solve that.
A convolutional deep network is used to identify cell features. A transitional layer then maps the features, which are in an array the form of the original image and n layers deep, into a smaller array of m×m image patches (encoded as an m×m-deep layer). A few more layers of this depth effectively provide a sequence of fully-connected networks connecting m×m image patches. The final layer is the same shape  and each patch should contain at most a single cell annotation.
