# ============================================================
# Library Management System (Production-Ready Example)
# Tech: Python + Streamlit + SQLite + Pandas
# ============================================================

import streamlit as st
import sqlite3
import pandas as pd
import datetime
import hashlib

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="Library Management System", layout="wide")

# ------------------------------------------------------------
# DATABASE CONNECTION
# ------------------------------------------------------------
conn = sqlite3.connect("library.db", check_same_thread=False)
cursor = conn.cursor()

# ------------------------------------------------------------
# DATABASE TABLES
# ------------------------------------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
username TEXT UNIQUE,
password TEXT,
role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS books(
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT,
author TEXT,
serial TEXT UNIQUE,
type TEXT,
status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS members(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
plan TEXT,
start_date TEXT,
end_date TEXT,
status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS issued_books(
id INTEGER PRIMARY KEY AUTOINCREMENT,
book_id INTEGER,
title TEXT,
author TEXT,
issue_date TEXT,
return_date TEXT,
remarks TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS fines(
id INTEGER PRIMARY KEY AUTOINCREMENT,
book_id INTEGER,
title TEXT,
fine_amount INTEGER,
paid INTEGER
)
""")

conn.commit()

# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_books():
    return pd.read_sql("SELECT * FROM books", conn)

def get_available_books():
    return pd.read_sql("SELECT * FROM books WHERE status='Available'", conn)

def get_issued_books():
    return pd.read_sql("SELECT * FROM issued_books", conn)

def get_members():
    return pd.read_sql("SELECT * FROM members", conn)

def get_users():
    return pd.read_sql("SELECT * FROM users", conn)

def calculate_fine(return_date):
    today = datetime.date.today()
    delay = (today - return_date).days
    if delay > 0:
        return delay * 5
    return 0

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None

# ------------------------------------------------------------
# LOGIN PAGE
# ------------------------------------------------------------
def login_page():

    st.title("Library Management System Login")

    username = st.text_input("Username")

    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if not username or not password:
            st.error("Enter username and password")
            return

        hashed = hash_password(password)

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hashed)
        )

        user = cursor.fetchone()

        if user:
            st.session_state.logged_in = True
            st.session_state.role = user[4]
            st.session_state.username = user[1]
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

# ------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------
def dashboard():

    st.header("Dashboard")

    books = get_books()
    issued = get_issued_books()
    members = get_members()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Books", len(books))
    col2.metric("Issued Books", len(issued))
    col3.metric("Members", len(members))

# ------------------------------------------------------------
# ADD BOOK
# ------------------------------------------------------------
def add_book():

    st.subheader("Add Book")

    book_type = st.radio(
        "Type",
        ["Book", "Movie"],
        index=0
    )

    title = st.text_input("Title")
    author = st.text_input("Author")
    serial = st.text_input("Serial Number")

    if st.button("Add Book"):

        if not title or not author or not serial:
            st.error("All fields mandatory")
            return

        cursor.execute("""
        INSERT INTO books(title,author,serial,type,status)
        VALUES(?,?,?,?,?)
        """, (title, author, serial, book_type, "Available"))

        conn.commit()

        st.success("Book added")

# ------------------------------------------------------------
# UPDATE BOOK
# ------------------------------------------------------------
def update_book():

    st.subheader("Update Book")

    serial = st.text_input("Enter Serial Number")

    if st.button("Fetch Book"):

        cursor.execute(
            "SELECT * FROM books WHERE serial=?",
            (serial,)
        )

        book = cursor.fetchone()

        if not book:
            st.error("Book not found")
            return

        st.session_state.book_data = book

    if "book_data" in st.session_state:

        book = st.session_state.book_data

        title = st.text_input("Title", value=book[1])
        author = st.text_input("Author", value=book[2])

        book_type = st.radio(
            "Type",
            ["Book", "Movie"],
            index=0 if book[4]=="Book" else 1
        )

        if st.button("Update Book"):

            if not title or not author:
                st.error("All fields mandatory")
                return

            cursor.execute("""
            UPDATE books
            SET title=?,author=?,type=?
            WHERE serial=?
            """, (title, author, book_type, serial))

            conn.commit()

            st.success("Book updated")

# ------------------------------------------------------------
# BOOK AVAILABLE SEARCH
# ------------------------------------------------------------
def search_books():

    st.subheader("Book Available")

    title = st.text_input("Book Title")
    author = st.text_input("Author")

    if st.button("Search"):

        if title=="" and author=="":
            st.error("Fill at least one field")
            return

        query = "SELECT * FROM books WHERE status='Available'"

        if title:
            query += f" AND title LIKE '%{title}%'"

        if author:
            query += f" AND author LIKE '%{author}%'"

        df = pd.read_sql(query, conn)

        if df.empty:
            st.warning("No books found")
        else:
            st.dataframe(df)

# ------------------------------------------------------------
# ISSUE BOOK
# ------------------------------------------------------------
def issue_book():

    st.subheader("Issue Book")

    books = get_available_books()

    if books.empty:
        st.warning("No available books")
        return

    book_title = st.selectbox(
        "Book Name",
        books["title"]
    )

    selected = books[books["title"]==book_title].iloc[0]

    st.text_input(
        "Author",
        value=selected["author"],
        disabled=True
    )

    issue_date = st.date_input(
        "Issue Date",
        min_value=datetime.date.today()
    )

    default_return = datetime.date.today()+datetime.timedelta(days=15)

    return_date = st.date_input(
        "Return Date",
        value=default_return
    )

    remarks = st.text_area("Remarks")

    if st.button("Confirm Issue"):

        if issue_date < datetime.date.today():
            st.error("Issue date invalid")
            return

        if return_date > default_return:
            st.error("Return date cannot exceed 15 days")
            return

        cursor.execute("""
        INSERT INTO issued_books
        (book_id,title,author,issue_date,return_date,remarks)
        VALUES(?,?,?,?,?,?)
        """, (
            selected["id"],
            selected["title"],
            selected["author"],
            issue_date,
            return_date,
            remarks
        ))

        cursor.execute(
            "UPDATE books SET status='Issued' WHERE id=?",
            (selected["id"],)
        )

        conn.commit()

        st.success("Book issued")

# ------------------------------------------------------------
# RETURN BOOK
# ------------------------------------------------------------
def return_book():

    st.subheader("Return Book")

    issued = get_issued_books()

    if issued.empty:
        st.info("No issued books")
        return

    book_title = st.selectbox(
        "Book Name",
        issued["title"]
    )

    selected = issued[issued["title"]==book_title].iloc[0]

    st.text_input("Author", value=selected["author"], disabled=True)

    serial = st.text_input("Serial Number")

    st.date_input(
        "Issue Date",
        value=datetime.date.fromisoformat(selected["issue_date"]),
        disabled=True
    )

    return_date = st.date_input(
        "Return Date",
        value=datetime.date.fromisoformat(selected["return_date"])
    )

    if st.button("Confirm Return"):

        if not serial:
            st.error("Serial number mandatory")
            return

        fine = calculate_fine(
            datetime.date.fromisoformat(selected["return_date"])
        )

        cursor.execute("""
        INSERT INTO fines(book_id,title,fine_amount,paid)
        VALUES(?,?,?,?)
        """, (
            selected["book_id"],
            selected["title"],
            fine,
            0
        ))

        conn.commit()

        st.session_state.fine_book = selected["title"]

        st.success("Proceed to Fine Pay page")

# ------------------------------------------------------------
# FINE PAYMENT
# ------------------------------------------------------------
def fine_payment():

    st.subheader("Fine Pay")

    fines = pd.read_sql("SELECT * FROM fines WHERE paid=0", conn)

    if fines.empty:
        st.success("No pending fines")
        return

    book = st.selectbox("Book", fines["title"])

    selected = fines[fines["title"]==book].iloc[0]

    st.number_input(
        "Fine Amount",
        value=int(selected["fine_amount"]),
        disabled=True
    )

    fine_paid = st.checkbox("Fine Paid")

    remarks = st.text_area("Remarks")

    if st.button("Confirm Payment"):

        if selected["fine_amount"]>0 and not fine_paid:
            st.error("Fine must be paid")
            return

        cursor.execute(
            "UPDATE fines SET paid=1 WHERE id=?",
            (selected["id"],)
        )

        cursor.execute(
            "DELETE FROM issued_books WHERE title=?",
            (selected["title"],)
        )

        cursor.execute(
            "UPDATE books SET status='Available' WHERE title=?",
            (selected["title"],)
        )

        conn.commit()

        st.success("Transaction completed")

# ------------------------------------------------------------
# ADD MEMBERSHIP
# ------------------------------------------------------------
def add_membership():

    st.subheader("Add Membership")

    name = st.text_input("Member Name")

    plan = st.radio(
        "Plan",
        ["6 Months","1 Year","2 Years"],
        index=0
    )

    if st.button("Add Membership"):

        if not name:
            st.error("All fields mandatory")
            return

        start = datetime.date.today()

        if plan=="6 Months":
            end = start + datetime.timedelta(days=180)
        elif plan=="1 Year":
            end = start + datetime.timedelta(days=365)
        else:
            end = start + datetime.timedelta(days=730)

        cursor.execute("""
        INSERT INTO members(name,plan,start_date,end_date,status)
        VALUES(?,?,?,?,?)
        """, (name, plan, start, end, "Active"))

        conn.commit()

        st.success("Membership added")

# ------------------------------------------------------------
# USER MANAGEMENT
# ------------------------------------------------------------
def user_management():

    st.subheader("User Management")

    mode = st.radio(
        "Mode",
        ["New User","Existing"],
        index=0
    )

    name = st.text_input("Name")

    username = st.text_input("Username")

    password = st.text_input("Password", type="password")

    role = st.selectbox("Role", ["User","Admin"])

    if st.button("Save User"):

        if not name:
            st.error("Name mandatory")
            return

        cursor.execute("""
        INSERT INTO users(name,username,password,role)
        VALUES(?,?,?,?)
        """, (name, username, hash_password(password), role))

        conn.commit()

        st.success("User created")

# ------------------------------------------------------------
# REPORTS
# ------------------------------------------------------------
def reports():

    st.subheader("Reports")

    report = st.selectbox(
        "Select Report",
        [
            "Available Books",
            "Issued Books",
            "Members",
            "Fines"
        ]
    )

    if report=="Available Books":
        df = pd.read_sql(
            "SELECT * FROM books WHERE status='Available'",
            conn
        )

    elif report=="Issued Books":
        df = pd.read_sql(
            "SELECT * FROM issued_books",
            conn
        )

    elif report=="Members":
        df = get_members()

    else:
        df = pd.read_sql(
            "SELECT * FROM fines",
            conn
        )

    st.dataframe(df)

# ------------------------------------------------------------
# MAIN APPLICATION
# ------------------------------------------------------------
if not st.session_state.logged_in:

    login_page()

else:

    st.sidebar.title("Menu")

    menu = ["Dashboard","Reports","Transactions"]

    if st.session_state.role=="Admin":
        menu.append("Maintenance")

    section = st.sidebar.radio("Navigation", menu)

    if section=="Dashboard":
        dashboard()

    elif section=="Reports":
        reports()

    elif section=="Transactions":

        page = st.sidebar.selectbox(
            "Transactions",
            [
                "Book Available",
                "Issue Book",
                "Return Book",
                "Fine Pay"
            ]
        )

        if page=="Book Available":
            search_books()

        elif page=="Issue Book":
            issue_book()

        elif page=="Return Book":
            return_book()

        elif page=="Fine Pay":
            fine_payment()

    elif section=="Maintenance":

        page = st.sidebar.selectbox(
            "Maintenance",
            [
                "Add Book",
                "Update Book",
                "Add Membership",
                "User Management"
            ]
        )

        if page=="Add Book":
            add_book()

        elif page=="Update Book":
            update_book()

        elif page=="Add Membership":
            add_membership()

        elif page=="User Management":
            user_management()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in=False
        st.rerun()
# CREATE DEFAULT USERS (RUN ONLY ONCE)

cursor.execute("SELECT * FROM users")
data = cursor.fetchall()

if len(data) == 0:

    cursor.execute("""
    INSERT INTO users(name,username,password,role)
    VALUES(?,?,?,?)
    """, (
        "Admin",
        "admin",
        hash_password("admin123"),
        "Admin"
    ))

    cursor.execute("""
    INSERT INTO users(name,username,password,role)
    VALUES(?,?,?,?)
    """, (
        "Library User",
        "user",
        hash_password("user123"),
        "User"
    ))

    conn.commit()