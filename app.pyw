
# %%
# Importing MySQL Connector
import mysql.connector as mysql

from tkinter import *
from tkinter.font import Font, BOLD
import tkinter.messagebox as MessageBox

# %%
# Connect to book_store Database 
mydb = mysql.connect(
    host="localhost",
    database="book_store",
    user="root",
    passwd="root")
mydb.is_connected()

# Get Cursor & Store it in reference to execute query;
cur = mydb.cursor()

# %%
# Database & Utility Functions

def commitToDB():
    mydb.commit()

def parseData(data):
    tempArr = []
    for i in data:
        if (isinstance(i, str)):
            if (i == ''):
                tempArr.append("NULL")
                continue
            tempArr.append("'"+i+"'")
        else:
            tempArr.append(str(i))
    return ",".join(tempArr)

# %%
# SQL-Tkinter Functions
def searchInTable(tablename, search_col, search_value):
    cur.execute("SELECT COUNT(*) FROM {} WHERE {}={}".format(tablename, search_col, search_value))
    return (cur.fetchall()[0][0] >= 1)

def searchInTable2(tablename, search_col, search_value, search_col2, search_value2):
    cur.execute("SELECT COUNT(*) FROM {} WHERE {}='{}' and {}='{}'".format(tablename, search_col, search_value, search_col2, search_value2))
    return (cur.fetchall()[0][0] >= 1)

def showTable(tablename):
    top = Toplevel()
    top.title(tablename+"s")
    cur.execute("SELECT * FROM {}".format(tablename))
    for i, col_name in enumerate(map(lambda x:x[0].capitalize(),cur.description)):
        labelFont = Font(family='Arial', weight=BOLD, size=10)
        e = Label(top,text=col_name, fg='black', font=labelFont)
        e.grid(row=0, column=i)
    for i, student in enumerate(cur.fetchall()):
        for j in range(len(student)):
            e = Label(top, text=str(student[j]), fg='black')
            e.grid(row=i+1, column=j)

def deleteTableRow(tablename, col, value):
    if(searchInTable(tablename,col,value)):
        cur.execute("DELETE FROM {} WHERE {}={}".format(tablename,col,value))
        commitToDB()
        MessageBox.showwarning("Database Updated", "Entry Deleted in {}.".format(tablename))
    else:
        MessageBox.showerror("Error", "No Entry Found in Table!")

def updateTableRow(tablename, col, value, search_col, search_value):
    if(searchInTable(tablename,search_col,search_value)):
        cur.execute("UPDATE {} SET {}={} WHERE {}={}".format(tablename, col, value, search_col, search_value))
        commitToDB()
        MessageBox.showinfo("Database Updated", "{} updated.".format(tablename))
    else:
        MessageBox.showerror("Error", "No Entry Found in Table!")

def insertTableRow(tablename, data):
    try:
        cur.execute("INSERT INTO {} VALUES ({})".format(tablename, parseData(data)))
        commitToDB()
        MessageBox.showwarning("Database Updated", "Entry Added in {}.".format(tablename))
    except (mysql.Error) as e:
        MessageBox.showerror("Error", e)


# Users SQL-TKinter Fuctions
def showUserDetails(username):
    if not(searchInTable("Customer","email",parseData([username]))):
        MessageBox.showerror("Error","{} doesn't exist".format(username))
        return 
    top = Toplevel()
    top.title("User Details : {}".format(username))
    cur.execute("SELECT name, phone, address FROM Customer WHERE email='{}'".format(username))
    for i, col_name in enumerate(map(lambda x:x[0].capitalize(),cur.description)):
        labelFont = Font(family='Arial', weight=BOLD, size=9)
        e = Label(top,text=col_name, fg='black', font=labelFont)
        e.grid(row=i, column=0)
    for i, student in enumerate(cur.fetchall()):
        for j in range(len(student)):
            e = Label(top, text=str(student[j]), fg='black')
            e.grid(row=j, column=i+1)      

