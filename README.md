# Project 1
Web Programming with Python and JavaScript

### Description
My project1 is about book reference. It contains several parts

### Video

```
https://youtu.be/WkgjbS4G09k
```

### Folder Distribution

The project has the following folder distribution    

```
\static
\templates
application.py
books.csv
import.py
sentences.sql
requirements.txt 

```

1. In the folder static, there are all the used images and styles of this projec.
2. In the folder templates, there are the different pages of this web page an layout which is the base of the other html files
3. The applicaition.py stores all the functions to request services or sources from the data base.
4. books.csv and import.py are used for filling the table book of the database.
5. export.sh sets the environmental variables.
6. sentences.sql stores all the SQL sentences which are needed to create the database and its realations.
7. requirements.txt stores all the necessary packages to run this web page.

### Pages Information and Implementation

###### Login and Register

If we have a user we can log in the page. If not, we can create a new user with registration page.

###### Search

In this page, you can find a book according to ISBN, title or author. Once you click on one book, you can see the book detail page.

###### Book Detail

In this page, you can see all the information about a book. Besides, you can see some commments of other user, and you can comment it only one time.

###### API

This web page includes an api. You can access to that api using:

```
\api\[isbn]

```



