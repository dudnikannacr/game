import mysql.connector
from mysql.connector import errorcode
import os
from City import City


class Database:
    def __init__(self):
        self._db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="qwerty13",
        )
        db_name = "cities_db"

        self._cursor = self._db.cursor()
        # self._cursor.execute("DROP DATABASE IF EXISTS {}".format(db_name))

        self._cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(db_name))
        self._cursor.execute("USE {}".format(db_name))
        TABLES = {}
        TABLES['cities'] = (
            "CREATE TABLE IF NOT EXISTS `cities` ("
            "  `id` int(11) NOT NULL AUTO_INCREMENT,"
            "  `name` varchar(255) NOT NULL,"
            "  PRIMARY KEY (`id`)"
            ")"
        )
        TABLES['used_cities'] = (
            "CREATE TABLE  IF NOT EXISTS used_cities ("
            "  id int(11) NOT NULL AUTO_INCREMENT,"
            "  city_id int(11) NOT NULL,"
            "  PRIMARY KEY (id),"
            "  FOREIGN KEY (city_id) REFERENCES cities(id)"
            ")"
        )
        for table_name in TABLES:
            table_description = TABLES[table_name]
            try:
                print("Creating table: {}".format(table_name))
                self._cursor.execute(table_description)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)

        current_dir = os.getcwd()
        cities_file = os.path.join(current_dir, 'cities.txt')
        cities_list = open(cities_file).read().splitlines()
        add_city = "INSERT INTO cities (name) VALUES ('{}')"

        # for city in cities_list:
        #     try:
        #         sql = add_city.format(city)
        #         self._cursor.execute(sql)
        #     except mysql.connector.Error as err:
        #             print(err.msg)
        # self._db.commit()

        #
        # add_city = "INSERT INTO cities (name) VALUES ('{}')"
        # self._cursor.executemany(add_city.format(city))


    def __del__(self):
        try:
            self._db.close()
        except mysql.connector.Error as err:
            print(err.msg)

    def get_cities(self):
        query = "SELECT * FROM cities"
        # try:
        #     self._cursor.execute(query)
        # except mysql.connector.Error as err:
        #     print(err.msg)
        # for (id, name) in self._cursor:
        #     print("{}, {}".format(id, name))
        self._cursor.execute(query)
        cities = self._cursor.fetchall()
        return cities

    def find_city(self, name):
        try:
            query = "SELECT * FROM cities WHERE name = %s"
            self._cursor.execute(query, (name, ))
            city = self._cursor.fetchone()
            if city is not None:
                return City(city_id=city[0], name=city[1])
        except mysql.connector.Error as err:
            print(err.msg)

    def get_cities_started_on(self, letter):
        not_allowed_letters = ['Ь', 'Ъ', 'Э', 'Ы', 'Й']
        if letter in not_allowed_letters:
            return []
        query = "SELECT cities.id, name FROM cities LEFT JOIN used_cities ON cities.id = used_cities.city_id " \
                "WHERE used_cities.city_id is NULL AND cities.name LIKE %s"
        self._cursor.execute(query, (letter + "%",))
        cities = self._cursor.fetchall()
        return cities

    def get_last_used_city(self):
        try:
            query = "SELECT city_id FROM used_cities ORDER BY id DESC LIMIT 1"
            self._cursor.execute(query)
            last_id = self._cursor.fetchone()
            query = "SELECT id, name FROM cities WHERE id = %s"
            self._cursor.execute(query, last_id)
            city = self._cursor.fetchone()
            if city is not None:
                return City(city_id=city[0], name=city[1])
        except mysql.connector.Error as err:
                print(err.msg)

    def get_valid_cities(self):
        last_city = self.get_last_used_city()
        if last_city is None:
            return self.get_cities()
        else:
            last_letter = last_city.name[-1]
            penultimate_letter = last_city.name[-2]
            valid_cities = self.get_cities_started_on(last_letter)
            if len(valid_cities) > 0:
                return valid_cities
            else:
                return self.get_cities_started_on(penultimate_letter)

    def city_is_used(self, city):
        query = "SELECT * FROM used_cities WHERE city_id = %s"
        self._cursor.execute(query, (city.city_id,))
        city = self._cursor.fetchone()
        if city is None:
            return False
        else:
            return True

    def set_used_flag(self, city):
        query = "INSERT INTO used_cities (city_id) VALUES ('{}')"
        try:
            add_flag = query.format(city.city_id)
            self._cursor.execute(add_flag)
        except mysql.connector.Error as err:
                print(err.msg)
        self._db.commit()

    def get_valid_city_from_user(self):
        answered = False
        answer = input("Please enter a city: \n")
        while not answered:
            if len(answer) <= 2:
                answer = input("City is too short. Try again \n")
                continue
            else:
                user_city = self.find_city(name=answer)
                if user_city is None:
                    answer = input("City isn't exist. Try again: \n")
                    continue
                elif self.city_is_used(user_city):
                    print("City is already used. Try again: \n")
                    continue
                
                else:
                    self.set_used_flag(city=user_city)
                    return user_city
                    answered = True

    def computer_answer(self):
        valid_cities = self.get_valid_cities()[0][1]
        if len(valid_cities)>0:
            print("Computer answer: \n {}".format(self.get_valid_cities()[0][1]))
        else:
            print("All cities are used. The end of game")

    def play(self):
        end = False
        while not end:
            user_answer = self.get_valid_city_from_user()
            if user_answer in self.get_valid_cities():
                self.computer_answer()
                continue
            else:
                print("Wrong first letter. Try again: \n")
                continue





db1 = Database()
db1.get_cities()
# found_city = db1.find_city("ялуторовсК")
db1.play()
#
# city = City(city_id=41, name="Днипро")
# db1.set_used_flag(city)
# print(db1.get_valid_cities(city))

# print(db1.can_use_city(found_city))