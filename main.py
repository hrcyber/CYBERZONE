import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
st.balloons()




# Database Setup
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS notebook (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        date TEXT,
                        note TEXT)''')
    conn.commit()
    conn.close()


# Function to add a new user (Sign-up)
def add_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()


# Function to verify user credentials (Login)
def verify_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user


# Function to add a new note
def add_note(username, date, note):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO notebook (username, date, note) VALUES (?, ?, ?)', (username, date, note))
    conn.commit()
    conn.close()


# Function to update a note
def update_note(note_id, note):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE notebook SET note=? WHERE id=?', (note, note_id))
    conn.commit()
    conn.close()


# Function to delete a note
def delete_note(note_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notebook WHERE id=?', (note_id,))
    conn.commit()
    conn.close()


# Function to get all notes for a user
def get_notes(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notebook WHERE username=? ORDER BY date DESC', (username,))
    notes = cursor.fetchall()
    conn.close()
    return notes


# Login page
def login_page():
    st.title("Login")
    st.write("Please enter your credentials to log in.")
    img = Image.open("cc.jpg")
    st.image(
        img,
        caption="Naseem Khan (Software developer)",
        width= 400,

        channels= "RGB"
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        user = verify_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful!")
            dashboard_page(username)
        else:
            st.error("Invalid username or password!")


# Sign up page
def signup_page():
    st.title("Sign Up Page")
    st.write("Create a new account.")

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    confirm_password = st.text_input("Confirm Password", type='password')

    if password != confirm_password:
        st.warning("Passwords do not match!")

    if st.button("Sign Up"):
        if username and password and confirm_password:
            try:
                add_user(username, password)
                st.success("Account created successfully! You can now log in.")
            except:
                st.error("Username already exists. Please try a different one.")
        else:
            st.warning("Please fill in all the fields!")


# Dashboard page
def dashboard_page(username):
    st.title("Daily Notebook Dashboard")

    # Option to add a new note
    st.subheader("Add New Note")
    date = st.date_input("Select Date")
    note = st.text_area("Write your note here:")

    if st.button("Save Note"):
        if note:
            add_note(username, str(date), note)
            st.success(f"Note for {date} has been saved!")
        else:
            st.warning("Please write something to save.")

    # View existing notes
    st.subheader("Your Notes")
    notes = get_notes(username)
    if notes:
        df = pd.DataFrame(notes, columns=["ID", "Username", "Date", "Note"])
        df = df.drop("Username", axis=1)  # Remove the 'Username' column for display
        st.dataframe(df)

        # Option to update or delete a note
        note_id = st.number_input("Enter Note ID to Update/Delete", min_value=1, max_value=10000, step=1)

        if note_id:
            action = st.radio("Select Action", ["Update", "Delete"])

            if action == "Update":
                updated_note = st.text_area("Update Note", value="")
                if st.button("Update Note"):
                    update_note(note_id, updated_note)
                    st.success("Note updated successfully!")

            if action == "Delete":
                if st.button("Delete Note"):
                    delete_note(note_id)
                    st.success("Note deleted successfully!")


# Streamlit Sidebar navigation
def main():
    st.sidebar.title("Navigation")
    if "logged_in" in st.session_state and st.session_state.logged_in:
        menu = ["Dashboard"]
    else:
        menu = ["Login", "Sign Up"]

    choice = st.sidebar.selectbox("Select Page", menu)

    if choice == "Login":
        login_page()
    elif choice == "Sign Up":
        signup_page()
    elif choice == "Dashboard":
        if "username" in st.session_state:
            dashboard_page(st.session_state.username)
        else:
            st.warning("Please log in first.")


# Initialize database and run the app
init_db()
main()
