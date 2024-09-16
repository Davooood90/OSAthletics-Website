from funcs.sql_helper import sql_get

# Parent Class
class Sport:
    # Initialize Base Variables
    def __init__(self, sport):
        self.sport = sport

    # Retrieve the Sport
    def getsport(self):
        return self.sport

# Child Class
class Roster(Sport):
    # Initialize Base Variables
    def __init__(self, sport, cursor):
        super().__init__(sport)

        test_case = (self.sport, "coach")
        self.coaches = sql_get("*", "roster", "sport = %s AND role = %s", test_case, cursor)

        test_case = (self.sport, "player")
        self.players = sql_get("*", "roster", "sport = %s AND role = %s", test_case, cursor)

    # Return Sorted Dictionary of Players by First Name
    def sortedplayers(self):
        return sorted(self.players, key=lambda x: x["name"])
    
    # Return Sorted Dictionary of Coaches by First Name
    def sortedcoaches(self):
        return sorted(self.coaches, key=lambda x: x["name"])

# Child Class
class Achievements(Sport):
    # Initialize Base Variables
    def __init__(self, sport, cursor):
        super().__init__(sport)
        sql_select_Query = "SELECT * FROM achievements WHERE sport = %s ORDER BY yachieved DESC"

        cursor.execute(sql_select_Query, (self.sport,))
        self.achievements = cursor.fetchall()
    
    # Retrieve Achievements
    def getachievements(self):
        return self.achievements