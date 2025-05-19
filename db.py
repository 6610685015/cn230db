# นายอติชาต เพ็ญวงษ์ 6610685015
# project หลักจะอยู่ส่วนขึ้นล่างของ file โดยจะเป็น program ที่ใช้ในการ search 
# หาข้อมูลที่ต้องการได้ตามต้องการ ใน data โดยจะเเสดงออกมาเป็น table

import requests
import sqlite3

# path api
url = "https://www.mmobomb.com/api1/games"
# connetion for connect sqllite
con = sqlite3.connect("tutorial.db")

cur = con.cursor()

cur.execute("DROP TABLE IF EXISTS games")
cur.execute("CREATE TABLE games(id, title, genre, platform, developer, publisher, release_date)")


response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    # json attribute
    fieldvalues=[]
    for game in data:
        id = game["id"]
        title = game["title"]
        genre = game["genre"]
        platform = game["platform"]
        developer = game["developer"]
        publisher = game["publisher"]
        release_date = game["release_date"]

        fieldvalues=[(id,title, genre, platform, developer, publisher, release_date)]

        cur.executemany("INSERT INTO games VALUES(?, ?, ?, ?, ?, ?, ?)", fieldvalues)
        con.commit()

else:
    print("ERROR", response.status_code)

print("-------------------Order by ID---------------------")

# Order all game by id from less to high
for row in cur.execute("SELECT id,title, genre, platform, developer, publisher, release_date FROM games ORDER BY id asc"):
    print(row)

print("------------------Number of games in data base----------------------")
# How much games in the database
for row in cur.execute("SELECT count(id) as count_id FROM games "):
    print(row)

# Order all MMORPG games by id
print("------------------MMORPG games----------------------")
for row in cur.execute("SELECT id,title, genre FROM games where genre = 'MMORPG' ORDER by id asc"):
    print(row)

print("------------------Total MMORPG games----------------------")
# How much MMORPG games in the database
for row in cur.execute("SELECT count(id) as count_id FROM games where genre = 'MMORPG'"):
    print(row)

print("-------------------Total games from every genre---------------------")
# Count games type for every game genre and resolve space in name by accident using trim
for row in cur.execute("SELECT trim(genre), count(id) as count_id FROM games group by trim(genre) order by count_id desc"):
    print(row)

print("-------------------Genre Distribution (%)---------------------")
total_count = cur.execute("SELECT COUNT(*) FROM games").fetchone()[0]

for row in cur.execute("SELECT trim(genre), COUNT(id) FROM games GROUP BY trim(genre) ORDER BY COUNT(id) DESC"):
    genre, count = row
    percent = (count / total_count) * 100
    print(f"{genre}: {count} games ({percent:.2f}%)")


print("-------------------Total games from every platform---------------------")
# Count games type for every game platform and resolve space in name by accident using trim
for row in cur.execute("SELECT trim(platform), count(id) as count_id FROM games group by trim(platform) order by count_id desc"):
    print(row)

print("-------------------Platform Distribution (%)---------------------")
for row in cur.execute("SELECT trim(platform), COUNT(id) FROM games GROUP BY trim(platform) ORDER BY COUNT(id) DESC"):
    platform, count = row
    percent = (count / total_count) * 100
    print(f"{platform}: {count} games ({percent:.2f}%)")


print("-------------------Total games from every developer---------------------")
# Count games type for every game developer and resolve space in name by accident using trim
for row in cur.execute("SELECT trim(developer), count(id) as count_id FROM games group by trim(developer) order by count_id desc"):
    print(row)

print("-------------------Publisher Distribution (%)---------------------")
for row in cur.execute("SELECT trim(publisher), COUNT(id) FROM games GROUP BY trim(publisher) ORDER BY COUNT(id) DESC"):
    publisher, count = row
    percent = (count / total_count) * 100
    print(f"{publisher}: {count} games ({percent:.2f}%)")
    

print("-------------------Total games from every publisher---------------------")
# Count games type for every game publisher and resolve space in name by accident using trim
for row in cur.execute("SELECT trim(publisher), count(id) as count_id FROM games group by trim(publisher) order by count_id desc"):
    print(row)

print("-------------------Total games from every year---------------------")
for row in cur.execute("SELECT strftime('%Y', release_date) AS year, COUNT(id) as count_id FROM games GROUP BY year ORDER BY year desc"):
    print(row)

print("-------------------Game Genre Distribution (%)---------------------")
total_count = cur.execute("SELECT COUNT(*) FROM games").fetchone()[0]

for row in cur.execute("SELECT trim(genre), COUNT(id) as count_id FROM games GROUP BY trim(genre) ORDER BY count_id DESC"):
    genre, count = row
    percent = (count / total_count) * 100
    print(f"{genre}: {count} games ({percent:.2f}%)")



Loop = True
current_sort = "id"  # default sort

while Loop:
    print("\n------------------Search or Sort----------------------")
    mode = input("Choose mode: (search / sort / exit): ").lower()

    # If user type exit the program will stop
    if mode == "exit":
        print("Thank you for using the game search system!")
        break

    # Sort data by (defial is sort by id)
    elif mode == "sort":
        sort_field = input("Sort by (id, genre, platform, developer, publisher, release_date): ").lower()
        if sort_field in ["id", "genre", "platform", "developer", "publisher", "release_date"]:
            current_sort = sort_field
            print(f"Sorting will now be done by: {current_sort}")
        else:
            print("Invalid sort field. Sort not changed.")

    elif mode == "search":
        # Store various search values
        search_conditions = {}

        # Ask user what they want to search for
        while True:
            search_type = input("What to search? (genre, platform, developer, publisher, year, title): ").lower()
            if search_type in ["genre", "platform", "developer", "publisher", "year", "title"]:
                if search_type not in search_conditions:
                    value = input(f"Enter {search_type} you want to find: ")
                    search_conditions[search_type] = value
                else:
                    print(f"You already added {search_type}")
            else:
                print("Invalid search type.")

            cont = input("Add more condition? (Y/N): ").upper()
            if cont == "N":
                break

        # Create a query based on user-specified conditions.
        base_query = "SELECT id, title, genre, platform, developer, publisher, release_date FROM games"
        where_clauses = []
        values = []

        # prepare "where_clauses" for using in next step for searching
        for key, val in search_conditions.items():
            if key == "year":
                where_clauses.append("strftime('%Y', release_date) = ?")
                values.append(val)
            elif key == "title":
                where_clauses.append("title LIKE ?")
                values.append(f"%{val}%")
            else:
                where_clauses.append(f"{key} = ?")
                values.append(val)

        # Set value of query in SQL form for using in serch
        if where_clauses:
            query = base_query + " WHERE " + " AND ".join(where_clauses) + f" ORDER BY {current_sort} ASC"
        else:
            query = base_query + f" ORDER BY {current_sort} ASC"

        # Pull wanted search results from input
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()
        print("Tables in database:", tables)
        cur.execute(query, values)
        results = cur.fetchall()
        

        # Show results
        if results:
            print(f"\n------ Search Results ({len(results)} games found, sorted by {current_sort}) ------")
            for row in results:
                print(row)

        # if there no search result found
        else:
            print("\nNo games found with the specified conditions.")
    #ask user if they want to continus or not
    else:
        print("Invalid mode. Please choose 'search', 'sort', or 'exit'.")

con.close()