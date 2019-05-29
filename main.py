from icr_model_00 import generate_model

model = generate_model(imagecount=512, iX=1024, iY=1024, m=64, strides_per_frame=8,
                       kernelfilters=[[3, 5], [3, 1]],
                       attentional_depth=4)

