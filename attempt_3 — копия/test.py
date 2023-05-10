outfits_dict = {
    '1161388698': [
        {'рубашка': 'фиолетовый'}, {'футболка': 'светло-голубой'}, 
        {'футболка': 'сиреневый'}, {'брюки': 'неопределённый'}, 
        {'рубашка': 'светло-голубой'}
    ],
    '6188130935': [
        {'брюки': 'неопределённый'}, {'футболка': 'сиреневый'}, 
        {'футболка': 'светло-голубой'}, {'рубашка': 'фиолетовый'}, 
        {'футболка': 'сиреневый'}
    ]
}

def recommend_color_outfit(color, outfits_dict):
    """
    Функция, которая выводит на экран все элементы одежды с заданным цветом в словаре outfits_dict
    :param color: str, цвет, по которому ищем элементы одежды
    :param outfits_dict: dict, словарь с элементами одежды
    """
    for outfit in outfits_dict.values():
        for item in outfit:
            for key, value in item.items():
                if value == color:
                    print(f"{key}: {value}")

recommend_color_outfit('сиреневый', outfits_dict)