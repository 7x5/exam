import sqlite3

con = sqlite3.connect("database.db")
cur = con.cursor()


cur.execute("""CREATE TABLE IF NOT EXISTS problemer (
                problem_id INTEGER PRIMARY KEY AUTOINCREMENT,
                helenavn TEXT,
                telenr INTEGER,
                body TEXT,
                time TEXT,
                status TEXT
              );""")


cur.execute("""CREATE TABLE IF NOT EXISTS arbeid (
                arbeid_id INTEGER PRIMARY KEY AUTOINCREMENT,
                person TEXT,
                time TEXT,
                status TEXT,
                problem_id INTEGER,
                FOREIGN KEY (problem_id) REFERENCES problemer(problem_id)
              );""")

con.commit()

