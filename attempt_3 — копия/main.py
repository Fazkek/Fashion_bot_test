#КОД РАБОТАЕТ НА ВЕРСИИ PYTHON 3.10!!!!!!!!!!!!!!!!!!
# файл, где хранятся пользователи и инфа о них
import json
# штука для открытия фото
from PIL import Image
# удаление заднего фона картинки
import rembg
# для удаления фото, после моего работы с ними (чтоб память не загружать)
import os
# 123
from sklearn.cluster import KMeans

import tensorflow as tf
# загрузка модели
from tensorflow.keras.models import load_model
# для перевода скачанной картинки в grayscale
from colorthief import ColorThief

import keras.utils as imag
import numpy as np
import cv2


class JsonFile:
    def write(data, file_name):
        with open(file_name, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def read(file_name):
        with open(file_name, 'r', encoding="utf-8") as file:
            return json.load(file)


class Predict:
    def fashion(photo):
        classes = ['футболка', 'брюки', 'свитер', 'платье', 'пальто', 'туфли', 'рубашка', 'кроссовки', 'сумка',
                   'ботинки']

        model = load_model('fashion_mnist_dense.h5')

        image = Image.open(f"{photo.file_id}.jpg")

        # удаление фона с помощью rembg
        image = rembg.remove(image)

        # создание нового изображения с белым фоном аналогичного размера
        new_image = Image.new("RGB", image.size, (255, 255, 255))

        # наложение полученной png фотографии на белый фон
        new_image.paste(image, (0, 0), image)

        new_image.save(f"1_{photo.file_id}.jpg")

        img = imag.load_img(f"1_{photo.file_id}.jpg", target_size=(28, 28), color_mode='grayscale')

        x = imag.img_to_array(img)
        x = x.reshape(1, 784)
        x = 255 - x
        x /= 255

        prediction = model.predict(x)
        prediction = np.argmax(prediction)

        name = classes[prediction]
        return name


class Color:
    def find(photo):
        # Получение цвета в массив с форматом RGB
        color_thief = ColorThief(f"1_{photo.file_id}.jpg")
        # get the dominant color
        dominant_color = color_thief.get_color(quality=1)
        os.remove(f"1_{photo.file_id}.jpg")
        os.remove(f"{photo.file_id}.jpg")

        model = load_model('colormodel_trained_90.h5')
        # Интерпритация массива в название цвета
        color_dict={
            0 : 'Красный',
            1 : 'Зелёный',
            2 : 'Синий',
            3 : 'Жёлтый',
            4 : 'Оранжевый',
            5 : 'Розовый',
            6 : 'Фиолетовый',
            7 : 'Коричневый',
            8 : 'Серый',
            9 : 'Чёрный',
            10 : 'Белый'
        }


        
        rgb = np.array(dominant_color) #rgb tuple to numpy array
        input_rgb = np.reshape(rgb, (-1,3)) #reshaping as per input to ANN model
        color_class_confidence = model.predict(input_rgb) # Output of layer is in terms of Confidence of the 11 classes
        color_index = np.argmax(color_class_confidence, axis=1) #finding the color_class index from confidence
        color = color_dict[int(color_index)]
        return color