from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split
import pandas as pd
import riotPoll

dataset = riotPoll.matchInfo
x = pd.DataFrame()
x = dataset.iloc[:, 0:25]
y = dataset.iloc[:, -1]

xTrain, xTest, yTrain, yTest = train_test_split(x, y)

model = Sequential()
model.add(Dense(25, input_dim = 25, activation = 'relu'))
model.add(Dense(25, activation = 'relu'))
model.add(Dense(1, activation = 'sigmoid'))

model.compile(loss = 'binary_crossentropy', optimizer = 'adam', metrics = ['accuracy'])
model.fit(xTrain, yTrain, 1, 1000)

_, accuracy = model.evaluate(x, y)
print('Accuracy: %.2f' % (accuracy*100))
