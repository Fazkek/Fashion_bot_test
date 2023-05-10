from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import asyncio
import config
from main import JsonFile, Predict, Color

bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


# Здесь я добавляю пользователя в файл users.json при нажатии на /start
@dp.message_handler(commands="start")
async def start(message: types.Message):
    data = JsonFile.read("users.json")
    data[f"{message.from_user.id}"] = []
    JsonFile.write(data, "users.json")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = types.KeyboardButton(text="Проверить гардероб")    
    keyboard.add(button_1)
    await message.bot.send_message(message.from_user.id, "Добро пожаловать!")
    await asyncio.sleep(1)
    await message.bot.send_message(message.from_user.id, """Вот что я умею:\n Вы отправляете мне свой гардероб. И когда вы захотите выйти на улицу, то я скину вам то, что вам надеть (исходя из базовых правил моды)""", reply_markup=keyboard)

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
    if message.text == 'Проверить гардероб':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_1 = types.KeyboardButton(text="Проверить гардероб")    
        keyboard.add(button_1)  
        await message.bot.send_message(message.from_user.id, "Вот ваши вещи (Виберите вещь под n цифрой)", reply_markup=keyboard)
        data = JsonFile.read("users.json")
        for i in range(len(data[f'{message.from_user.id}'])):
            for key, value in data[f'{message.from_user.id}'][i].items():
                await message.bot.send_message(message.from_user.id, f"{i+1} {key}: {value}")
        

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