def checkoutBasket(top, username, price):
    top.destroy()
    if not(searchInTable("Customer","email",parseData([username]))):
        MessageBox.showerror("Error","{} doesn't exist".format(username))
        return 
    if(searchInTable("ShoppingBasket","email",parseData([username]))):
        cur.execute("DELETE FROM ShoppingBasket WHERE email='{}'".format(username))
        commitToDB()
        MessageBox.showinfo("Checkout Sucessfull", "Book Purchased, Total Cost: {0:.2f}.".format(price))
    else:
        MessageBox.showerror("Error", "No Books To Checkout!")

def showShoppingBasket(username):
    if not(searchInTable("Customer","email",parseData([username]))):
        MessageBox.showerror("Error","{} doesn't exist".format(username))
        return 
    top = Toplevel()
    top.title("Shopping Basket : {}".format(username))
    cur.execute("""SELECT Book.ISBN, Book.title, price ,COUNT(book_isbn) as 'quantity', SUM(Book.price) as 'total_price'
        FROM ShoppingBasket 
        JOIN Book ON ShoppingBasket.book_isbn = Book.ISBN
        WHERE email='{}'
        GROUP BY Book.ISBN;
        """.format(username))
    labelFont = Font(family='Arial', weight=BOLD, size=10)
    for i, col_name in enumerate(map(lambda x:x[0].capitalize(),cur.description)):
        e = Label(top,text=col_name, fg='black', font=labelFont)
        e.grid(row=0, column=i)
    finalPrice = 0
    for i, student in enumerate(cur.fetchall()):
        for j in range(len(student)):
            e = Label(top, text=str(student[j]), fg='black')
            if (j == len(student) -1 ):
                finalPrice += float(student[j])
            e.grid(row=i+1, column=j)
    finalPriceLabel = Label(top,text="Final Price : {0:.2f} /-".format(finalPrice), fg='black', font=labelFont)
    finalPriceLabel.grid()

    checkoutBtn = Button(top,text='Checkout', command=lambda: checkoutBasket(top,username,finalPrice))
    checkoutBtn.grid(column=4)

def deleteFromBasket(username, isbn):
    if not(searchInTable("Customer","email",parseData([username]))):
        MessageBox.showerror("Error","{} doesn't exist".format(username))
        return  
    if(searchInTable2("ShoppingBasket","book_isbn",isbn, "email", username)):
        cur.execute("DELETE FROM ShoppingBasket WHERE book_isbn='{}' and email='{}' LIMIT 1;".format(isbn,username))
        commitToDB()
        MessageBox.showwarning("Database Updated", "Entry Deleted in Shopping Basket.")
    else:
        MessageBox.showerror("Error", "No Entry Found in Table!")

def addToBasket(username, isbn):
    if not(searchInTable("Customer","email",parseData([username]))):
        MessageBox.showerror("Error","{} doesn't exist".format(username))
        return
    insertTableRow("ShoppingBasket", [username, isbn])

# %%
root = Tk()
root.title("Book Store Management")

# region AdminFrame[MAIN]
adminFrame = LabelFrame(root, text="Admin Tools", padx=5, pady=5)

# region ViewDataFrame
viewDataFrame = LabelFrame(adminFrame, text="View Data", padx=5, pady=5)

showBooksBtn = Button(viewDataFrame, text="Show Books", command = lambda : showTable("Book"))
showAuthorsBtn = Button(viewDataFrame, text="Show Authors", command = lambda : showTable("Author"))
showCustormersBtn = Button(viewDataFrame, text="Show All Customers", command = lambda : showTable("Customer"))
showPublishersBtn = Button(viewDataFrame, text="Show Publishers", command = lambda : showTable("Publisher"))
showBooksBtn.grid(row=0,column=1)
showAuthorsBtn.grid(row=0,column=2)
showCustormersBtn.grid(row=0,column=3)
showPublishersBtn.grid(row=0,column=4)

viewDataFrame.pack(fill='x')
# endregion

# region BookFrame
bookFrame = LabelFrame(adminFrame, text="Book Operations", padx=5, pady=5)

# region DeleteBook 
deleteFrame = LabelFrame(bookFrame, text="Delete Book", padx=5, pady=5)

isbn_df = IntVar()
isbn_df_label = Label(deleteFrame, text="ISBN:")
isbn_df_label.grid(row=0,column=0)
isbn_df_entry = Entry(deleteFrame, textvariable=isbn_df)
isbn_df_entry.grid(row=0,column=1)

