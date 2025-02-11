import json
import random
import uuid
from datetime import datetime
from abc import ABC, abstractmethod

# Read data from json into a list
with open("users.json", "r") as usersJson:
    users = json.load(usersJson)

with open("books.json", "r") as booksJson:
    books = json.load(booksJson)

with open("librarians.json", "r") as librariansJson:
    libs = json.load(librariansJson)


# convert lists to dictionaries for fast searching
booksDict = {book["bookId"]: book for book in books}
usersDict = {user["username"]: user for user in users}
libsDict = {lib["username"]: lib for lib in libs}

def updateBooks():
    with open("books.json", "w") as booksJson:
        json.dump(list(booksDict.values()), booksJson, indent=4)

class User(ABC):
    _borrowLimit = None

    def __init__(self, user):
        self.user = user

    def __str__(self):
        return f'userId: {self.user["userId"]}, username: {self.user["username"]}, pass: {self.user["password"]}.'

    def _updateUser(self):
        with open("users.json", "w") as usersJson:
            json.dump(list(usersDict.values()), usersJson, indent=4)

    def _listBooks(self):
        if len(books) == 0:
            print("there are currently no books in the library...\n")
            return
        
        print("\n----------------------------------------\n")   
        for book in books:
            print(f'{book["bookId"]} - {book["bookName"]} - {book["bookAuthor"]} - {"available" if book["availability"] else "unavailable"}\n')
        print("----------------------------------------\n")

    def __displayBook(self, book):
        print("\n---------------------------")
        print("book ID:", book["bookId"])
        print("book name:", book["bookName"])
        print("book author:", book["bookAuthor"])
        print("book location (Rack no.):", "not found" if book["rackNumber"] is None else str(book["rackNumber"]))
        print("availability:", "available" if book["availability"] else "unavailable")
        print("book count:", str(book["bookCount"]))
        print("---------------------------")
    
    def _searchBook(self):
        while True:
            print("------------------------------")
            try:
                choice = int(input("How would you like to seach the book?\n\t1. by name\n\t2. by author\n\t3. by rack number\n\t4. by availability\n\t0. return\n----> "))

                match choice:
                    case 0:
                        break

                    case 1: # Search by Title
                        bookName = input("enter book name: ")
                        booksFound = False

                        for book in booksDict.values():
                            if bookName.lower() in book["bookName"].lower():
                                self.__displayBook(book)
                                booksFound = True
                        
                        if not booksFound:
                            print("book with name", bookName, "was not found...\n")
                    
                    case 2: # Search by Author
                        authorName = input("enter author name: ")
                        booksFound = False

                        for book in booksDict.values():
                            if authorName.lower() in book["bookAuthor"].lower():
                                self.__displayBook(book)
                                booksFound = True
                        
                        if not(booksFound):
                            print("there are no books from", authorName, "\n")

                    case 3: # Search by Rack Number
                        rackNumber = int(input("enter rack number to search: "))
                        booksFound = False

                        for book in booksDict.values():
                            if book["rackNumber"] == rackNumber:
                                self.__displayBook(book)
                                booksFound = True

                        if not(booksFound):
                            print("there are no books on rack number", str(rackNumber), "\n")
                    
                    case 4: # Search by availability
                        booksFound = False

                        for book in booksDict.values():
                            if book["availability"]:
                                self.__displayBook(book)
                                booksFound = True

                        if not(booksFound):
                            print("there are currently no books in the library...\n")

                    case _:
                        print("invalid choice...\n")

            except ValueError:
                print("invalid choice...\n")
    
    def _borrowBook(self):
        if self.user["currentlyBorrowedBook"] == self._borrowLimit:
            print(f'you can not borrow more than {self._borrowLimit} book at a time...\nf')
            return

        bookId = input("enter book ID of the book you want to borrow: ")

        book = booksDict.get(bookId)

        if not book:
            print("book not found... check the book ID...\n")
            return

        if self.user["userId"] in book["borrowers"]:
            print("you can't borrow the same book twice...\n")
            return
        
        if not book["availability"]:
            print("book is not available. try another one...\n")
            return
        
        if bookId in self.user["reservations"]:
            self.user["reservations"].remove(bookId)
        
        # EDITING BOOKS OBJECT
        book["bookCount"] -= 1
        book["borrowers"].append(self.user["userId"])
        
        if book["bookCount"] == 0:
            book["designatedRackNumber"] = book["rackNumber"]
            book["rackNumber"] = None
            book["availability"] = False

        # EDITING USER OBJECT
        self.user["borrowedBooks"].append({
            'transactionId': str(uuid.uuid4()),
            'bookId': book["bookId"],
            'bookName': book["bookName"],
            'borrowedDate': datetime.today().strftime("%Y-%m-%d"),
            'returnedDate': None
        })
        self.user["currentlyBorrowedBook"] += 1

        print("Successfully borrowed", book["bookName"], "by", book["bookAuthor"] + "...\n")

    def _returnBook(self):
        if self.user["currentlyBorrowedBook"] == 0:
            print("You haven't borrowed any book to return...\n")
            return
        
        bookId = input("enter book ID of the book you want to return: ")
        transactionsDict = {(transaction["bookId"], transaction["returnedDate"]): transaction for transaction in self.user["borrowedBooks"]}

        if (bookId, None) not in transactionsDict:
            print("book ID does not match your currently borrowed book(s) ID...\n")
            return
        
        transaction = transactionsDict.get((bookId, None))
        
        dateFormat = "%Y-%m-%d"
        # UN/COMMENT THIS FOR THE 3 DAYS MINIMUM TIME LIMIT #

        # dateToday = datetime.today().strftime(dateFormat)

        # dateBorrowed = transaction["borrowedDate"]
        # dateDifference = datetime.strptime(dateToday, dateFormat) - datetime.strptime(dateBorrowed, dateFormat)

        # if dateDifference.days <= 3:
        #     print("You can only return a book after 3 days...\n")
        #     return

        book = booksDict.get(bookId)
        if not book:
            print("ERROR: BOOK NOT FOUND.\n")
            return
        
        # EDITING BOOKS
        book["bookCount"] += 1
        book["borrowers"].remove(self.user["userId"])

        if book["bookCount"] == 1:
            book["rackNumber"] = book["designatedRackNumber"]
            book.pop("designatedRackNumber")
            book["availability"] = True
        
        # EDITING USERS
        self.user["currentlyBorrowedBook"] -= 1
        transaction["returnedDate"] = datetime.today().strftime(dateFormat)

        print("Successfully returned", book["bookName"], "by", book["bookAuthor"] + "...\n")

    @abstractmethod
    def serveUser():
        pass

