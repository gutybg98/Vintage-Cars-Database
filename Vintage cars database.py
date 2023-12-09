import requests
import json


BASE_URL = 'http://localhost:3000'
CAR_ENDPOINT = f'{BASE_URL}/cars'

KEY_WIDTHS = {'id': 10, 'brand': 15, 'model': 10,
              'production_year': 20, 'convertible': 15}


def check_server(car_id=None):
    # returns True or False;
    # when invoked without arguments simply checks if server responds;
    # invoked with car ID checks if the ID is present in the database;
    try:
        response = requests.get(
            BASE_URL if car_id is None else f'{CAR_ENDPOINT}/{car_id}')
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


def print_menu():
    # prints user menu - nothing else happens here;
    print('+' + '-' * 35 + '+')
    print('|' + ' ' * 7 + 'Vintage Cars Database' + ' ' * 7 + '|')
    print('+' + '-' * 35 + '+')
    print('M E N U')
    print('=======')
    print('1. List cars')
    print('2. Add new car')
    print('3. Delete car')
    print('4. Update car')
    print('0. Exit')


def read_user_choice():
    # reads user choice and checks if it's valid;
    # returns '0', '1', '2', '3' or '4'
    user_choice = input('Enter your choice (0..4): ')
    if user_choice.isdigit() and 0 <= int(user_choice) <= 4:
        return user_choice
    return None


def print_header():
    # prints elegant cars table header;
    for key, width in KEY_WIDTHS.items():
        print(key.ljust(width), end='| ')
    print()


def print_car(car):
    # prints one car's data in a way that fits the header;
    for key, width in KEY_WIDTHS.items():
        print(str(car[key]).ljust(width), end='| ')
    print()


def list_cars():
    # gets all cars' data from server and prints it;
    # if the database is empty prints diagnostic message instead;
    try:
        response = requests.get(CAR_ENDPOINT)
        response.raise_for_status()
        cars = response.json()
        if cars:
            print_header()
            for car in cars:
                print_car(car)
        else:
            print('*** Database is empty ***')
        print()
    except requests.RequestException as e:
        print(f'Error retrieving cars: {e}')


def name_is_valid(name):
    # checks if name (brand or model) is valid;
    # valid name is non-empty string containing
    # digits, letters and spaces;
    # returns True or False;
    for char in name:
        if not char.isalnum() and not char.isspace():
            return False
    return True


def enter_id():
    # allows user to enter car's ID and checks if it's valid;
    # valid ID consists of digits only;
    # returns int or None (if user enters an empty line);
    id = input('Car ID (empty string to exit): ')
    try:
        id = int(id)
        return id
    except:
        return None


def enter_production_year():
    # allows user to enter car's production year and checks if it's valid;
    # valid production year is an int from range 1900..2000;
    # returns int or None  (if user enters an empty line);
    production_year = input('Car production year (empty string to exit): ')
    try:
        if int(production_year) in range(1900, 2001):
            return int(production_year)
        else:
            return None
    except:
        return None


def enter_name(what):
    # allows user to enter car's name (brand or model) and checks if it's valid;
    # uses name_is_valid() to check the entered name;
    # returns string or None  (if user enters an empty line);
    # argument describes which of two names is entered currently ('brand' or 'model');
    name = input('Car ' + what + ' (empty string to exit): ')
    if not name:
        return None
    elif name_is_valid(name):
        return name
    else:
        print("Invalid characters")
        return None


def enter_convertible():
    # allows user to enter Yes/No answer determining if the car is convertible;
    # returns True, False or None  (if user enters an empty line);
    convertible = input(
        'Is this car convertible? [y/n] (empty string to exit): ')
    if convertible == 'y':
        return True
    elif convertible == 'n':
        return False
    else:
        return None


def delete_car():
    # asks user for car's ID and tries to delete it from database;
    id = input('Car ID (empty string to exit): ')
    if id:
        if check_server(id):
            requests.delete('http://localhost:3000/cars/' + id)
            print('Success!')
        else:
            print("Car ID not found")
            return None
    else:
        return None


def input_car_data(with_id):
    # lets user enter car data;
    # argument determines if the car's ID is entered (True) or not (False);
    # returns None if user cancels the operation or a dictionary of the following structure:
    # {'id': int, 'brand': str, 'model': str, 'production_year': int, 'convertible': bool }
    if with_id:
        id = enter_id()
        if not id or check_server(id):
            return None
    brand = enter_name('brand')
    if not brand:
        return None
    model = enter_name('model')
    if not model:
        return None
    production_year = enter_production_year()
    if not production_year:
        return None
    convertible = enter_convertible()
    if convertible == None:
        return None
    if with_id:
        new_car = {'id': id, 'brand': brand, 'model': model,
                   'production_year': production_year, 'convertible': convertible}
    else:
        new_car = {'brand': brand, 'model': model,
                   'production_year': production_year, 'convertible': convertible}
    return new_car


def add_car():
    # invokes input_car_data(True) to gather car's info and adds it to the database;
    headers = {'Content-Type': 'application/json'}
    new_car = input_car_data(with_id=True)
    if new_car:
        try:
            response = requests.post(
                CAR_ENDPOINT, headers=headers, data=json.dumps(new_car))
            response.raise_for_status()
            print('Car added successfully!')
        except requests.RequestException as e:
            print(f'Error adding car: {e}')


def update_car():
    # invokes enter_id() to get car's ID if the ID is present in the database;
    # invokes input_car_data(False) to gather new car's info and updates the database;
    car_id = enter_id()
    if car_id and check_server(car_id):
        headers = {'Content-Type': 'application/json'}
        updated_car = {'id': car_id}
        try:
            updated_car.update(input_car_data(with_id=False))
        except TypeError:
            return None
        try:
            response = requests.put(
                f'{CAR_ENDPOINT}/{car_id}', headers=headers, data=json.dumps(updated_car))
            response.raise_for_status()
            print('Car updated successfully!')
        except requests.RequestException as e:
            print(f'Error updating car: {e}')


if __name__ == "__main__":
    while True:
        if not check_server():
            print('Server is not responding - quitting!')
            exit(1)

        print_menu()
        choice = read_user_choice()
        if choice == '0':
            print('Bye!')
            exit(0)
        elif choice == '1':
            list_cars()
        elif choice == '2':
            add_car()
        elif choice == '3':
            delete_car()
        elif choice == '4':
            update_car()
