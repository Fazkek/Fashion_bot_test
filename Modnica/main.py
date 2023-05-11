from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import asyncio
import config
import pymorphy2
from random import shuffle
from main import JsonFile, Predict, Color, Recomend

bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


# Здесь я добавляю пользователя в файл users.json при нажатии на /start
@dp.message_handler(commands="start")
async def start(message: types.Message):
    data = JsonFile.read("users.json")
    data[f"{message.from_user.id}"] = []
    JsonFile.write(data, "users.json")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = types.KeyboardButton(text="Проверить гардероб ✔️")
    button_2 = types.KeyboardButton(text="Удалить последнюю вещь ❌️")    
    button_3 = types.KeyboardButton(text="Получить рекомендацию 👑")    

    keyboard.add(button_1, button_2, button_3)
    await message.bot.send_message(message.from_user.id, "🌺Добро пожаловать 🌺")
    await asyncio.sleep(1)
    await message.bot.send_message(message.from_user.id, "👕Смотри, что я умею:👖\n"\
"1. Чтобы дополнить свой гардероб, отправь фото вещи, которую хочешь добавить📷\n"\
"2. Чтобы проверить, какие вещи у тебя в гардеробе, нажми 'Проверить гардероб ✔️'\n"\
"3. Чтобы удалить последнюю добавленную вещь, нажми 'Удалить последнюю вещь ❌️''\n"\
"4. Чтобы получить модный совет, нажми 'Получить рекомендацию 👑'", reply_markup=keyboard)

# Основной код: При скидывании фоток, я вызываю соответсвующие функии из файла main.py и передаю им параметры. код всё обрабатывает и записывает в users.json
@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    photo = message.photo[-1]
    photo_file = await bot.download_file_by_id(photo.file_id)

    with open(f"{photo.file_id}.jpg", "wb") as f:
        f.write(photo_file.read())
    fashion = Predict.fashion(photo)
    await bot.send_message(message.chat.id, text=f"На фото: {fashion}")


    colour = Color.find(photo)
    await bot.send_message(message.chat.id, text=f"Цвет: {colour}")

    data = JsonFile.read("users.json")
    data[f"{message.from_user.id}"].append({
        f"{fashion}": f"{colour}"
    })
    JsonFile.write(data, "users.json")


@dp.message_handler(content_types=['text'])
async def main(message: types.Message):
    if message.text == 'Проверить гардероб ✔️':
        data = JsonFile.read("users.json")
        if len(data[f'{message.from_user.id}']) == 0:
             await message.bot.send_message(message.from_user.id, "‼️❌️В вашем гардеробе нет вещей❌️‼️")
        else:
            await message.bot.send_message(message.from_user.id, "🎩Готово. Ваш гардероб:🎩")
            clothes = ''
            morph = pymorphy2.MorphAnalyzer()
            for i in range(len(data[f'{message.from_user.id}'])):
                for key, value in data[f'{message.from_user.id}'][i].items():
                        if morph.parse(key)[0].tag.number == 'plur':
                            clothes += f"{i+1}) {morph.parse(value)[0].inflect({'nomn', f'{morph.parse(key)[0].tag.number}'}).word.capitalize()} {key}\n"
                        else:
                            clothes += f"{i+1}) {morph.parse(value)[0].inflect({'nomn', f'{morph.parse(key)[0].tag.number}', f'{morph.parse(key)[0].tag.gender}'}).word.capitalize()} {key}\n"
                             

            await message.bot.send_message(message.from_user.id, clothes)


    elif message.text == 'Удалить последнюю вещь ❌️':
        data = JsonFile.read("users.json")
        if len(data[f'{message.from_user.id}']) == 0:
             await message.bot.send_message(message.from_user.id, "‼️❌️В вашем гардеробе нет вещей❌️‼️")
        else:
            data[f'{message.from_user.id}'].pop()
            JsonFile.write(data, "users.json")

            await message.bot.send_message(message.from_user.id, "Готово. Вот ваш гардероб:")

            clothes = ''
            for i in range(len(data[f'{message.from_user.id}'])):
                for key, value in data[f'{message.from_user.id}'][i].items():
                        clothes += f"{i+1}) {key}: {value}\n"

            await message.bot.send_message(message.from_user.id, clothes)


    elif message.text == 'Получить рекомендацию 👑': 
        data = JsonFile.read('users.json')
        if len(data[f'{message.from_user.id}']) == 0:
            await message.bot.send_message(message.from_user.id, "‼️❌️В вашем гардеробе нет вещей❌️‼️")
        else:
            rec = Recomend.recommend_outfit({f'{message.from_user.id}': data[f'{message.from_user.id}']})
            shuffle(rec)
            try:
                await message.bot.send_message(message.from_user.id, rec[0])
            except IndexError:
                await message.bot.send_message(message.from_user.id, "К сожалению, ничего не нашлось 😔")
                await asyncio.sleep(0.5)
                await message.bot.send_message(message.from_user.id, "Попробуйте отправить мне ещё фотографий.")
                await asyncio.sleep(0.5)
                await message.bot.send_message(message.from_user.id, "Вот вам универсальный совет: \n Надевайте вещи одного тона и вы всегда будете выглядеть стильно 👍")
    else:
        await message.bot.send_message(message.from_user.id, "⛔️Команда отсутствует ⛔️")
        

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)