df_button = Button(deleteFrame, text='Delete Book', command=lambda: deleteTableRow("Book", "ISBN", isbn_df.get()))
df_button.grid(row=1,column=0)

deleteFrame.pack(fill='x')
# endregion

# region UpdateBook
updateFrame = LabelFrame(bookFrame, text="Update Book", padx=5, pady=5)

isbn_uf = IntVar()
isbn_uf_label = Label(updateFrame, text="ISBN:")
isbn_uf_label.grid(row=0,column=0)
isbn_uf_entry = Entry(updateFrame, textvariable=isbn_uf)
isbn_uf_entry.grid(row=0,column=1)

cols_uf = ["price","stocks"]
col_uf = StringVar()
col_uf.set(cols_uf[0])
col_uf_option = OptionMenu(updateFrame, col_uf, *cols_uf)
col_uf_option.grid(row=1,column=0)
col_value_uf = IntVar()
col_value_uf_entry = Entry(updateFrame, textvariable=col_value_uf)
col_value_uf_entry.grid(row=1,column=1)


uf_button = Button(updateFrame, text='Update Book', command=lambda: updateTableRow("Book", col_uf.get(), col_value_uf.get(), "ISBN", isbn_uf.get()))
uf_button.grid(row=2,column=0)

updateFrame.pack(fill='x')
# endregion

# region InsertBook
insertFrame = LabelFrame(bookFrame, text="Insert Book", padx=5, pady=5)

isbn_if = IntVar()
isbn_if_label = Label(insertFrame, text="ISBN:")
isbn_if_label.grid(row=0,column=0)
isbn_if_entry = Entry(insertFrame, textvariable=isbn_if)
isbn_if_entry.grid(row=0,column=1)

title_if = StringVar()
title_if_label = Label(insertFrame, text="Title:")
title_if_label.grid(row=1,column=0)
title_if_entry = Entry(insertFrame, textvariable=title_if)
title_if_entry.grid(row=1,column=1)

year_if = IntVar()
year_if_label = Label(insertFrame, text="Year:")
year_if_label.grid(row=2,column=0)
year_if_entry = Entry(insertFrame, textvariable=year_if)
year_if_entry.grid(row=2,column=1)


price_if = DoubleVar()
price_if_label = Label(insertFrame, text="Price:")
price_if_label.grid(row=3,column=0)
price_if_entry = Entry(insertFrame, textvariable=price_if)
price_if_entry.grid(row=3,column=1)

stocks_if = IntVar()
stocks_if_label = Label(insertFrame, text="Stocks:")
stocks_if_label.grid(row=4,column=0)
stocks_if_entry = Entry(insertFrame, textvariable=stocks_if)
stocks_if_entry.grid(row=4,column=1)

publisher_if = StringVar()
publisher_if_label = Label(insertFrame, text="Publisher (FK):")
publisher_if_label.grid(row=5,column=0)
publisher_if_entry = Entry(insertFrame, textvariable=publisher_if)
publisher_if_entry.grid(row=5,column=1)

author_if = StringVar()
author_if_label = Label(insertFrame, text="Author (FK):")
author_if_label.grid(row=6,column=0)
author_if_entry = Entry(insertFrame, textvariable=author_if)
author_if_entry.grid(row=6,column=1)

if_button = Button(
    insertFrame, 
    text='Insert Book', 
    command=lambda: insertTableRow("Book", [
        isbn_if.get(),
        title_if.get(),
        year_if.get(),
        price_if.get(),
        stocks_if.get(),
        publisher_if.get(),
        author_if.get()
    ])
    )
if_button.grid(row=7,column=0)

insertFrame.pack(fill='x')
# endregion

bookFrame.pack(side='left')
# endregion

# region AuthorFrame
authorFrame = LabelFrame(adminFrame, text="Author Operations", padx=5, pady=5)

# region DeleteAuthor
deleteFrame_A = LabelFrame(authorFrame, text="Delete Author", padx=5, pady=5)

