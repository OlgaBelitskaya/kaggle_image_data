# -*- coding: utf-8 -*-
"""the-dataset-of-flower-images.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wZN8krW3TyAwzIMkF7kMlnRi6mpNb7m0

<h1 class='font-effect-3d' style='font-family:Ewert; color:#ff355e;'> 🌐 Styling, Links and Modules</h1>
---
#### [Keras. Applications](https://keras.io/applications/#inceptionv3)
#### [Extended version. Python](https://olgabelitskaya.github.io/kaggle_flowers.html) & [Extended version. R](https://olgabelitskaya.github.io/kaggle_flowers_R.html)
#### [Github Repository](https://github.com/OlgaBelitskaya/deep_learning_projects/tree/master/DL_PP0) & [Colaboratory Version](https://colab.research.google.com/drive/1H2ArWH_1kYfkIoCbxleX-aHAozRVBAdB)
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
from keras.models import Sequential,load_model
from keras.layers import BatchNormalization,Conv2D,Dense
from keras.layers import LSTM,Flatten,Activation,Dropout
from keras.layers.advanced_activations import PReLU,LeakyReLU
from keras.layers import MaxPooling2D,GlobalMaxPooling2D
from keras.layers import GlobalAveragePooling2D
from keras.applications.inception_v3 import InceptionV3
from keras.applications.inception_v3 import preprocess_input as iv3pi
fpath='../input/flower-color-images/flower_images/flower_images/'
fw='weights.best.flowers.hdf5'
from keras import __version__
print('keras version:', __version__)
print('tensorflow version:', tf.__version__)

def history_plot(fit_history):
    pl.figure(figsize=(12,9));pl.subplot(211)
    pl.plot(fit_history.history['loss'],
            color='slategray',label='train')
    pl.plot(fit_history.history['val_loss'],
            color='#ff355e',label='valid')
    pl.xlabel("Epochs"); pl.ylabel("Loss")
    pl.legend(); pl.grid()
    pl.title('Loss Function')      
    pl.subplot(212)
    pl.plot(fit_history.history['acc'],
            color='slategray',label='train')
    pl.plot(fit_history.history['val_acc'], 
            color='#ff355e',label='valid')
    pl.xlabel('Epochs'); pl.ylabel('Accuracy')    
    pl.legend(); pl.title('Accuracy')
    pl.grid(); pl.show()
def path_to_tensor(img_path,fpath=fpath):
    img=kimage.load_img(fpath+img_path, 
                        target_size=(128,128))
    x=kimage.img_to_array(img)
    return np.expand_dims(x,axis=0)
def paths_to_tensor(img_paths):
    tensor_list=[path_to_tensor(img_path) 
                 for img_path in tqdm(img_paths)]
    return np.vstack(tensor_list)
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES=True

"""<h1 class='font-effect-3d' style='font-family:Ewert; color:#ff355e;'> &#x1F310; &nbsp; Data Exploration</h1>"""

flowers=pd.read_csv(fpath+"flower_labels.csv")
flower_files=flowers['file']
flower_labels=flowers['label'].values
names=['phlox','rose','calendula','iris',
       'max chrysanthemum','bellflower','viola',
       'rudbeckia laciniata','peony','aquilegia']

# with h5py.File('../input/FlowerColorImages.h5','r') as f:
#     flower_images=f['images'].value
#     flower_labels=f['labels'].value

n=np.random.randint(0,210,1)[0]
print('Label: ',flower_labels[n],
      names[flower_labels[n]])
img=cv2.imread(fpath+flower_files[n])
rgb_img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
pl.figure(figsize=(3,3))
pl.imshow(rgb_img);

flower_images=paths_to_tensor(flower_files)/255
flower_labels=to_categorical(flower_labels,10)

x_train,x_test,y_train,y_test=\
train_test_split(flower_images,flower_labels,
                 test_size=.2,random_state=1)
m=int(len(x_test)/2)
x_valid,y_valid=x_test[:m],y_test[:m]
x_test,y_test=x_test[m:],y_test[m:]
[x_train.shape,x_test.shape,x_valid.shape,
 y_train.shape,y_test.shape,y_valid.shape]

n=np.random.randint(0,168,1)[0]
print('Label: ',y_train[n],
      names[np.argmax(y_train[n])])
pl.figure(figsize=(3,3))
pl.imshow((x_train[n]));

"""<h1 class='font-effect-3d' style='font-family:Ewert; color:#ff355e;'> &#x1F310; &nbsp; Classification Models</h1>"""

