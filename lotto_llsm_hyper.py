import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow import keras
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping
from keras_tuner.tuners import RandomSearch

# 데이터 로드
rows = np.loadtxt("./lotto.csv", delimiter=",")
row_count = len(rows)

# 당첨번호를 원핫인코딩벡터로 변환
def numbers2ohbin(numbers):
    ohbin = np.zeros(45)
    for i in range(6):
        ohbin[int(numbers[i])-1] = 1
    return ohbin

# 원핫인코딩벡터를 번호로 변환
def ohbin2numbers(ohbin):
    numbers = []
    for i in range(len(ohbin)):
        if ohbin[i] == 1.0:
            numbers.append(i+1)
    return numbers

numbers = rows[:, 1:7]
ohbins = list(map(numbers2ohbin, numbers))

# 데이터 형태 변환
x_samples = np.array(ohbins[0:row_count-1])
y_samples = np.array(ohbins[1:row_count])

# 데이터 분할
x_train, x_test, y_train, y_test = train_test_split(x_samples, y_samples, test_size=0.2, random_state=42)

# 데이터 형태 조정
x_train = x_train.reshape(-1, 1, 45)
x_test = x_test.reshape(-1, 1, 45)

# 검증 세트 분할 및 형태 조정
x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.25, random_state=42) # 검증 세트 분할
x_val = x_val.reshape(-1, 1, 45)

# 모델 정의 함수
def build_model(hp):
    model = keras.Sequential([
        keras.layers.LSTM(units=hp.Int('units', min_value=32, max_value=512, step=32), input_shape=(1, 45)),
        keras.layers.Dense(45, activation='sigmoid')
    ])
    model.compile(optimizer=keras.optimizers.Adam(hp.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4])),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    return model

# 하이퍼파라미터 튜닝
tuner = RandomSearch(
    build_model,
    objective='val_accuracy',
    max_trials=10,
    executions_per_trial=3,
    directory='tuning',
    project_name='lotto_hyper_tuning'
)

# 조기 종료
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

# 튜닝 시작
tuner.search(x_train, y_train, epochs=100, validation_data=(x_val, y_val), callbacks=[early_stopping])

# 최적의 하이퍼파라미터로 모델 학습
best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
model = tuner.hypermodel.build(best_hps)
history = model.fit(x_train, y_train, epochs=100, validation_data=(x_val, y_val), callbacks=[early_stopping])

# 모델 평가
test_loss, test_acc = model.evaluate(x_test, y_test)
print(f'\nTest Loss: {test_loss}, Test Accuracy: {test_acc}')


# 학습 과정 시각화
plt.figure(figsize=(12, 4))

# 손실 시각화
plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Loss Over Time')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

# 정확도 시각화
plt.subplot(1, 2, 2)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Accuracy Over Time')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.tight_layout()
plt.show()

# 로또 번호 생성을 위한 확률 기반 함수
def gen_numbers_from_probability(prob_dist):
    numbers = np.random.choice(range(1, 46), size=6, replace=False, p=prob_dist/np.sum(prob_dist))
    return numbers

# 예측된 로또 번호 출력
print('Receive numbers:')
xs = x_samples[-1].reshape(1, 1, 45)
ys_pred = model.predict_on_batch(xs)
list_numbers = []

for n in range(5):
    numbers = gen_numbers_from_probability(ys_pred[0])
    numbers.sort()
    print('{0} : {1}'.format(n, numbers))
    list_numbers.append(numbers)