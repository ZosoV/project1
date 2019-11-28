import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    firstline = True

    num_proof_record = 100
    i = 0
    for isbn,title,author,year in reader:
        if firstline:    #skip first line
            firstline = False
            continue
        db.execute("INSERT INTO book (isbn,title,author,year) VALUES (:isbn,:title,:author,:year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added book with isbn: {isbn}, title: {title}, author: {author}, and year: {year}.")
        i = i + 1
        if i == num_proof_record:
            break
    db.commit() #se empaqueto en una transaccion y aqui se ejecuta la transaccion

if __name__ == "__main__":
    main()