def mlp_model():
    model=Sequential()    
    model.add(Dense(128,activation='relu',
                    input_shape=(128*128*3,)))
    model.add(BatchNormalization())    
    model.add(Dense(256,activation='relu'))
    model.add(BatchNormalization())    
    model.add(Dense(512,activation='relu'))
    model.add(BatchNormalization())   
    model.add(Dense(1024, activation='relu'))
    model.add(Dropout(.2))     
    model.add(Dense(10, activation='softmax'))
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',metrics=['accuracy'])
    return model
mlp_model=mlp_model()

early_stopping=EarlyStopping(monitor='val_loss',patience=20,verbose=2)
checkpointer=ModelCheckpoint(filepath=fw,save_best_only=True,verbose=2)
lr_reduction=ReduceLROnPlateau(monitor='val_loss',verbose=2,
                               patience=5,factor=.8)
history=mlp_model.fit(x_train.reshape(-1,128*128*3),y_train,
                      epochs=100,batch_size=64,verbose=2,
                      validation_data=(x_valid.reshape(-1,128*128*3),y_valid),
                      callbacks=[checkpointer,early_stopping,lr_reduction])

history_plot(history)
mlp_model.load_weights(fw)
mlp_model.evaluate(x_test.reshape(-1,128*128*3),y_test)

def cnn_model():
    model=Sequential()
    model.add(Conv2D(32,(5,5),padding='same',
                     input_shape=x_train.shape[1:]))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(.25))
    model.add(Conv2D(96,(5,5)))
    model.add(Activation('relu'))    
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(.25))
    model.add(GlobalAveragePooling2D())    
    model.add(Dense(512,activation='tanh'))
    model.add(Dropout(.25))     
#    model.add(Dense(256,activation='tanh'))
#    model.add(Dropout(.25))     
    model.add(Dense(128,activation='tanh'))
    model.add(Dropout(.25)) 
    model.add(Dense(10))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy',
                  optimizer='nadam',metrics=['accuracy'])    
    return model
cnn_model=cnn_model()

early_stopping=EarlyStopping(monitor='val_loss',patience=20,verbose=2)
checkpointer=ModelCheckpoint(filepath=fw,save_best_only=True,verbose=2)
lr_reduction=ReduceLROnPlateau(monitor='val_loss',verbose=2,
                               patience=5,factor=.8)
history=cnn_model.fit(x_train,y_train,epochs=100,batch_size=16,
                      verbose=2,validation_data=(x_valid,y_valid),
                      callbacks=[checkpointer,early_stopping,lr_reduction])

history_plot(history)
cnn_model.load_weights(fw)
cnn_model.evaluate(x_test,y_test)

'''
generator=kimage.\
ImageDataGenerator(shear_range=.3,zoom_range=.3,
                   rotation_range=30,horizontal_flip=True)
ghistory=cnn_model.fit_generator(generator\
.flow(x_train,y_train,batch_size=64),\
steps_per_epoch=189,epochs=3,verbose=2,\
validation_data=(x_valid,y_valid),
callbacks=[checkpointer,early_stopping,lr_reduction])
'''
''' '''

'''
cnn_model.load_weights(fw)
cnn_model.evaluate(x_test,y_test)
'''
''' '''

y_test_predict=cnn_model.predict_classes(x_test)
fig=pl.figure(figsize=(14,7))
randch=np.random.choice(x_test.shape[0],size=8,replace=False)
for i,idx in enumerate(randch):
    ax=fig.add_subplot(2,4,i+1,xticks=[],yticks=[])
    ax.imshow(np.squeeze(x_test[idx]))
    pred_idx=y_test_predict[idx]
    true_idx=np.argmax(y_test[idx])
    ax.set_title("{}\n({})".format(names[pred_idx],names[true_idx]),
                 color=("#4876ff" if pred_idx==true_idx else "darkred"))
pl.show()

def rnn_model():
    model=Sequential()
    model.add(LSTM(196,return_sequences=True,
                   input_shape=(1,128*128*3))) 
    model.add(LSTM(196,return_sequences=True))
    model.add(LSTM(196))  
    model.add(Dense(512,activation='relu'))
    model.add(Dense(10,activation='softmax'))
    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',metrics=['accuracy'])    
    return model
rnn_model=rnn_model()

early_stopping=EarlyStopping(monitor='val_loss',patience=20,verbose=2)
checkpointer=ModelCheckpoint(filepath=fw,save_best_only=True,verbose=2)
lr_reduction=ReduceLROnPlateau(monitor='val_loss',verbose=2,
                               patience=5,factor=.8)
history=rnn_model.fit(x_train.reshape(-1,1,128*128*3),y_train,
                      epochs=100,batch_size=64,verbose=2,
                      validation_data=(x_valid.reshape(-1,1,128*128*3),y_valid),
                      callbacks=[checkpointer,early_stopping,lr_reduction])

history_plot(history)
rnn_model.load_weights(fw)
rnn_model.evaluate(x_test.reshape(-1,1,128*128*3),y_test)