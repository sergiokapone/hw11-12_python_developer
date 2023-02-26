import re
from prettytable import PrettyTable
from botmodule import Name, Phone, Birthday, Record, AddressBook

# ============================ Tables decoration =============================#


def build_table(data):
    """Функция строит PrettyTable для заданного списка записей."""
    table = PrettyTable()
    table.field_names = ["Name", "Birthday", "Phones"]
    table.min_width.update({"Name": 20, "Birthday": 12, "Phones": 40})
    data = AddressBook(data)
    for key in data:
        record = data[key]
        name = record.name.value
        birthday = record.show_birthday()
        phones = record.show_phones()
        table.add_row([name, birthday, phones])
    return table


# ================================= Decorator ================================#


def input_error(func):
    def wrapper(*func_args, **func_kwargs):
        try:
            return func(*func_args, **func_kwargs)
        except KeyError as error:
            if "name" in str(error):
                return "\033[31mGive me a name, please\033[0m"
        except ValueError as error:
            return str(error)
        except TypeError as error:
            return str(error)
        except FileNotFoundError:
            return "\033[31mFile not found\033[31m"

    return wrapper


# ================================== handlers ================================#


def hello(*args):
    return "\033[32mHow can I help you?\033[0m"


def good_bye(*args):
    contacts.save_contacts("contacts")
    return "\033[32mGood bye!\033[0m"


def undefined(*args):
    return "\033[32mWhat do you mean?\033[0m"


def show_all(*args):
    """Функция-handler показує книгу контактів."""
    return f"\033[32mAddress book contain {len(contacts)} contacts\033[0m"


@input_error
def save(*args):
    contacts.save_contacts(args[0])
    return f"File {args[0]} saved"


@input_error
def load(*args):
    contacts.load_contacts(args[0])
    return f"File {args[0]} loaded"


@input_error
def set_birthday(*args):
    """Функція-handler додає день народження до контакту."""

    if not args[0]:
        raise KeyError("Give me a name, please")

    name, birthday = Name(args[0]), Birthday(args[1])

    if name.value in contacts.data:
        record = contacts.data[name.value]
    else:
        record = Record(name)
        contacts.add_record(record)
    record.add_birthday(birthday)

    return f"I added a birthday {args[1]} to contact {args[0]}"


@input_error
def add(*args):
    """Добавляет телефонный номер в контакт по имени."""

    if not args[0]:
        raise KeyError("Give me a name, please")

    name, phone = Name(args[0]), Phone(args[1])

    if name.value in contacts.data:
        record = contacts.data[name.value]
    else:
        record = Record(name)
        contacts.add_record(record)
    record.add_phone(phone)

    return f"I added a phone {args[1]} to contact {args[0]}"


@input_error
def phones(*args):
    """Функція-handler показує телефонні номери відповідного контакту."""

    if not args[0]:
        raise KeyError("Give me a name, please")

    table = PrettyTable()
    table.field_names = ["Name", "Phones"]
    table.min_width.update({"Name": 20, "Phones": 55})

    phones = contacts.show_phones(Name(args[0])) or "-"
    table.add_row([args[0], phones])

    return table


@input_error
def birthday(*args):
    """Функція-handler показує день народження та кількість днів до наступного."""

    if not args[0]:
        raise KeyError("Give me a name, please")

    table = PrettyTable()
    table.field_names = ["Name", "Birthday", "Days to next Birthday"]
    table.min_width.update(
        {"Name": 20, "Birthday": 12, "Days to next Birthday": 40}
    )

    days_to_next_birthday = contacts.data[args[0]].days_to_birthday() or "-"
    birthday = contacts.get(args[0]).show_birthday() or "-"

    table.add_row([args[0], birthday, days_to_next_birthday])

    return table

    # return "No such contach founded"


def search(*args):
    return "Here are the found contacts"


@input_error
def remove(*args):
    """Функція-handler видаляє запис з книги."""

    if not args[0]:
        raise KeyError

    name = Name(args[0])

    del contacts[name.value]

    return f"Contact {name.value} was removed"


@input_error
def change(*args):
    """Функція-handler змінює телефон контакту."""

    if not args[0]:
        raise KeyError

    if not args[1]:
        raise ValueError("Old phone number is required")

    if not args[2]:
        raise ValueError("New phone number is required")

    name = Name(args[0])
    old_phone = Phone(args[1])
    new_phone = Phone(args[2])

    if name.value not in contacts:
        return f"Contact {name.value} not found"

    contact_list = contacts[name.value].phones
    for number in contact_list:
        if number == old_phone:
            idx = contact_list.index(number)
            contact_list[idx] = new_phone
            break
        return f"Phone {old_phone.value} not found for {name.value}"

    return f"Contact {name.value} with phone number {old_phone.value} was updated with new phone number {new_phone.value}"


# =============================== handler loader =============================#

COMMANDS = {
    "hello": hello,
    "set birthday": set_birthday,
    "birthday of": birthday,
    "add": add,
    "change": change,
    "phones of": phones,
    "show all": show_all,
    "remove": remove,
    "good bye": good_bye,
    "close": good_bye,
    "exit": good_bye,
    "save": save,
    "load": load,
    "search": search,
}


def get_handler(*args):
    """Функція викликає відповідний handler."""
    return COMMANDS.get(args[0], undefined)


# ================================ main function =============================#

contacts = AddressBook()  # Global variable for storing contacts


def main():

    table = PrettyTable()
    table.field_names = ["Name", "Birthday", "Phones"]
    table.min_width.update({"Name": 20, "Birthday": 12, "Phones": 40})

    command_pattern = "|".join(COMMANDS.keys())
    pattern = re.compile(
        r"\b(\.|" + command_pattern + r")\b"
        r"(?:\s+([a-zA-Z0-9\.]+))?"
        r"(?:\s+(\d+|\d{1,2}\.\d{1,2}\.\d{4}(?:\.\d{2})?))?"
        r"(?:\s+(\d+)?)?",
        re.IGNORECASE,
    )

    load("contacts")
    while True:
        # waiting for nonempty input
        while True:
            inp = input(">>> ").strip()
            if inp == "":
                continue
            break

        text = pattern.search(inp)

        params = (
            tuple(
                map(
                    # Made a commands to be a uppercase
                    lambda x: x.lower() if text.groups().index(x) == 0 else x,
                    text.groups(),
                )
            )
            if text
            else (None, 0, 0)
        )
        handler = get_handler(*params)
        response = handler(*params[1:])
        if inp.strip() == ".":
            contacts.save_contacts("contacts")
            return
        if params[0] in ("show all", "search"):
            param = (
                int(params[1])
                if params[1] is not None
                and isinstance(params[1], str)
                and params[1].isdigit()
                else 100
            )
            if params[0] == "show all":
                entry = contacts
            elif params[0] == "search":
                entry = contacts.search(params[1])
            for tab in entry.iterator(param):
                if tab == "continue":
                    input("Press <Enter> to continue...")
                else:
                    print(build_table(tab))

        print(response)
        if response == "Good bye!":
            return


# ================================ main programm ============================ #

if __name__ == "__main__":

    main()
