# -*- coding: utf-8 -*-
"""flower-images-keras-applications.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13MruUk4akDmbxrSvkp-G9EIxy9ZsEDKn

<h1 class='font-effect-3d' style='font-family:Ewert; color:#ff355e'>🌐 Styling, Links, Helpful Functions, and Modules</h1>
#### [Github Repository](https://github.com/OlgaBelitskaya/deep_learning_projects/tree/master/DL_PP0) & [Colaboratory Version](https://colab.research.google.com/drive/1H2ArWH_1kYfkIoCbxleX-aHAozRVBAdB) & [SageMathCell Version](https://olgabelitskaya.github.io/DL_PP0_Solutions_SMC.html)
"""

# Commented out IPython magic to ensure Python compatibility.
# %%html
# <style> 
# @import url('https://fonts.googleapis.com/css?family=Ewert|Roboto&effect=3d'); 
# a,h4 {color:slategray; font-family:Roboto; text-shadow:4px 4px 4px #aaa;}
# span {color:black; font-family:Roboto; text-shadow:4px 4px 4px #aaa;}
# div.output_prompt,div.output_area pre {color:slategray;}
# div.input_prompt,div.output_subarea {color:#ff355e;}      
# div.output_stderr pre {background-color:gainsboro;}  
# div.output_stderr {background-color:slategrey;}     
# </style>

import warnings; warnings.filterwarnings('ignore')
import pandas as pd,numpy as np,pylab as pl
import keras as ks,tensorflow as tf
import h5py,cv2; from tqdm import tqdm
from sklearn.model_selection import train_test_split
from keras.preprocessing import image as kimage
from keras.utils import to_categorical
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ModelCheckpoint,EarlyStopping
from keras.callbacks import ReduceLROnPlateau
from keras.models import Sequential,load_model,Model
from keras.layers import BatchNormalization,Conv2D,Dense
from keras.layers import LSTM,Flatten,Activation,Dropout
from keras.layers.advanced_activations import PReLU,LeakyReLU
from keras.layers import MaxPooling2D,GlobalMaxPooling2D
from keras.layers import GlobalAveragePooling2D
from keras.applications.inception_v3 import InceptionV3
from keras.applications.vgg16 import VGG16
fpath='../input/flower-color-images/'
fw='weights.best.flowers.hdf5'
fpath2='../input/inceptionv3/'
fw2='inception_v3_weights_tf_dim_ordering_tf_kernels_notop.h5'
fpath3='../input/vgg16/'
fw3='vgg16_weights_tf_dim_ordering_tf_kernels_notop.h5'
from keras import __version__
print('keras version:', __version__)
print('tensorflow version:', tf.__version__)

def history_plot(fit_history):
    pl.figure(figsize=(12,10)); pl.subplot(211)
    keys=list(fit_history.history.keys())[0:4]
    pl.plot(fit_history.history[keys[0]],
            color='slategray',label='train')
    pl.plot(fit_history.history[keys[2]],
            color='#ff355e',label='valid')
    pl.xlabel("Epochs"); pl.ylabel("Loss")
    pl.legend(); pl.grid()
    pl.title('Loss Function')     
    pl.subplot(212)
    pl.plot(fit_history.history[keys[1]],
            color='slategray',label='train')
    pl.plot(fit_history.history[keys[3]],
            color='#ff355e',label='valid')
    pl.xlabel("Epochs"); pl.ylabel("Accuracy")    
    pl.legend(); pl.grid()
    pl.title('Accuracy'); pl.show()

tpu=tf.distribute.cluster_resolver.TPUClusterResolver()
tf.config.experimental_connect_to_cluster(tpu)
tf.tpu.experimental.initialize_tpu_system(tpu)
tpu_strategy=tf.distribute.experimental.TPUStrategy(tpu)

"""<h1 class='font-effect-3d' style='font-family:Ewert; color:#ff355e'>🌐 Data Exploration</h1>"""

f=h5py.File(fpath+'FlowerColorImages.h5','r')
keys=list(f.keys())
images=np.array(f[keys[0]])/255
labels=np.array(f[keys[1]])
names=['phlox','rose','calendula','iris',
       'max chrysanthemum','bellflower','viola',
       'rudbeckia laciniata','peony','aquilegia']
fig=pl.figure(figsize=(11,7))
n=np.random.randint(1,30)
for i in range(n,n+8):
    ax=fig.add_subplot(2,4,i-n+1,\
    xticks=[],yticks=[],title=names[labels[i]])
    ax.imshow((images[i]))
labels=to_categorical(labels,10)
st1='Images => array shape: %s'
st2='Labels => array shape: %s'
print(st1%str(images.shape))
print(st2%str(labels.shape))

x_train,x_test,y_train,y_test=\
train_test_split(images,labels,test_size=.1,random_state=1)
m=int(len(x_test)/2)
x_valid,y_valid=x_test[:m],y_test[:m]
x_test,y_test=x_test[m:],y_test[m:]
print([x_train.shape,x_test.shape,x_valid.shape,
       y_train.shape,y_test.shape,y_valid.shape])

