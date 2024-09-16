import mysql.connector

# Connects To MySQL Server
def sql_connect(key):
    connection = mysql.connector.connect(host='localhost',
                                        database='osa_athletics',
                                        user='management',
                                        password=key)
    return connection

# Disconnects From MySQL Server
def sql_close(connection, cursor):
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

# Get Item From MySQL Server
def sql_get(column, table, cond, test_case, cursor):
    sql_select_Query = f"SELECT {column} FROM {table} WHERE {cond}"
    cursor.execute(sql_select_Query, test_case)
    return cursor.fetchall()

# Delete Item From MySQL Server
def sql_rmv(connection, table, cond, test_case, cursor):
    sql_Delete_query = f"""DELETE FROM {table} WHERE {cond}"""
    cursor.execute(sql_Delete_query, test_case)
    connection.commit()

# Insert Item Into MySQL Server
def sql_insert(connection, table, columns, values, test_case, cursor):
    mySQL_insert_query = f"""INSERT INTO {table} {columns} VALUES {values}"""
    cursor.execute(mySQL_insert_query, test_case)
    connection.commit()

# Update Item In MySQL Server
def sql_update(connection, table, columns, cond, test_case, cursor):
    cursor.execute("""SET SQL_SAFE_UPDATES = 0""")
    connection.commit()

    mySQL_update_query = f"""UPDATE {table} SET {columns} WHERE {cond}"""

    cursor.execute(mySQL_update_query, test_case)
    connection.commit()

    cursor.execute("""SET SQL_SAFE_UPDATES = 1""")
    connection.commit()