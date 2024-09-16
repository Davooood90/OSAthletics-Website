from funcs.sql_helper import sql_get

# Parent Class


class Account:
    # Initialize Base Variables
    def __init__(self, email, cursor):
        self.email = email
        self.accountId = sql_get(
            "accountId", "accounts", "email = %s", (email,), cursor)

    # Retrieve the Sport
    def getEmail(self):
        return self.email

    # Retrieve the Sport
    def getId(self):
        return self.accountId[0]["accountId"]

# Child Class


class Student(Account):
    # Initialize Base Variables
    def __init__(self, email, cursor):
        super().__init__(email, cursor)
        self.information = sql_get(
            "*", "students", "accountId = %s", (self.getId(),), cursor)
        try:
            self.pemail = sql_get("email", "accounts", "accountId= %s", (sql_get(
                "accountId", "parents", "parentId = %s", (self.information[0]["parentId"],), cursor)[0]["accountId"],), cursor)[0]['email']
        except:
            self.pemail = ""

    # Retrieve Name
    def getname(self, part):
        name = self.information[0][part+"name"]
        return name if name else ""

    # Retrieve Birthday
    def getbirthday(self):
        return self.information[0]["birthday"] or ""

    # Retrieve Gender
    def getgender(self):
        return self.information[0]["gender"] or ""

    # Retrieve Phone Number
    def getphonenumber(self):
        return self.information[0]["phone_number"] or ""

    # Retrieve Parent Email
    def getpemail(self):
        return self.pemail


# Child Class
class Parent(Account):
    # Initialize Base Variables
    def __init__(self, email, cursor):
        super().__init__(email, cursor)
        self.information = sql_get(
            "*", "parents", "accountId = %s", (self.getId(),), cursor)
        try:
            self.pemail = sql_get("email", "accounts", "accountId= %s", (sql_get(
                "accountId", "students", "studentId = %s", (self.information[0]["studentId"],), cursor)[0]["accountId"],), cursor)[0]['email']
        except:
            self.pemail = ""

    # Retrieve Name
    def getname(self, part):
        name = self.information[0][part+"name"]
        return name if name else ""

    # Retrieve Birthday
    def getbirthday(self):
        return self.information[0]["birthday"] or ""

    # Retrieve Gender
    def getgender(self):
        return self.information[0]["gender"] or ""

    # Retrieve Phone Number
    def getphonenumber(self):
        return self.information[0]["phone_number"] or ""

    # Retrieve Child Email
    def getpemail(self):
        return self.pemail


# Child Class
class Coach(Account):
    # Initialize Base Variables
    def __init__(self, email, cursor):
        super().__init__(email, cursor)
        self.information = sql_get(
            "*", "coaches", "accountId = %s", (self.getId(),), cursor)

    # Retrieve Name
    def getname(self, part):
        name = self.information[0][part+"name"]
        return name if name else ""

    # Retrieve Birthday
    def getbirthday(self):
        return self.information[0]["birthday"] or ""

    # Retrieve Gender
    def getgender(self):
        return self.information[0]["gender"] or ""

    # Retrieve Phone Number
    def getphonenumber(self):
        return self.information[0]["phone_number"] or ""