class Client(User):
    def __init__(self, user):
        self.user = user
        self._borrowLimit = 1

    def __reserveBook(self):
        bookId = input("enter book ID that you want to reserve: ")

        if bookId not in booksDict:
            print(f'a book with ID "{bookId}" does not exist, confirm the book ID...\n')
            return
        
        if booksDict[bookId]["availability"]:
            print(f'the book with ID "{bookId}" and name "{booksDict[bookId]["bookName"]}" is already available...\n')
            return
        
        if bookId in self.user["reservations"]:
            print(f'you have already reserved the book with ID {bookId} and name "{booksDict[bookId]["bookName"]}"...\n')
            return

        self.user["reservations"].append(bookId)

        print(f'successfully reserved "{booksDict[bookId]["bookName"]}"...\n')

    def serveUser(self):
        for reservation in self.user["reservations"]:
            if booksDict[reservation]["availability"]:
                print(f'\nthe book "{booksDict[reservation]["bookName"]}" is now available to borrow...\n')

        while True:
            print("------------------------------")
            try:
                choice = int(input("U: what would you like to do?\n\t1. search book\n\t2. borrow book\n\t3. return book\n\t4. list books\n\t5. reserve book\n\t0. quit\n---> "))

                match choice:
                    case 0:
                        updateBooks()
                        self._updateUser()
                        print("logged out...")
                        return

                    case 1:
                        self._searchBook()

                    case 2:
                        self._borrowBook()

                    case 3:
                        self._returnBook()

                    case 4:
                        self._listBooks()

                    case 5:
                        self.__reserveBook()

                    case _:
                        print("invalid choice...\n")
            
            except ValueError:
                print("invalid choice...\n")