name_df_A = StringVar()
name_df_label_A = Label(deleteFrame_A, text="Name:")
name_df_label_A.grid(row=0,column=0)
name_df_entry_A = Entry(deleteFrame_A, textvariable=name_df_A)
name_df_entry_A.grid(row=0,column=1)

df_button_A = Button(deleteFrame_A, text='Delete Author', command=lambda: deleteTableRow("Author", "name", parseData([name_df_A.get()])))
df_button_A.grid(row=1,column=0)

deleteFrame_A.pack(fill='x')
# endregion

# region UpdateAuthor
updateFrame_A = LabelFrame(authorFrame, text="Update Author", padx=5, pady=5)

name_uf_A = StringVar()
name_uf_label_A = Label(updateFrame_A, text="Name:")
name_uf_label_A.grid(row=0,column=0)
name_uf_entry_A = Entry(updateFrame_A, textvariable=name_uf_A)
name_uf_entry_A.grid(row=0,column=1)

cols_uf_A = ["url","address"]
col_uf_A = StringVar()
col_uf_A.set(cols_uf_A[0])
col_uf_option_A = OptionMenu(updateFrame_A, col_uf_A, *cols_uf_A)
col_uf_option_A.grid(row=1,column=0)
col_value_uf_A = StringVar()
col_value_uf_entry_A = Entry(updateFrame_A, textvariable=col_value_uf_A)
col_value_uf_entry_A.grid(row=1,column=1)

uf_button_A = Button(updateFrame_A, text='Update Author', command=lambda: updateTableRow(
    "Author", 
    col_uf_A.get(), 
    parseData([col_value_uf_A.get()]), 
    "name", 
    parseData([name_uf_A.get()])
    ))
uf_button_A.grid(row=2,column=0)

updateFrame_A.pack(fill='x')
# endregion

# region InsertAuthor
insertFrame_A = LabelFrame(authorFrame, text="Insert Author", padx=5, pady=5)

name_if_A = StringVar()
name_if_label_A = Label(insertFrame_A, text="Name:")
name_if_label_A.grid(row=0,column=0)
name_if_entry_A = Entry(insertFrame_A, textvariable=name_if_A)
name_if_entry_A.grid(row=0,column=1)

address_if_A = StringVar()
address_if_label_A = Label(insertFrame_A, text="Address:")
address_if_label_A.grid(row=1,column=0)
address_if_entry_A = Entry(insertFrame_A, textvariable=address_if_A)
address_if_entry_A.grid(row=1,column=1)

url_if_A = StringVar()
url_if_label_A = Label(insertFrame_A, text="Url:")
url_if_label_A.grid(row=2,column=0)
url_if_entry_A = Entry(insertFrame_A, textvariable=url_if_A)
url_if_entry_A.grid(row=2,column=1)

if_button_A = Button(
    insertFrame_A, 
    text='Insert Author', 
    command=lambda: insertTableRow("Author", [
        name_if_A.get(),
        address_if_A.get(),
        url_if_A.get()
    ])
    )
if_button_A.grid(row=3,column=0)

insertFrame_A.pack(fill='x')
# endregion

authorFrame.pack(side='left', fill='both')
# endregion

# region UserSubFrame
customerFrame = LabelFrame(adminFrame, text="Customer Operations", padx=5, pady=5)

# region DeleteUser
deleteFrame_U = LabelFrame(customerFrame, text="Delete Customer", padx=5, pady=5)

email_df_U = StringVar()
email_df_label_U = Label(deleteFrame_U, text="email:")
email_df_label_U.grid(row=0,column=0)
email_df_entry_U = Entry(deleteFrame_U, textvariable=email_df_U)
email_df_entry_U.grid(row=0,column=1)

df_button_U = Button(deleteFrame_U, text='Delete Customer', command=lambda: deleteTableRow("Customer", "email", parseData([email_df_U.get()])))
df_button_U.grid(row=1,column=0)

deleteFrame_U.pack(fill='x')
# endregion

# region UpdateUser
updateFrame_U = LabelFrame(customerFrame, text="Update User", padx=5, pady=5)

email_uf_U = StringVar()
email_uf_label_U = Label(updateFrame_U, text="Email:")
email_uf_label_U.grid(row=0,column=0)
email_uf_entry_U = Entry(updateFrame_U, textvariable=email_uf_U)
email_uf_entry_U.grid(row=0,column=1)