"""<h1 class='font-effect-3d' style='font-family:Ewert; color:#ff355e'>🌐 Keras Applications</h1>
#### InceptionV3
"""

with tpu_strategy.scope():
    iv3base_model=InceptionV3(weights=fpath2+fw2,include_top=False)
x=iv3base_model.output
x=GlobalAveragePooling2D()(x)
x=Dense(512,activation='relu')(x)
y=Dense(10,activation='softmax')(x)
with tpu_strategy.scope():
    iv3_model=Model(inputs=iv3base_model.input,outputs=y)
# freezing InceptionV3 convolutional layers
for layer in iv3base_model.layers:
    layer.trainable=False
with tpu_strategy.scope():
    iv3_model.compile(loss='categorical_crossentropy',
                      optimizer='adam',metrics=['accuracy'])

steps,epochs=189,10
data_generator=kimage\
.ImageDataGenerator(shear_range=.2,zoom_range=.2, 
                    horizontal_flip=True)
checkpointer=ModelCheckpoint(filepath=fw,save_best_only=True,verbose=2)
lr_reduction=ReduceLROnPlateau(monitor='val_loss',verbose=2,
                               patience=5,factor=.8)
history=iv3_model.fit_generator(data_generator\
.flow(x_train,y_train,batch_size=64),\
steps_per_epoch=steps,epochs=epochs,verbose=2, 
validation_data=(x_valid,y_valid), \
callbacks=[checkpointer,lr_reduction])

#for i,layer in enumerate(iv3base_model.layers[173:]):
#    print(i,layer.name)

# Unfreeze the layers [173:]
for layer in iv3_model.layers[:173]:
    layer.trainable=False
for layer in iv3_model.layers[173:]:
    layer.trainable=True   
with tpu_strategy.scope():
    iv3_model.compile(loss='categorical_crossentropy',
                      optimizer='adam',metrics=['accuracy'])

checkpointer=ModelCheckpoint(filepath=fw,save_best_only=True,verbose=2)
lr_reduction=ReduceLROnPlateau(monitor='val_loss',verbose=2,
                               patience=5,factor=.8)
history=iv3_model.fit_generator(data_generator\
.flow(x_train,y_train,batch_size=64),\
steps_per_epoch=50,epochs=epochs,verbose=2,\
validation_data=(x_valid,y_valid),\
callbacks=[checkpointer,lr_reduction])

history_plot(history)
iv3_model.load_weights(fw)
iv3_model.evaluate(x_test,y_test)

y_test_predict=np.array([np.argmax(x) 
                         for x in iv3_model.predict(x_test)])
fig=pl.figure(figsize=(12,7))
randch=np.random.choice(x_test.shape[0],size=8,replace=False)
for i,idx in enumerate(randch):
    ax=fig.add_subplot(2,4,i+1,xticks=[],yticks=[])
    ax.imshow(np.squeeze(x_test[idx]))
    pred_idx=y_test_predict[idx]
    true_idx=np.argmax(y_test[idx])
    ax.set_title("{}\n({})".format(names[pred_idx],names[true_idx]),
                 color=("#4876ff" if pred_idx==true_idx else "darkred"))
pl.show()

"""#### VGG16"""

with tpu_strategy.scope():
    vgg16base_model=VGG16(weights=fpath3+fw3,
                          include_top=False)
pvx_train=vgg16base_model.predict(x_train)
pvx_valid=vgg16base_model.predict(x_valid)
pvx_test=vgg16base_model.predict(x_test)
sh=pvx_train.shape[1:]

def vgg16model():
    model=Sequential()  
    model.add(GlobalAveragePooling2D(input_shape=sh))   
    model.add(Dense(512))
    model.add(LeakyReLU(alpha=.02))
    model.add(Dropout(.5))        
    model.add(Dense(64))
    model.add(LeakyReLU(alpha=.02))
    model.add(Dropout(.25))   
    model.add(Dense(10,activation='softmax'))    
    model.compile(loss='categorical_crossentropy',
                  optimizer='nadam',metrics=['accuracy'])
    return model
vgg16model=vgg16model()

checkpointer=ModelCheckpoint(filepath=fw,verbose=2,save_best_only=True)
lr_reduction=ReduceLROnPlateau(monitor='val_loss',patience=5,
                               verbose=2,factor=.8)
estopping=EarlyStopping(monitor='val_loss',patience=30,verbose=2)
history=vgg16model.fit(pvx_train,y_train, 
                       validation_data=(pvx_valid,y_valid), 
                       epochs=100,batch_size=64,verbose=2, 
                       callbacks=[checkpointer,lr_reduction,estopping])

history_plot(history)
vgg16model.load_weights(fw)
vgg16model.evaluate(pvx_test,y_test)