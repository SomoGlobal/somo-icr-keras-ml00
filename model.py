from keras.models import Sequential
from keras.layers import Conv2D

# input image count
imagecount = 512

# input image dimensions
iX = 1024
iY = 1024

# output patch dimension
m = 64

# transition stride
strides_per_frame = 8
t_stride = m / strides_per_frame;

# kernel sizes
kernels = [5, 7, 9, 11, 13, 15, 17, 19]

# attentional depth
attentional_depth = 4

model = Sequential()

# feature layers
model.add(Conv2D(input_shape=(imagecount, iX, iY, 3), data_format="channels_last"), kernel_size=kernels[0], filters = kernels[0])
for kernel in kernels:
  model.add(Conv2D, kernel_size=kernel, filters=kernel)

# transition layer
model.add(Conv2D, kernel_size=1, filters=m*m, strides=t_stride)

i = 0;
# attentional layers
while (i < attentional_depth):
  model.add(Conv2D, kernel_size=1, filters=m*m)
  i += 1

model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])