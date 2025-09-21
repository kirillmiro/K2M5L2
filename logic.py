import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


class DB_Map():
    def __init__(self, database):
        self.database = database
    

    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                marker_color TEXT DEFAULT 'red',
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self, user_id, city_name, color="red"):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                conn.execute('INSERT INTO users_cities (user_id, city_id, marker_color) VALUES (?, ?, ?)',
                             (user_id, city_id, color))
                conn.commit()
                return 1
            else:
                return 0

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city, users_cities.marker_color
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            return cursor.fetchall()  # [(city, color), (city, color), ...]

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    def create_grapf(self, path, cities_with_colors):
        """
        cities_with_colors — список кортежей [(city, color), ...]
        """
        coordinates = []
        for city, color in cities_with_colors:
            coords = self.get_coordinates(city)
            if coords:
                coordinates.append((city, coords[0], coords[1], color))

        if not coordinates:
            return None

        fig = plt.figure(figsize=(12, 6))
        ax = plt.axes(projection=ccrs.PlateCarree())
        
        # Фон и географические объекты
        ax.stock_img()
        ax.coastlines()
        ax.add_feature(cfeature.BORDERS, linewidth=0.5)  # границы стран
        ax.add_feature(cfeature.LAKES, alpha=0.5)       # озёра
        ax.add_feature(cfeature.RIVERS)                 # реки

        for city, lat, lng, color in coordinates:
            ax.plot(lng, lat, marker='o', color=color, markersize=6, transform=ccrs.PlateCarree())
            ax.text(lng + 1, lat + 1, city, fontsize=8, transform=ccrs.PlateCarree())

        plt.savefig(path, bbox_inches='tight')
        plt.close()
        return path

    def draw_distance(self, city1, city2):
        pass


if __name__ == "__main__":
    m = DB_Map(DATABASE)
    m.create_user_table()
