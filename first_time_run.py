
# %%
# Importing MySQL Connector
import mysql.connector as mysql

# %%
# Connect to book_store Database 
mydb = mysql.connect(
    host="localhost",
    user="root",
    passwd="root")
mydb.is_connected()

# Get Cursor & Store it in reference to execute query;
cur = mydb.cursor()

# %%
cur.execute("SHOW DATABASES")
for i in cur.fetchall():
    if (i[0] == 'book_store'):
        cur.execute("DROP DATABASE book_store")
        break
cur.execute("CREATE DATABASE book_store")
cur.execute("USE book_store")

# %%
# Schema for database
cur.execute("""
    CREATE TABLE Book(
    ISBN INT PRIMARY KEY,
    title VARCHAR(50) NOT NULL,
    year INT,
    price DECIMAL(5,2) DEFAULT 0,
    stocks INT DEFAULT 0
    )""")
cur.execute("""
    CREATE TABLE Publisher(
    name VARCHAR(20) PRIMARY KEY,
    address VARCHAR(50),
    phone VARCHAR(10),
    url VARCHAR(20)
    )""")
cur.execute("ALTER TABLE Book ADD publisher VARCHAR(20)")
cur.execute("ALTER TABLE Book ADD FOREIGN KEY (publisher) REFERENCES Publisher(name) ON DELETE SET NULL")

cur.execute("""
    CREATE TABLE Author(
    name VARCHAR(20) PRIMARY KEY,
    address VARCHAR(50),
    url VARCHAR(20)
    )""")
cur.execute("ALTER TABLE Book ADD author VARCHAR(20)")
cur.execute("ALTER TABLE Book ADD FOREIGN KEY (author) REFERENCES Author(name) ON DELETE SET NULL")

cur.execute("""
    CREATE TABLE Customer(
    email VARCHAR(20) PRIMARY KEY,
    name VARCHAR(20),
    phone VARCHAR(10),
    address VARCHAR(50)
    )""")
cur.execute("""CREATE TABLE ShoppingBasket(
    email VARCHAR(20),
    book_isbn INT,
    FOREIGN KEY (email) REFERENCES Customer(email) ON DELETE CASCADE,
    FOREIGN KEY (book_isbn) REFERENCES Book(ISBN) ON DELETE CASCADE
    )""")


# %%
# Adding data to database.
cur.execute("""
    INSERT INTO Publisher VALUES 
    ('New Publishers','Plot 120, Budhwar Peth, ABC Chowk, Pune','1112223334','newpublishers.co.in'),
    ('Technic','12, Swarkar Nagar, Mumbai','9811122233','technicbooks.com'),
    ('Open Archives','Rathore Colony, Bangalore','9876543211','openarchives.org'),
    ('Neo Books','32, Mangalwar Peth, Pune','9876767651','booksbyneo.com');
""")
cur.execute("""
    INSERT INTO Author VALUES 
    ('K.S. Verma','Science Colony, Pune','kverma.co.in'),
    ('Dr. Immy Khan','Navi Mumbai, Mumbai','booksbyimmy.com'),
    ('Dilip Singh', 'College Road, Nashik','wordsofdilip.com'),
    ('Pravin Goyal', 'Budhwar Peth, Pune','blog.pravingoyal.com'),
    ('Dr. Chucks', 'Texas, USA','pythonbychucks.com'),
    ('John Roy','Silicon Valley, USA','johnroy.us');
""")
cur.execute("""
    INSERT INTO Book VALUES 
    (120001,'Pythons For Beginners',2019,158.99,100,'Technic','K.S. Verma'),
    (110021,'C/C++ For Beginners',1999,135.00,50,'Technic', 'Dilip Singh'),
    (120003,'Ruby on Rails For Beginners',2019,219.68,500,'Technic', 'Dr. Immy Khan'),
    (120021,'Python Advanced',2021,190.78,100,'Technic','K.S. Verma'),
    (108901,'Python For Everybody By Dr. Chucks',2012,0,1,NULL,'Dr. Chucks'),
    (120008,'The Secret Of Life',2021,390.89,30,'Neo Books','Pravin Goyal'),
    (100001,'Archive: Microchips',1987,0,1,'Open Archives',NULL),
    (100007,'Archive: High Speed Connectivity via Water',1993,0,1,'Open Archives',NULL);
""")
cur.execute("INSERT INTO Customer VALUES ('username@domain.com','User1','9812345678','Manjari, Pune')") # Sample User
cur.execute("INSERT INTO  ShoppingBasket VALUES ('username@domain.com',120001);") # Sample Book
cur.execute("INSERT INTO  ShoppingBasket VALUES ('username@domain.com',120001);") # Sample Book
cur.execute("INSERT INTO  ShoppingBasket VALUES ('username@domain.com',120021);") # Sample Book
cur.execute("INSERT INTO  ShoppingBasket VALUES ('username@domain.com',120021);") # Sample Book
cur.execute("INSERT INTO  ShoppingBasket VALUES ('username@domain.com',120021);") # Sample Book


# %%
# Commiting Changes
mydb.commit()