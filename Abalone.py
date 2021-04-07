#%%
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
from tensorflow.keras.layers.experimental import preprocessing

"""Potrzebne biblioteki do uruchomienia programu to sklearn, tensorflow oraz matplotlib
    -   pip install sklearn
    -   pip install tensorflow
    -   pip install matplotlib
"""

# Wczytanie pliku
"""Plik powinien być umieszczony w tym samym folderze co uruchamiany program."""
column_names=["Sex", "Length", "Diameter", "Height", "Whole weight", "Shucked weight", "Viscera weight", "Shell weight", "Rings"]
dataframe = pd.read_csv('abalone.csv', sep=',', header=None, names=column_names)

# Normalizacja danych
"""Aby zmienić wartości w kolumnie 'Sex' z cyfry na bardziej użyteczne dla nas liczby,
 posługujemy się funkcją get_dummies"""
dataframe = pd.get_dummies(dataframe)
#print("This is our Data:\n", dataframe.head(-5))

"""Wiek naszych skorupiaków to ilość pierścieni + 1.5, dlatego też tworzymy nową kolumnę przekształcającą dane"""
dataframe['Age'] = dataframe['Rings'] + 1.5
dataframe.drop('Rings', axis = 1, inplace = True)

# Podział danych na zbiory treningowe i testowe
from sklearn.model_selection import train_test_split

X = dataframe[['Length', 'Diameter', 'Height', 'Whole weight', 'Shucked weight',
       'Viscera weight', 'Shell weight', 'Sex_F', 'Sex_I', 'Sex_M']]
Y = dataframe["Age"]

train_features, test_features, train_labels, test_labels = train_test_split(X, Y, test_size=0.28)

# Normalizacja danych
"""Normalizujemy nasze dane, żeby zmniejszyć między nimi rozbieżność"""
normalizer = preprocessing.Normalization()
normalizer.adapt(np.array(train_features))

"""Wyświetlanie w jaki sposób wyglądaja dane przed i po normalizacji:

print("This is how normalisation works:")
first = np.array(train_features[-1:])

with np.printoptions(precision=2, suppress=True):
    print('Before:', first)
    print('After:', normalizer(first).numpy())
"""

# Model regresji liniowej
"""Tworzymy model, kompilujemy go oraz uczymy"""
linear_model = keras.Sequential([
    normalizer,
    keras.layers.Dense(units=1)
])

linear_model.compile(
    optimizer=tf.optimizers.Adam(learning_rate=0.1),
    loss='mse', metrics=['mse'])
print("Fitting Linear Regression")
history_linear = linear_model.fit(train_features, train_labels, epochs=100,
    verbose=3, validation_split = 0.21)

# Model DNN
dnn_model = keras.Sequential([
      normalizer,
      keras.layers.Dense(56, activation='relu'),
      keras.layers.Dense(56, activation='relu'),
      keras.layers.Dense(1)
  ])

dnn_model.compile(loss='mse', metrics=['mse'],
                optimizer=tf.keras.optimizers.Adam(0.004))
print("Fitting DNN")
history_dnn = dnn_model.fit(train_features, train_labels, epochs=300,
    verbose=3, validation_split = 0.2)

# Model DNN with dropout
"""W celu zmniejszenia Overfittingu, w naszym modelu zastosujemy dropout"""
dnn_dropout_model = keras.Sequential([
      normalizer,
      keras.layers.Dense(56, activation='relu'),
      keras.layers.Dropout(0.5),
      keras.layers.Dense(56, activation='relu'),
      keras.layers.Dropout(0.5),
      keras.layers.Dense(1)
  ])

dnn_dropout_model.compile(loss='mse', metrics=['mse'],
                optimizer=tf.keras.optimizers.Adam(0.004))
print("Fitting DNN with dropout")
history_dnn_dropout = dnn_dropout_model.fit(train_features, train_labels, epochs=300,
    verbose=3, validation_split = 0.2)

# Wykres reprezentacji danych dla architektury DTR I RFR
def scatter_y(y_test, predicted_y):
    """Funkcja tworzy wykres przedstawiający rozbieżność między przewidzianym wiekiem a prawdziwym"""
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(y_test, predicted_y, '.k')
    
    ax.plot([0, 30], [0, 30], '--k')
    ax.plot([0, 30], [2, 32], ':k')
    ax.plot([2, 32], [0, 30], ':k')
    
    #wyświetlanie RMS
    rms = (y_test - predicted_y).std()
    ax.text(25, 3, "Root Mean Square Error = %.2g" % rms,
            ha='right', va='bottom')

    ax.set_xlim(0, 30)
    ax.set_ylim(0, 30)
    ax.set_xlabel('Wiek właściwy')
    ax.set_ylabel('Wiek przewidziany')

