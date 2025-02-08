import json
import uuid
from datetime import datetime

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

class User:
    borrowLimit = 1

    def __init__(self, user):
        self.user = user

    def __str__(self):
        return f'userId: {self.user["userId"]}, username: {self.user["username"]}, pass: {self.user["password"]}.'
    
    def updateData(self):
        with open("users.json", "w") as usersJson:
            json.dump(list(usersDict.values()), usersJson, indent=4)

    def displayBook(self, book):
        print("\n----- Book Data -----")
        print("book ID:", book["bookId"])
        print("book name:", book["bookName"])
        print("book author:", book["bookAuthor"])
        print("book location (Rack no.):", "not found" if book["rackNumber"] is None else str(book["rackNumber"]))
        print("availability:", "available" if book["availability"] else "unavailable")
        print("book count:", str(book["bookCount"]))
        print("---------------------\n")
    
    def searchBook(self):
        while True:
            print("------------------------------")
            choice = int(input("How would you like to seach the book?\n\t1. by name\n\t2. by author\n\t3. by rack number\n\t4. by availability\n\t0. return\n----> "))

            if choice == 0:
                break

            elif choice == 1: # Search by Title
                bookName = input("enter book name: ")

                for book in booksDict.values():
                    if book["bookName"].title() == bookName.title():
                        self.displayBook(book)
                        break
                else:
                    print("book with name", bookName, "was not found...\n")
            
            elif choice == 2: # Search by Author
                authorName = input("enter author name: ")
                booksFound = False

                for book in booksDict.values():
                    if book["bookAuthor"].lower() == authorName.lower():
                        self.displayBook(book)
                        booksFound = True
                
                if not(booksFound):
                    print("there are no books from", authorName, "\n")

            elif choice == 3: # Search by Rack Number
                rackNumber = int(input("enter rack number to search: "))
                booksFound = False

                for book in booksDict.values():
                    if book["rackNumber"] == rackNumber:
                        self.displayBook(book)
                        booksFound = True

                if not(booksFound):
                    print("there are no books on rack number", str(rackNumber), "\n")
            
            elif choice == 4:
                booksFound = False

                for book in booksDict.values():
                    if book["availability"]:
                        self.displayBook(book)
                        booksFound = True

                if not(booksFound):
                    print("there are currently no books in the library...\n")

            else:
                print("invalid choice...\n")
    
    def borrowBook(self):
        if self.user["currentlyBorrowedBook"] == self.borrowLimit:
            print(f'you can not borrow more than {self.borrowLimit} book at a time...\nf')
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
            'borrowedDate': datetime.today().strftime("%Y-%m-%d"),
            'returnedDate': None
        })
        self.user["currentlyBorrowedBook"] += 1

        print("Successfully borrowed", book["bookName"], "by", book["bookAuthor"] + "...\n")

    def returnBook(self):
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
        dateToday = datetime.today().strftime(dateFormat)

        dateBorrowed = transaction["borrowedDate"]
        dateDifference = datetime.strptime(dateToday, dateFormat) - datetime.strptime(dateBorrowed, dateFormat)

        if dateDifference.days <= 3:
            print("You can only return a book after 3 days...\n")
            return

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

    def serveUser(self):
        while True:
            print("------------------------------")
            choice = int(input("what would you like to do?\n\t1. search book\n\t2. borrow book\n\t3. return book\n\t0. quit\n---> "))

            if choice == 0:
                updateBooks()
                self.updateData()
                print("logged out...")

                break

            elif choice == 1:
                self.searchBook()
            
            elif choice == 2:
                self.borrowBook()

            elif choice == 3:
                self.returnBook()
            
            else:
                print("invalid choice...\n")

class Librarian(User):
    borrowLimit = 3

    def updateData(self):
        with open("librarians.json", "w") as librariansJson:
            json.dump(list(libsDict.values()), librariansJson, indent=4)

    # ADD ADDITIONAL LIBRARIAN ONLY METHODS

while True:
    print("------------------------------")
    choice = int(input("choose your action:\n\t1. Login\n\t2. Register\n\t0. quit\n----> "))

    if choice == 0:
        exit(0)

    elif choice == 1:
        username = input("enter your username: ")

        if username in usersDict:
            user = usersDict.get(username)
            password = input("enter your password: ")

            if password != user["password"]:
                print("incorrect password...\n")
                continue

            client = User(user)
            client.serveUser()
            exit(0)
            
        elif username in libsDict:
            user = libsDict.get(username)
            password = input("enter your password: ")

            if password != user["password"]:
                print("incorrect password...\n")
                continue

            client = Librarian(user)
            client.serveUser()
            exit(0)

        else:
            print("User not found...\n")

    elif choice == 2:
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
        client = User(newUser)
        client.serveUser()
        exit(0)

    else:
        print("invalid choice...\n")
