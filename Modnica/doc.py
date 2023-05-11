import json
from PIL import Image
import rembg
import pymorphy2
import os
from sklearn.cluster import KMeans
import tensorflow as tf
from tensorflow.keras.models import load_model
from colorthief import ColorThief
import keras.utils as imag
import numpy as np
import cv2


class JsonFile:
    def write(data, file_name):
        with open(file_name, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def read(file_name):
        with open(file_name, 'r', encoding="utf-8") as file:
            return json.load(file)


class Predict:
    def fashion(photo):
        classes = ['футболка', 'брюки', 'свитер', 'платье', 'пальто', 'кроссовки', 'футболка', 'кроссовки', 'футболка',
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
            8 : 'Белый',
            9 : 'Чёрный',
            10 : 'Белый'
        }


        
        rgb = np.array(dominant_color)
        input_rgb = np.reshape(rgb, (-1,3))
        color_class_confidence = model.predict(input_rgb)
        color_index = np.argmax(color_class_confidence, axis=1)
        color = color_dict[int(color_index)]
        return color

class Recomend:
    def recommend_outfit(data):
        def opposite_color(color):
            color_wheel = {
                'Красный': 'Зелёный',
                'Зелёный': 'Красный',            
                'Синий': 'Оранжевый',
                'Оранжевый': 'Синий',
                'Жёлтый': 'Фиолетовый',            
                'Фиолетовый': 'Жёлтый',            
                'Белый': 'Чёрный',
                'Чёрный': 'Белый',
                'Розовый': 'Коричневый',
                'Коричневый': 'Розовый',
                'Серый': 'белый'
            }
            return color_wheel[color]
        def circle_color(color):
            color_circle = {
                'Красный': '🔴',
                'Зелёный': '🟢',            
                'Синий': '🔵',
                'Оранжевый': '🟠',
                'Жёлтый': '🟡',            
                'Фиолетовый': '🟣',            
                'Белый': '⚪️',
                'Чёрный': '⚫️',
                'Розовый': '🌸',
                'Коричневый': '🟤',
                'Серый': '⚙️'
            }
            return color_circle[color]
        
        morph = pymorphy2.MorphAnalyzer()
        outfits = []
        for outfit in data.values():
            for i, item1 in enumerate(outfit):
                type1, color1 = list(item1.keys())[0], list(item1.values())[0]
                if type1 in ['футболка', 'рубашка', 'свитер', 'платье', 'пальто']:
                    for j, item2 in enumerate(outfit[i+1:], start=i+1):
                        type2, color2 = list(item2.keys())[0], list(item2.values())[0]
                        if type1 != type2 and (color1 not in ['Белый', 'Чёрный']) and opposite_color(color1) == color2:
                            if morph.parse(type2)[0].tag.number == 'plur':
                                outfits.append(f"🕶 Будут хорошо смотреться 🕶\n{circle_color(color1)} {morph.parse(color1)[0].inflect({'nomn', f'{morph.parse(type1)[0].tag.number}', f'{morph.parse(type1)[0].tag.gender}'}).word.capitalize()} {morph.parse(type1)[0].inflect({'nomn'}).word} и {morph.parse(color2)[0].inflect({'nomn', f'{morph.parse(type2)[0].tag.number}'}).word} {type2} {circle_color(color2)}")                            
                            else:
                                outfits.append(f"🕶 Будут хорошо смотреться 🕶\n{circle_color(color1)} {morph.parse(color1)[0].inflect({'nomn', f'{morph.parse(type1)[0].tag.number}', f'{morph.parse(type1)[0].tag.gender}'}).word.capitalize()} {morph.parse(type1)[0].inflect({'nomn'}).word} и {morph.parse(color2)[0].inflect({'nomn', f'{morph.parse(type2)[0].tag.number}', f'{morph.parse(type2)[0].tag.gender}'}).word} {type2} {circle_color(color2)}")
                        elif (color1 in ['Белый', 'Чёрный']) and type1 != type2:
                            if morph.parse(type2)[0].tag.number == 'plur':
                                outfits.append(f"🕶 Будут хорошо смотреться 🕶\n{circle_color(color1)} {morph.parse(color1)[0].inflect({'nomn', f'{morph.parse(type1)[0].tag.number}', f'{morph.parse(type1)[0].tag.gender}'}).word.capitalize()} {morph.parse(type1)[0].inflect({'nomn'}).word} и {morph.parse(color2)[0].inflect({'nomn', f'{morph.parse(type2)[0].tag.number}'}).word} {type2} {circle_color(color2)}")                            
                            else:
                                outfits.append(f"🕶 Будут хорошо смотреться 🕶\n{circle_color(color1)} {morph.parse(color1)[0].inflect({'nomn', f'{morph.parse(type1)[0].tag.number}', f'{morph.parse(type1)[0].tag.gender}'}).word.capitalize()} {morph.parse(type1)[0].inflect({'nomn'}).word} и {morph.parse(color2)[0].inflect({'nomn', f'{morph.parse(type2)[0].tag.number}', f'{morph.parse(type2)[0].tag.gender}'}).word} {type2} {circle_color(color2)}")
                elif type1 in ['брюки', 'юбка', 'сумка']:
                    for j, item2 in enumerate(outfit):
                        if j <= i:
                            continue
                        type2, color2 = list(item2.keys())[0], list(item2.values())[0]
                        if type1 != type2 and (color1 not in ['Белый', 'Чёрный']) and opposite_color(color1) == color2:
                            if morph.parse(type1)[0].tag.number == 'plur':
                                outfits.append(f"🕶 Будут хорошо смотреться 🕶\n{circle_color(color1)} {morph.parse(color1)[0].inflect({'nomn', f'{morph.parse(type1)[0].tag.number}'}).word.capitalize()} {type1} и {morph.parse(color2)[0].inflect({'nomn', f'{morph.parse(type2)[0].tag.number}', f'{morph.parse(type2)[0].tag.gender}'}).word} {type2} {circle_color(color2)}")
                            else:
                                outfits.append(f"🕶 Будут хорошо смотреться 🕶\n{circle_color(color1)} {morph.parse(color1)[0].inflect({'nomn', f'{morph.parse(type1)[0].tag.number}', f'{morph.parse(type1)[0].tag.gender}'}).word.capitalize()} {morph.parse(type1)[0].inflect({'nomn'}).word} и {morph.parse(color2)[0].inflect({'nomn', f'{morph.parse(type2)[0].tag.number}', f'{morph.parse(type2)[0].tag.gender}'}).word} {type2} {circle_color(color2)}")
                        elif (color1 in ['Белый', 'Чёрный']) and type1 != type2:
                            if morph.parse(type1)[0].tag.number == 'plur':
                                outfits.append(f"🕶 Будут хорошо смотреться 🕶\n{circle_color(color1)} {morph.parse(color1)[0].inflect({'nomn', f'{morph.parse(type1)[0].tag.number}'}).word.capitalize()} {type1} и {morph.parse(color2)[0].inflect({'nomn', f'{morph.parse(type2)[0].tag.number}', f'{morph.parse(type2)[0].tag.gender}'}).word} {type2} {circle_color(color2)}")
                            else:
                                outfits.append(f"🕶 Будут хорошо смотреться 🕶\n{circle_color(color1)} {morph.parse(color1)[0].inflect({'nomn', f'{morph.parse(type1)[0].tag.number}', f'{morph.parse(type1)[0].tag.gender}'}).word.capitalize()} {morph.parse(type1)[0].inflect({'nomn'}).word} и {morph.parse(color2)[0].inflect({'nomn', f'{morph.parse(type2)[0].tag.number}', f'{morph.parse(type2)[0].tag.gender}'}).word} {type2} {circle_color(color2)}")

                            

                else:
                   outfits.append(f"Неизвестный тип элемента: {type1}")
        return outfits