cols_uf_U = ["name","address","phone"]
col_uf_U = StringVar()
col_uf_U.set(cols_uf_U[0])
col_uf_option_U = OptionMenu(updateFrame_U, col_uf_U, *cols_uf_U)
col_uf_option_U.grid(row=1,column=0)
col_value_uf_U = StringVar()
col_value_uf_entry_U = Entry(updateFrame_U, textvariable=col_value_uf_U)
col_value_uf_entry_U.grid(row=1,column=1)

uf_button_U = Button(updateFrame_U, text='Update Customer', command=lambda: updateTableRow(
    "Customer", 
    col_uf_U.get(), 
    parseData([col_value_uf_U.get()]), 
    "email", 
    parseData([email_uf_U.get()])
    ))
uf_button_U.grid(row=2,column=0)

updateFrame_U.pack(fill='x')
# endregion

# region InsertUser
insertFrame_U = LabelFrame(customerFrame, text="Insert Customer", padx=5, pady=5)

email_if_U = StringVar()
email_if_label_U = Label(insertFrame_U, text="Email:")
email_if_label_U.grid(row=0,column=0)
email_if_entry_U = Entry(insertFrame_U, textvariable=email_if_U)
email_if_entry_U.grid(row=0,column=1)

name_if_U = StringVar()
name_if_label_U = Label(insertFrame_U, text="Name:")
name_if_label_U.grid(row=1,column=0)
name_if_entry_U = Entry(insertFrame_U, textvariable=name_if_U)
name_if_entry_U.grid(row=1,column=1)

phone_if_U = StringVar()
phone_if_label_U = Label(insertFrame_U, text="Phone:")
phone_if_label_U.grid(row=2,column=0)
phone_if_entry_U = Entry(insertFrame_U, textvariable=phone_if_U)
phone_if_entry_U.grid(row=2,column=1)

address_if_U = StringVar()
address_if_label_U = Label(insertFrame_U, text="Address:")
address_if_label_U.grid(row=3,column=0)
address_if_entry_U = Entry(insertFrame_U, textvariable=address_if_U)
address_if_entry_U.grid(row=3,column=1)

if_button_U = Button(
    insertFrame_U, 
    text='Insert Customer', 
    command=lambda: insertTableRow("Customer", [
        email_if_U.get(),
        name_if_U.get(),
        phone_if_U.get(),
        address_if_U.get()
    ])
    )
if_button_U.grid(row=4,column=0)

insertFrame_U.pack(fill='x')
# endregion

customerFrame.pack(side='left', fill='both')
# endregion

# region PublisherFrame
publisherFrame = LabelFrame(adminFrame, text="Publisher Operations", padx=5, pady=5)

# region DeletePublisher
deleteFrame_P = LabelFrame(publisherFrame, text="Delete Publisher", padx=5, pady=5)

name_df_P = StringVar()
name_df_label_P = Label(deleteFrame_P, text="Name:")
name_df_label_P.grid(row=0,column=0)
name_df_entry_P = Entry(deleteFrame_P, textvariable=name_df_P)
name_df_entry_P.grid(row=0,column=1)

df_button_P = Button(deleteFrame_P, text='Delete Publisher', command=lambda: deleteTableRow("Publisher", "name", parseData([name_df_P.get()])))
df_button_P.grid(row=1,column=0)

deleteFrame_P.pack(fill='x')
# endregion

# region UpdatePublisher
updateFrame_P = LabelFrame(publisherFrame, text="Update Publisher", padx=5, pady=5)

name_uf_P = StringVar()
name_uf_label_P = Label(updateFrame_P, text="Name:")
name_uf_label_P.grid(row=0,column=0)
name_uf_entry_P = Entry(updateFrame_P, textvariable=name_uf_P)
name_uf_entry_P.grid(row=0,column=1)

cols_uf_P = ["url","address","phone"]
col_uf_P = StringVar()
col_uf_P.set(cols_uf_P[0])
col_uf_option_P = OptionMenu(updateFrame_P, col_uf_P, *cols_uf_P)
col_uf_option_P.grid(row=1,column=0)
col_value_uf_P = StringVar()
col_value_uf_entry_P = Entry(updateFrame_P, textvariable=col_value_uf_P)
col_value_uf_entry_P.grid(row=1,column=1)