class Librarian(User):
    def __init__(self, user):
        self.user = user
        self._borrowLimit = 3

    def _updateUser(self):
        with open("librarians.json", "w") as librariansJson:
            json.dump(list(libsDict.values()), librariansJson, indent=4)

    def __updateBook(self):
        bookId = input("enter the book ID of the book you want to update: ")

        if bookId not in booksDict:
            print(f'a book with ID "{bookId}" does not exist, confirm the book ID...\n')
            return
        
        while True:
            status = input("update availability (y/n): ")
            if status in ["y", "yes"]:
                if not booksDict[bookId]["availability"]:
                    booksDict[bookId]["availability"] = True
                    break

                print("\nthe book is already available\n")

            elif status in ["n", "no"]:
                if booksDict[bookId]["availability"]:
                    booksDict[bookId]["availability"] = False
                    booksDict[bookId]["rackNumber"] = None
                    booksDict[bookId]["bookCount"] = 0
                    print("book data updated successfully...\n")

                    return

                print("\nthe book is already unavailable...\n")
            else:
                print("invalid choice...\n")

        while True:
            try:
                count = int(input("enter the count of books available: "))

                if count < 1 or count > 10:
                    print("\nenter valid number of books...\n")
                    continue

                booksDict[bookId]["bookCount"] = count
                booksDict[bookId]["rackNumber"] = random.randint(1, 20)
                print("book data updated successfully...\n")
                
                return
            except ValueError:
                print("invalid count...\n")

    def serveUser(self):
        while True:
            print("------------------------------")
            try:
                choice = int(input("L: what would you like to do?\n\t1. search book\n\t2. borrow book\n\t3. return book\n\t4. list books\n\t5. update book\n\t0. quit\n---> "))

                match choice:
                    case 0:
                        updateBooks()
                        self._updateUser()
                        print("logged out...")
                        return

                    case 1:
                        self._searchBook()

                    case 2:
                        self._borrowBook()

                    case 3:
                        self._returnBook()

                    case 4:
                        self._listBooks()

                    case 5:
                        self.__updateBook()

                    case _:
                        print("invalid choice...\n")

            except ValueError as error:
                print("invalid choice...\n")

while True:
    print("------------------------------")
    try:
        choice = int(input("choose your action:\n\t1. Login\n\t2. Register\n\t0. quit\n----> "))

        match choice:
            case 0:
                exit(0)

            case 1:
                username = input("enter your username: ")

                if username in usersDict:
                    user = usersDict.get(username)
                    password = input("enter your password: ")

                    if password != user["password"]:
                        print("incorrect password...\n")
                        continue

                    client = Client(user)
                    client.serveUser()
                    exit(0)
                    
                elif username in libsDict:
                    user = libsDict.get(username)
                    password = input("enter your password: ")

                    if password != user["password"]:
                        print("incorrect password...\n")
                        continue

                    libarian = Librarian(user)
                    libarian.serveUser()
                    exit(0)

                else:
                    print("User not found...\n")

            case 2:
                username = input("enter username: ")

                if username in usersDict:
                    print("User already exists...\n")
                    continue

                password = input("create a password: ")
                newUser = {
                    "userId": str(uuid.uuid4()),
                    "username": username,
                    "password": password,
                    "borrowedBooks": [],
                    "currentlyBorrowedBook": 0,
                }

                usersDict["username"] = newUser

                #Registered
                client = Client(newUser)
                client.serveUser()
                exit(0)

            case _:
                print("invalid choice...\n")
    
    except ValueError:
        print("invalid choice...\n")