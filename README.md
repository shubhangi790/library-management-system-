# 📚 Library Management System – Streamlit App

A fully functional Library Management System developed using Python and Streamlit.  
The application supports role-based login, book management, membership handling, issuing and returning books, and automated fine calculation with proper validations.
dmin Access
-Default Login Credentials

-Admin
Username: admin  
Password: admin123  

-User
Username: user  
Password: user123  


---

Features

role-Based Login
- Admin and User access
- Session-based authentication

Book Management
- Add Book / Movie
- Update Book / Movie
- Search available books

Issue Book
- Auto-populated author details
- Issue date cannot be less than today
- Return date limited to 15 days
- Form validation enforcement

Return Book
- Auto-fetch issue details
- Mandatory serial number validation
- Fine calculation for delayed returns

Fine Payment
- Automatic fine calculation
- Mandatory fine confirmation if applicable
- Transaction completion validation

 Membership Management
- Add Membership (6 months / 1 year / 2 years)
- Extend or Cancel Membership

User Management
- New / Existing user options
- Mandatory name validation

---

Tech Stack

- Python
- Streamlit
- Pandas
- Datetime

---

How to Run

1. Install Streamlit:
