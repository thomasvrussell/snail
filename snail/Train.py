import numpy as np
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
import tensorflow
tensorflow.compat.v1.logging.set_verbosity(tensorflow.compat.v1.logging.ERROR)
from tensorflow.keras import Input, Model
from tensorflow.keras.regularizers import l2
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam, RMSprop, Nadam
from tensorflow.keras.layers import LSTM, Dense, TimeDistributed, Bidirectional

class SNAIL_Train:
    @staticmethod
    def SLT(XDATA_train, YDATA_train, WEIGHT_train):

        # ** description of inputs
        #    XDATA_train: array shape (Nsamp, timestep, 1+1+184)
        #    YDATA_train: array shape (Nsamp, 184)
        #    WEIGHT_train: array shape (Nsamp)
        #    NOTE: timestep == 2 in our work
        #          184 is the dimension of FPCA parameterization for one SN spectrum
        #          1+1 (in XDATA_train) means target_phase + input_phase

        # ** define LSTM architechture parameters
        paradict = {'n_units': 256, 'batch_size': 1472, 'epochs': 30, 
                    'optmethod': 'Nadam', 'learning_rate': 40*1e-5, 
                    'drop_rate': 0.14, 'rdrop_rate': 0.16, 'rreg_l2':0*1e-6, 
                    'Bayesian': True}

        n_units, batch_size, epochs = paradict['n_units'], paradict['batch_size'], paradict['epochs']
        optmethod, learning_rate = paradict['optmethod'], paradict['learning_rate']
        drop_rate, rdrop_rate, rreg_l2 = paradict['drop_rate'], paradict['rdrop_rate'], paradict['rreg_l2']
        Bayesian = paradict['Bayesian']
        
        recurrent_regularizer = None
        if rreg_l2 is not None: 
            recurrent_regularizer = l2(rreg_l2)  # typical values are 1e-6, 1e-5, 1e-4 ...
        if optmethod == 'Adam': optimizer = Adam(lr=learning_rate)
        if optmethod == 'Nadam': optimizer = Nadam(lr=learning_rate)
        if optmethod == 'RMSprop': optimizer = RMSprop(lr=learning_rate)

        # ** train the model
        n_steps = 2
        n_features = (2+90)*2
        XDP_train = XDATA_train.copy()
        YDP_train = YDATA_train.copy()
        WDP_train = WEIGHT_train.copy()
        #-#-#-# + Adjust form [convert to 2-identical-layers] #-#-#-#
        YDP_train = np.array([[yd]*n_steps for yd in YDP_train])

        # *** Remarks on time-lock dropout mask in LSTM
        #     Keras has 3 implementations of LSTM, with implementation 1 as default (seems to be untied-weights).
        #     The implementation 2 corresponds to tied-weights LSTM 
        #     (Note: RNN dropout must be shared for all gates, resulting in a slightly reduced regularization.)
        #     training=True means MC dropout, here means W, U row-drop, dropconnect means direct weight-matrix drop.
        #     NOTE: Bidrectional & TimeDistributed requires return_sequence=True at last LSTM layer.

        if not Bayesian:
            model = Sequential()
            model.add(Bidirectional(LSTM(n_units, activation='tanh', dropout=0.0, kernel_regularizer=None, \
                recurrent_dropout=rdrop_rate, recurrent_regularizer=recurrent_regularizer, recurrent_activation='sigmoid', \
                return_sequences=True, implementation=1), input_shape=(n_steps, 2+n_features)))   # No dropout in first layer

            model.add(Bidirectional(LSTM(n_units, activation='tanh', dropout=drop_rate, kernel_regularizer=None, \
                recurrent_dropout=rdrop_rate, recurrent_regularizer=recurrent_regularizer, recurrent_activation='sigmoid', \
                return_sequences=True, implementation=1)))

            model.add(Bidirectional(LSTM(n_units, activation='tanh', dropout=drop_rate, kernel_regularizer=None, \
                recurrent_dropout=rdrop_rate, recurrent_regularizer=recurrent_regularizer, recurrent_activation='sigmoid', \
                return_sequences=True, implementation=1)))

            model.add(TimeDistributed(Dense(units=n_features, activation='linear')))  # No dropout before last layer.
            model.compile(loss='mse', optimizer=optimizer, metrics=['mae'])
            
        if Bayesian:
            inputs = Input(shape=(n_steps, 2+n_features))
            blstm1 = Bidirectional(LSTM(n_units, activation='tanh', dropout=0.0, kernel_regularizer=None, \
                recurrent_dropout=rdrop_rate, recurrent_regularizer=recurrent_regularizer, recurrent_activation='sigmoid', \
                return_sequences=True, implementation=1))(inputs, training=True)   # No dropout in first layer, otherwise it has terrible performance

            blstm2 = Bidirectional(LSTM(n_units, activation='tanh', dropout=drop_rate, kernel_regularizer=None, \
                recurrent_dropout=rdrop_rate, recurrent_regularizer=recurrent_regularizer, recurrent_activation='sigmoid', \
                return_sequences=True, implementation=1))(blstm1, training=True)
            
            blstm3 = Bidirectional(LSTM(n_units, activation='tanh', dropout=drop_rate, kernel_regularizer=None, \
                recurrent_dropout=rdrop_rate, recurrent_regularizer=recurrent_regularizer, recurrent_activation='sigmoid', \
                return_sequences=True, implementation=1))(blstm2, training=True)

            # No dropout layer here, as we didn't find a time-locked dropout-dense.
            outputs = TimeDistributed(Dense(units=n_features, activation='linear'))(blstm3)
            model = Model(inputs, outputs)
            model.compile(loss='mse', optimizer=optimizer, metrics=['mae'])

        model.fit(XDP_train, YDP_train, sample_weight=WDP_train, validation_data=None, \
            batch_size=batch_size, epochs=epochs, verbose=2, shuffle=True, callbacks=None)

        return model