# Model Decision Tree Regressor
from sklearn.tree import DecisionTreeRegressor

dtr_model = DecisionTreeRegressor(max_depth=10)
dtr_model.fit(train_features, train_labels)

"""Obliczanie Root Mean Square"""
predicted_test_y = dtr_model.predict(test_features)
dtr_rms = (test_labels - predicted_test_y).std()

scatter_y(test_labels, predicted_test_y)
plt.title("DTR scatter")

# Model Random Forest Regressor
from sklearn.ensemble import RandomForestRegressor

rfr_model = RandomForestRegressor(n_estimators=10)
rfr_model.fit(train_features, train_labels)

predicted_test_y = rfr_model.predict(test_features)
rfr_rms = (test_labels - predicted_test_y).std()

scatter_y(test_labels, predicted_test_y)
plt.title("RFR Scatter")

# Krzywa uczenia
def plot_history(history):
    """Funkcja tworzy krzywą uczenia z danych otrzymywanych podczas 'karmienia' sieci"""
    plt.figure()
    plt.xlabel('Epoch\n Root Mean Square Error = %.2g' % history.history['mse'][-1])
    plt.ylabel('MSE')
    #plt.ylabel("Root Mean Square Error = %.2g" % history.history['mse'][-1])
    plt.plot(history.epoch, np.array(history.history['mse']), label='Training error')
    plt.plot(history.epoch, np.array(history.history['val_mse']), label = 'Validation error')
    plt.legend()
    plt.ylim([0,12])

def learning_curve_sklearn(train_sizes, train_scores, validation_scores, rms):
    """Funkcja tworzy krzywą uczenia dla przykładów sklearn"""
    train_scores_mean = -train_scores.mean(axis = 1)
    validation_scores_mean = -validation_scores.mean(axis = 1)
    
    plt.figure()
    plt.plot(train_sizes, train_scores_mean, label = 'Training error')
    plt.plot(train_sizes, validation_scores_mean, label = 'Validation error')
    plt.xlabel('Training set size\n Root Mean Square Error = %.2g' % rms)
    plt.ylabel('MSE')
    plt.legend()
    plt.ylim([0,12])

# Generowanie Krzywych uczenia dla Regresji liniowej i DNN
plot_history(history_linear)
plt.title("Linear MSE")
plot_history(history_dnn)
plt.title("DNN MSE")
plot_history(history_dnn_dropout)
plt.title("DNN Dropout MSE")

# Przygotowanie danych dla krzywej uczenia sklearn
"""zmienna train_sizes określa zbiór zmiennych do generowania krzywej uczenia
minimalna wartość to 1, a maksymalna to wielkość instancji naszej bazy danych,
w naszym przypadku jest to 2706"""
train_sizes = [1, 100, 250, 500, 1000, 1500, 1900, 2200, 2706]
from sklearn.model_selection import learning_curve

# Krzywa uczenia dla DTR
"""Dla wyciągnięcia danych dla krzywej uczenia używamy funkcji learning_curve,
w tej funkcji nie ma możliwości scorowania za pomocą mse, dlatego używamy nmse i później odwaracmy dane
źródło, na którym się opierałem: https://www.dataquest.io/blog/learning-curves-machine-learning/
Wyniki krzywych uczenia nie są satysfakcjonujące."""
train_sizes, train_scores, validation_scores = learning_curve(
estimator = DecisionTreeRegressor(max_depth=10),
X = train_features, y = train_labels, train_sizes = train_sizes, cv = 10,
scoring = 'neg_mean_squared_error')
learning_curve_sklearn(train_sizes, train_scores, validation_scores, dtr_rms)
plt.title("DTR MSE")

# Krzywa uczenia dla RFR
train_sizes, train_scores, validation_scores = learning_curve(
estimator = RandomForestRegressor(n_estimators=10),
X = train_features, y = train_labels, train_sizes = train_sizes, cv = 10,
scoring = 'neg_mean_squared_error')
learning_curve_sklearn(train_sizes, train_scores, validation_scores, rfr_rms)
plt.title("RFR MSE")
#%%