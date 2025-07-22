import requests
from tkinter import Tk, Label, Frame, Button, Entry, Menu
from tkintermapview import TkinterMapView
import API_key


class WeatherApp:
    def __init__(self):
        self.master = Tk()
        self.master.title("Погода на карте")
        self.master.geometry("1000x700")
        self.api_key = API_key.API_key  # Твой API-ключ

        # Создаём меню
        self.menu_bar = Menu(self.master)
        self.master.config(menu=self.menu_bar)

        self.favorites_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Избранное", menu=self.favorites_menu)
        self.favorites_menu.add_command(label="Очистить избранное",
                                        command=self.clear_favorites)

        # Фрейм ввода
        self.top_frame = Frame(self.master, height=100)
        self.top_frame.pack(fill="x", padx=10, pady=5)

        Label(self.top_frame, text="Введите адрес:", font=("Arial", 12)).grid(row=0, column=0,
                                                                              padx=5, pady=5, sticky="w")
        self.address_entry = Entry(self.top_frame, font=("Arial", 12), width=30)
        self.address_entry.grid(row=0, column=1, padx=5, pady=5)

        self.search_button = Button(self.top_frame, text="Найти",
                                    font=("Arial", 12), command=self.search_address)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)

        self.weather_info_label = Label(self.top_frame, text="Выберите место на карте", font=("Arial", 12))
        self.weather_info_label.grid(row=1, column=0, columnspan=3, pady=5)

        self.add_favorite_button = Button(self.top_frame, text="Добавить в избранное",
                                          font=("Arial", 12), command=self.add_to_favorites)
        self.add_favorite_button.grid(row=2, column=0, columnspan=3, pady=5)

        # Карта
        self.map_widget = TkinterMapView(self.master, width=800, height=500)
        self.lat, self.lon = 55.751244, 37.618423
        self.map_widget.set_position(self.lat, self.lon)  # Москва по умолчанию
        self.map_widget.set_zoom(10)
        self.map_widget.pack(fill="both", expand=True, padx=10, pady=5)
        self.map_widget.add_left_click_map_command(self.on_map_click)

        # Избранные города
        self.favorites = {}

    def search_address(self):
        city_name = self.address_entry.get()
        if city_name:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&lang=ru&appid={self.api_key}"
            try:
                response = requests.get(url)
                data = response.json()

                # Получаем данные о координатах и погоде
                self.lat, self.lon = data["coord"]["lat"], data["coord"]["lon"]
                weather_info = f"{data['name']}: {data['main']['temp']}°C, {data['weather'][0]['description']}"
                self.weather_info_label.config(text=weather_info)

                # Перемещаем карту на указанные координаты
                self.map_widget.set_position(self.lat, self.lon)

            except requests.exceptions.HTTPError as e:
                self.weather_info_label.config(text="Город не найден. Попробуй другой.")
            except Exception as e:
                self.weather_info_label.config(text="Ошибка при обработке данных.")

    def on_map_click(self, coords):
        self.lat, self.lon = coords
        weather = self.get_weather(self.lat, self.lon)
        if weather:
            self.weather_info_label.config(text=f"{weather['name']}: {weather['temp']}°C, {weather['description']}")
        else:
            self.weather_info_label.config(text="Не удалось получить данные о погоде.")

    def get_weather(self, lat, lon):
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&units=metric&lang=ru&appid={self.api_key}"
        try:
            response = requests.get(url)
            data = response.json()
            return {
                "name": data["name"],
                "temp": data["main"]["temp"],
                "description": data["weather"][0]["description"]
            }
        except Exception as e:
            print(f"Ошибка при получении данных о погоде: {e}")
            return None

    def add_to_favorites(self):
        current_city = self.weather_info_label.cget("text")
        if "Выберите место" not in current_city:
            self.favorites[current_city] = (float(self.lat), float(self.lon))
            self.favorites_menu.add_command(label=current_city,
                                            command=lambda: self.show_favorite(current_city))

    def show_favorite(self, favorite):
        self.weather_info_label.config(text=favorite)
        self.map_widget.set_position(*self.favorites[favorite])

    def clear_favorites(self):
        self.favorites = {}
        self.favorites_menu.delete(0, "end")

    def run(self):
        self.master.mainloop()


if __name__ == "__main__":
    app = WeatherApp()
    app.run()