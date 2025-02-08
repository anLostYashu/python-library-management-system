import json
import uuid
from datetime import datetime

with open("users.json", "r") as usersJson:
    users = json.load(usersJson)

with open("books.json", "r") as booksJson:
    books = json.load(booksJson)

with open("librarians.json", "r") as librariansJson:
    libs = json.load(librariansJson)

def updateBooks():
    with open("books.json", "w") as booksJson:
        json.dump(books, booksJson, indent=4)

class User:
    borrowLimit = 1

    def __init__(self, user):
        self.user = user

    def __str__(self):
        return f'userId: {self.user["userId"]}, username: {self.user["username"]}, pass: {self.user["password"]}.'
    
    def updateData(self):
        with open("users.json", "w") as usersJson:
            json.dump(users, usersJson, indent=4)

    def displayBook(self, book):
        # {
        #     "bookName": "The Catcher in the Rye",
        #     "bookAuthor": "J.D. Salinger",
        #     "rackNumber": 9,
        #     "availability": true,
        #     "bookCount": 2,
        #     "borrowers": []
        # }

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

                for book in books:
                    if book["bookName"].title() == bookName.title():
                        self.displayBook(book)
                        break
                else:
                    print("book with name", bookName, "was not found...\n")
            
            elif choice == 2: # Search by Author
                authorName = input("enter author name: ")
                booksFound = False

                for book in books:
                    if book["bookAuthor"].lower() == authorName.lower():
                        self.displayBook(book)
                        booksFound = True
                
                if not(booksFound):
                    print("there are no books from", authorName, "\n")

            elif choice == 3: # Search by Rack Number
                rackNumber = int(input("enter rack number to search: "))
                booksFound = False

                for book in books:
                    if book["rackNumber"] == rackNumber:
                        self.displayBook(book)
                        booksFound = True

                if not(booksFound):
                    print("there are no books on rack number", str(rackNumber), "\n")
            
            elif choice == 4:
                booksFound = False

                for book in books:
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

        for book in books:
            if book["bookId"] == bookId:
                if not(book["availability"]):
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
                return
                    
        else:
            print("book not found... check the book ID...\n") 
            return

    def returnBook(self):
        if self.user["currentlyBorrowedBook"] == 0:
            print("You haven't borrowed any book to return...\n")
            return
        
        bookId = input("enter book ID of the book you want to return: ")

        for transaction in self.user["borrowedBooks"]:
            if transaction["bookId"] == bookId:
                break
        else:
            print("book ID does not match your currently borrowed book's ID...\n")
            return

        # if self.user["borrowedBooks"][-1] != bookId:
        #     print("book ID does not match your currently borrowed book's ID...\n")
        #     return
        
        dateFormat = "%Y-%m-%d"
        dateToday = datetime.today().strftime(dateFormat)

        for transaction in self.user["borrowedBooks"]:
            if transaction["bookId"] == bookId and transaction["returnedDate"] is None:
                dateBorrowed = transaction["borrowedDate"]
                break

        dateDifference = datetime.strptime(dateToday, dateFormat) - datetime.strptime(dateBorrowed, dateFormat)

        if dateDifference.days <= 3:
            print("You can only return a book after 3 days...\n")
            return
        
        for book in books:
            if book["bookId"] == bookId:
                # EDITING BOOKS
                book["bookCount"] += 1
                book["borrowers"].remove(self.user["userId"])

                if book["bookCount"] == 1:
                    book["rackNumber"] = book["designatedRackNumber"]
                    book.pop("designatedRackNumber")
                    book["availability"] = True
                
                # EDITING USERS
                self.user["currentlyBorrowedBook"] -= 1
                for transaction in self.user["borrowedBooks"]:
                    if transaction["bookId"] == bookId:
                        transaction["returnedDate"] = datetime.today().strftime(dateFormat)
                        break

                print("Successfully returned", book["bookName"], "by", book["bookAuthor"] + "...\n")
                return
        else:
            print("ERROR: BOOK NOT FOUND")


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
            json.dump(libs, librariansJson, indent=4)

    # ADD ADDITIONAL LIBRARIAN ONLY METHODS

while True:
    print("------------------------------")
    choice = int(input("choose your action:\n\t1. Login\n\t2. Register\n\t0. quit\n----> "))

    if choice == 0:
        exit(0)

    elif choice == 1:
        username = input("enter your username: ")

        for user in users:
            if user["username"] == username:
                password = input("enter your password: ")
                if user["password"] != password:
                    print("incorrect password...\n")
                    break

                client = User(user)
                client.serveUser()
                exit(0)
        else:
            for lib in libs:
                if lib["username"] == username:
                    password = input("enter your librarian password: ")

                    if lib["password"] != password:
                        print("invalid librarian password...\n")
                        break

                    client = Librarian(lib)
                    client.serveUser()
                    exit(0)
            else:
                print("user not found...\n")

    elif choice == 2:
        username = input("enter username: ")

        for user in users:
            if user["username"] == username:
                print("user already exists.\n")
                break
        else:
            password = input("create a password: ")

            newUser = {
                "userId": str(uuid.uuid4()),
                "username": username,
                "password": password,
                "borrowedBooks": [],
                "currentlyBorrowedBook": 0,
            }

            users.append(newUser)

            # REGISTERED
            user = User(newUser)
            user.serveUser()

            exit(0)
    else:
        print("invalid choice...\n")
