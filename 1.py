import streamlit as st
import datetime
import pandas as pd

st.set_page_config(page_title="Library Management System", layout="wide")

# ------------------ SESSION INITIALIZATION ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = ""
if "books" not in st.session_state:
    st.session_state.books = []
if "memberships" not in st.session_state:
    st.session_state.memberships = []
if "issued_books" not in st.session_state:
    st.session_state.issued_books = []
if "return_data" not in st.session_state:
    st.session_state.return_data = None


# ------------------ LOGIN ------------------
def login():
    st.title("📚 Library Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.success("Admin Logged In")
        elif username == "user" and password == "user123":
            st.session_state.logged_in = True
            st.session_state.role = "user"
            st.success("User Logged In")
        else:
            st.error("Invalid Credentials")


# ------------------ USER MANAGEMENT ------------------
def user_management():
    st.subheader("User Management")

    option = st.radio("Select Option", ["New User", "Existing User"], index=0)

    name = st.text_input("Name")

    if st.button("Confirm User"):
        if not name:
            st.error("Name is mandatory")
        else:
            st.success(f"{option} processed successfully")


# ------------------ ADD BOOK ------------------
def add_book():
    st.subheader("Add Book")

    category = st.radio("Select Type", ["Book", "Movie"], index=0)
    title = st.text_input("Title")
    author = st.text_input("Author")
    serial = st.text_input("Serial Number")

    if st.button("Add"):
        if not title or not author or not serial:
            st.error("All fields are mandatory")
        else:
            st.session_state.books.append({
                "category": category,
                "title": title,
                "author": author,
                "serial": serial
            })
            st.success("Added Successfully")


# ------------------ UPDATE BOOK ------------------
def update_book():
    st.subheader("Update Book")

    category = st.radio("Select Type", ["Book", "Movie"], index=0)
    title = st.text_input("Title to Update")
    new_author = st.text_input("New Author")
    new_serial = st.text_input("New Serial")

    if st.button("Update"):
        if not title or not new_author or not new_serial:
            st.error("All fields are mandatory")
            return

        for book in st.session_state.books:
            if book["title"] == title:
                book["author"] = new_author
                book["serial"] = new_serial
                st.success("Updated Successfully")
                return

        st.error("Book not found")


# ------------------ SEARCH BOOK ------------------
def search_book():
    st.subheader("Book Available")

    if not st.session_state.books:
        st.warning("No books available")
        return

    df = pd.DataFrame(st.session_state.books)
    selection = st.radio("Select Book", df["title"])

    if not selection:
        st.error("Please make a valid selection")
    else:
        st.success(f"{selection} selected")


# ------------------ ISSUE BOOK ------------------
def issue_book():
    st.subheader("Issue Book")

    if not st.session_state.books:
        st.warning("No books available")
        return

    titles = [b["title"] for b in st.session_state.books]
    selected = st.selectbox("Select Book", titles)

    book = next(b for b in st.session_state.books if b["title"] == selected)

    st.text_input("Author", value=book["author"], disabled=True)

    today = datetime.date.today()
    issue_date = st.date_input("Issue Date", min_value=today)
    return_date = st.date_input("Return Date", value=today + datetime.timedelta(days=15))

    remarks = st.text_area("Remarks")

    if st.button("Issue"):
        if return_date > issue_date + datetime.timedelta(days=15):
            st.error("Return date cannot exceed 15 days")
        else:
            st.session_state.issued_books.append({
                "title": selected,
                "author": book["author"],
                "issue_date": issue_date,
                "due_date": return_date
            })
            st.success("Book Issued Successfully")


# ------------------ RETURN BOOK ------------------
def return_book():
    st.subheader("Return Book")

    if not st.session_state.issued_books:
        st.warning("No issued books")
        return

    titles = [b["title"] for b in st.session_state.issued_books]
    selected = st.selectbox("Select Book", titles)

    book = next(b for b in st.session_state.issued_books if b["title"] == selected)

    st.text_input("Author", value=book["author"], disabled=True)
    st.text_input("Issue Date", value=str(book["issue_date"]), disabled=True)

    return_date = st.date_input("Return Date", value=book["due_date"])

    serial = st.text_input("Serial Number")

    if st.button("Confirm Return"):
        if not serial:
            st.error("Serial Number is mandatory")
            return

        delay = (return_date - book["due_date"]).days
        fine = delay * 5 if delay > 0 else 0

        st.session_state.return_data = {
            "title": selected,
            "fine": fine
        }

        st.success("Proceed to Fine Payment")


# ------------------ FINE PAY ------------------
def fine_pay():
    st.subheader("Fine Payment")

    data = st.session_state.return_data

    if not data:
        st.warning("No return initiated")
        return

    st.write("Book:", data["title"])
    st.write("Fine Amount:", data["fine"])

    paid = st.checkbox("Fine Paid")
    remarks = st.text_area("Remarks")

    if st.button("Confirm Payment"):
        if data["fine"] > 0 and not paid:
            st.error("Fine payment required")
        else:
            st.session_state.issued_books = [
                b for b in st.session_state.issued_books
                if b["title"] != data["title"]
            ]
            st.session_state.return_data = None
            st.success("Book Returned Successfully")


# ------------------ MEMBERSHIP ------------------
def add_membership():
    st.subheader("Add Membership")

    name = st.text_input("Member Name")
    plan = st.radio("Plan", ["6 Months", "1 Year", "2 Years"], index=0)

    if st.button("Add Membership"):
        if not name:
            st.error("All fields mandatory")
        else:
            st.session_state.memberships.append({
                "name": name,
                "plan": plan
            })
            st.success("Membership Added")


def update_membership():
    st.subheader("Update Membership")

    name = st.text_input("Membership Name")

    extend = st.radio("Action", ["Extend 6 Months", "Cancel"], index=0)

    if st.button("Update"):
        if not name:
            st.error("Membership Number required")
            return

        st.success("Membership Updated")


# ------------------ MAIN APP ------------------
if not st.session_state.logged_in:
    login()
else:
    st.sidebar.title("Navigation")

    menu = ["Search Book", "Issue Book", "Return Book", "Fine Pay"]

    if st.session_state.role == "admin":
        menu.extend([
            "Add Book", "Update Book",
            "Add Membership", "Update Membership",
            "User Management"
        ])

    choice = st.sidebar.radio("Menu", menu)

    if choice == "Search Book":
        search_book()
    elif choice == "Issue Book":
        issue_book()
    elif choice == "Return Book":
        return_book()
    elif choice == "Fine Pay":
        fine_pay()
    elif choice == "Add Book":
        add_book()
    elif choice == "Update Book":
        update_book()
    elif choice == "Add Membership":
        add_membership()
    elif choice == "Update Membership":
        update_membership()
    elif choice == "User Management":
        user_management()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = ""
        st.experimental_rerun()
