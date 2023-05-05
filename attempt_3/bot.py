from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
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
    await message.bot.send_message(message.from_user.id, "Добро пожаловать!")


# Основной код: При скидывании фоток, я вызываю соответсвующие функии из файла main.py и передаю им параметры. код всё обрабатывает и записывает в users.json
@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    photo = message.photo[-1]
    photo_file = await bot.download_file_by_id(photo.file_id)
    with open(f"{photo.file_id}.jpg", "wb") as f:
        f.write(photo_file.read())
    fashion = Predict.fashion(photo_file, photo)
    await bot.send_message(message.chat.id, text=f"На фото: {fashion}")
    photo_file = await bot.download_file_by_id(photo.file_id)
    colour = Color.find(photo_file, photo)
    await bot.send_message(message.chat.id, text=f"Цвет: {colour}")

    data = JsonFile.read("users.json")
    data[f"{message.from_user.id}"].append({
        f"{fashion}": f"{colour}"
    })
    JsonFile.write(data, "users.json")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
