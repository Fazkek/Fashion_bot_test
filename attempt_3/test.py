from sklearn.cluster import KMeans

color = (0, 127, 0)
color = [color]

color_names = {
    (0, 0, 0): "голубой",
    (128, 128, 128): "серый",
    (255, 0, 0): "красный",
    (0, 128, 0): "зелёный",
    (0, 0, 255): "синий",
    (0, 255, 255): "чёрный",
    (255, 255, 255): "белый",
    (255, 165, 0): "оранжевый",
    (255, 255, 0): "жёлтый",
    (128, 0, 128): "фиолетовый",
    (165, 42, 42): "коричневый",
    (255, 192, 203): "розовый"
}

colors = list(color_names.keys())

kmeans = KMeans(n_clusters=12, random_state=0, n_init=12).fit(colors)
print(color)

predicted_label = kmeans.predict(color)

closest_color = colors[predicted_label[0]]
closest_color_name = color_names[closest_color]

print("Ваш цвет наиболее близок к цвету:", closest_color_name)