uf_button_P = Button(updateFrame_P, text='Update Publisher', command=lambda: updateTableRow(
    "Publisher", 
    col_uf_P.get(), 
    parseData([col_value_uf_P.get()]), 
    "name", 
    parseData([name_uf_P.get()])
    ))
uf_button_P.grid(row=2,column=0)

updateFrame_P.pack(fill='x')
# endregion

# region InsertPublisher
insertFrame_P = LabelFrame(publisherFrame, text="Insert Publisher", padx=5, pady=5)

name_if_P = StringVar()
name_if_label_P = Label(insertFrame_P, text="Name:")
name_if_label_P.grid(row=0,column=0)
name_if_entry_P = Entry(insertFrame_P, textvariable=name_if_P)
name_if_entry_P.grid(row=0,column=1)

address_if_P = StringVar()
address_if_label_P = Label(insertFrame_P, text="Address:")
address_if_label_P.grid(row=1,column=0)
address_if_entry_P = Entry(insertFrame_P, textvariable=address_if_P)
address_if_entry_P.grid(row=1,column=1)

phone_if_P = StringVar()
phone_if_label_P = Label(insertFrame_P, text="Phone:")
phone_if_label_P.grid(row=2,column=0)
phone_if_entry_P = Entry(insertFrame_P, textvariable=phone_if_P)
phone_if_entry_P.grid(row=2,column=1)

url_if_P = StringVar()
url_if_label_P = Label(insertFrame_P, text="Url:")
url_if_label_P.grid(row=3,column=0)
url_if_entry_P = Entry(insertFrame_P, textvariable=url_if_P)
url_if_entry_P.grid(row=3,column=1)

if_button_P = Button(
    insertFrame_P, 
    text='Insert Publisher', 
    command=lambda: insertTableRow("Publisher", [
        name_if_P.get(),
        address_if_P.get(),
        phone_if_P.get(),
        url_if_P.get()
    ])
    )
if_button_P.grid(row=4,column=0)

insertFrame_P.pack(fill='x')
# endregion

publisherFrame.pack(side='left', fill='both')
# endregion


adminFrame.pack()
# endregion

# region UserFrame[MAIN]
email = StringVar()
email.set("username@domain.com")
userFrame = LabelFrame(root, text="User Tools", padx=5, pady=5)

emailFrame = Frame(userFrame)
email_label = Label(emailFrame, text="Email:")
email_label.pack(side='left')
email_entry = Entry(emailFrame, textvariable=email, width=100)
email_entry.pack(side='left')
emailFrame.pack()



buttonFrame = Frame(userFrame)
showUserDetailsBtn = Button(buttonFrame, text="Show User Details", command = lambda : showUserDetails(email.get()))
showUserDetailsBtn.pack(side='left')
showShoppingBasketBtn = Button(buttonFrame, text="Show Shopping Basket", command = lambda : showShoppingBasket(email.get()))
showShoppingBasketBtn.pack(side='left')
buttonFrame.pack()

adddeleteBookFrame = LabelFrame(userFrame, text="Add/Delete Book To Basket")

isbnToAdd = IntVar()
isbnToAdd_label = Label(adddeleteBookFrame, text="ISBN (FK):")
isbnToAdd_label.pack(side='left')
isbnToAdd_entry = Entry(adddeleteBookFrame, textvariable=isbnToAdd)
isbnToAdd_entry.pack(side='left')

addBookBtn = Button(adddeleteBookFrame, text="Add Book", command = lambda : addToBasket(email.get(), isbnToAdd.get()))
addBookBtn.pack(side='left')

deleteBookBtn = Button(adddeleteBookFrame, text="Delete Book", command = lambda : deleteFromBasket(email.get(),isbnToAdd.get()))
deleteBookBtn.pack(side='left')

adddeleteBookFrame.pack(fill='x')


userFrame.pack(fill='both')

# showShoppingBasket('username@domain.com')
# endregion

root.mainloop()
