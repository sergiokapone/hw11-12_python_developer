import re
from collections import UserDict

import pickle
import csv
from datetime import datetime


# ================================== Classes =================================#


"""
- Записи <Record> у <AddressBook> зберігаються як значення у словнику.
  В якості ключів використовується значення <Record.name.value>.
- <Record> зберігає об'єкт <Name> в окремому атрибуті.
- <Record> зберігає список об'єктів <Phone> в окремому атрибуті.
- <Record> реалізує методи додавання/видалення/редагування об'єктів <Phone>.
- <AddressBook> реалізує метод <add_record>, який додає <Record> у <self.data>.

"""


class Field:
    """Клас є батьківським для всіх полів, у ньому реалізується логіка,
    загальна для всіх полів."""

    def __init__(self, value: str):
        self.__value = value
        self.value = value

    @property
    def value(self):
        return self.__value

    def __eq__(self, other):
        return self.value == other.value


class Name(Field):
    """Клас --- обов'язкове поле з ім'ям."""

    @Field.value.setter
    def value(self, value):
        self.__value = value


class Phone(Field):
    """Клас -- необов'язкове поле з телефоном та таких один записів (Record)
    може містити кілька."""

    @Field.value.setter
    def value(self, value):
        if not bool(re.match(r"\d{10}", value)) or len(value) > 10:
            raise ValueError("Phone number must be 10 digits")
        self.__value = value


class Birthday(Field):
    """Клас -- необов'язкове поле з датою народження."""

    @Field.value.setter
    def value(self, value):
        try:
            date = datetime.strptime(value, "%d.%m.%Y")
        except (TypeError, ValueError):
            raise ValueError("Invalid date format. Please use DD.MM.YYYY")
        if date > datetime.today():
            raise ValueError("Date cannot be in the future")
        self.__value = date


class Record:
    """Клас відповідає за логіку додавання/видалення/редагування
    необов'язкових полів та зберігання обов'язкового поля Name."""

    def __init__(
        self,
        name: Name,
        phones: list[Phone] = None,
        birthday: Birthday = None,
    ):

        self.name = name  # Name --- атрибут ля зберігання об'єкту Name
        self.phones = phones or []
        self.birthday = birthday

    def add_birthday(self, birthday: Birthday):
        """Метод додає об'єкт день народження до запису."""

        self.birthday = birthday

    def add_phone(self, phone: Phone):
        """Метод додає об'єкт телефон до запису."""

        self.phones.append(phone)

    def remove_phone(self, phone: Phone):
        """Метод видаляє об'єкт телефон із запису."""

        self.phones.remove(phone)

    def change_phone(self, old_phone: Phone, new_phone: Phone) -> bool:
        """Метод змінює об'єкт телефон в записі на новий."""

        for phone in self.phones:
            if phone == old_phone:
                self.phones.remove(phone)
                self.phones.append(new_phone)
                return True
            return False

    def show_phones(self):

        phones = ", ".join(phone.value for phone in self.phones) or "-"
        return phones

    def show_birthday(self):

        birthday = getattr(self.birthday, "value", None) or "-"
        return birthday

        name = getattr(self.name, "value", False)
        return name

    def days_to_birthday(self) -> int:
        """Метод повертає кількість днів до наступного дня народження контакту."""

        if not self.birthday:
            return None

        today = datetime.today()
        dt_birthday = datetime.strptime(self.birthday.value, "%d.%m.%Y")
        next_birthday = dt_birthday.replace(year=today.year)

        if next_birthday < today:
            next_birthday = dt_birthday.replace(year=today.year + 1)

        return (next_birthday - today).days


class AddressBook(UserDict):
    """Клас містить логіку пошуку за записами до цього класу."""

    def add_record(self, record: Record):
        """Метод додає запис до списку контактів."""

        self.data[record.name.value] = record

    def save_contacts(self, filename):
        with open(filename, "wb") as file:
            pickle.dump(list(self.data.items()), file)

    def load_contacts(self, filename):
        with open(filename, "rb") as file:
            data = pickle.load(file)
            self.clear()
            self.update(data)

    def search(self, search_string):
        """Метод шукає записи  по ключовому слову."""

        results = AddressBook()
        for key in self.data:
            record = self.data[key]
            if (
                search_string in record.name.value
                or (
                    getattr(record.birthday, "value", False)
                    and search_string in record.birthday.value
                )
                or any(search_string in phone.value for phone in record.phones)
            ):
                results.add_record(record)
        return results

    def export_to_csv(self, filename):
        """Експорт записів із AddressBook в CSV-файл"""

        with open(filename, "w", newline="") as csvfile:
            fieldnames = ["name", "birthday", "phones"]
            writer = csv.DictWriter(
                csvfile, fieldnames=fieldnames, delimiter="|"
            )
            writer.writeheader()
            for record in self.data.values():
                writer.writerow(
                    {
                        "name": record.name.value,
                        "phones": record.show_phones(),
                        "birthday": record.show_birthday(),
                    }
                )

    def import_from_csv(self, filename):
        """Імпорт записів із CSV-файлу в AddressBook"""

        with open(filename, newline="") as csvfile:
            reader = csv.DictReader(csvfile, delimiter="|")
            for row in reader:
                name = row["name"]
                phones = [
                    Phone(phone.strip())
                    for phone in row["phones"].split(",")
                    if phone.strip() and row["phones"] != "-"
                ]
                birthday = (
                    Birthday(row["birthday"])
                    if row["birthday"] != "-"
                    else None
                )
                record = Record(
                    name=Name(name), phones=phones, birthday=birthday
                )
                self.add_record(record)

    def iterator(self, n: int = 10):
        """Метод ітерується по записам і виводить їх частинами по n-штук."""

        data_items = list(self.data.items())
        for i in range(0, len(data_items), n):
            data_slice = dict(data_items[i: i + n])
            yield data_slice
            if i + n < len(data_items):
                yield "continue"
