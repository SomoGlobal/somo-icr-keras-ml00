from icr_model_00 import generate_model

model = generate_model(imagecount=512, iX=1024, iY=1024, m=64, strides_per_frame=8, kernels=[5, 7, 9, 11, 13, 15, 17, 19], attentional_depth=4)

