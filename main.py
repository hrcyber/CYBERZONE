import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image

# Initialize the SQLite database
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


# Add a new user (Sign-up)
def add_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()


# Verify user credentials (Login)
def verify_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user


# Add a new note to the notebook
def add_note_to_db(username, date, note):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO notebook (username, date, note) VALUES (?, ?, ?)', (username, date, note))
    conn.commit()
    conn.close()


# Update an existing note
def update_note_in_db(note_id, note):

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE notebook SET note=? WHERE id=?', (note, note_id))
    conn.commit()
    conn.close()



# Delete a note from the notebook
def delete_note_from_db(note_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notebook WHERE id=?', (note_id,))
    conn.commit()
    conn.close()


# Get all notes for a specific user
def get_notes(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notebook WHERE username=? ORDER BY date DESC', (username,))
    notes = cursor.fetchall()
    conn.close()
    return notes


# Streamlit login page
def login():
    st.title("Wellcome to C.Zone")
    img = Image.open("cc.jpg")
    st.image(
        img,
        caption="Naseem Khan (Software developer)",
        width=300,

        channels="RGB"
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify_user(username, password):
            st.session_state.username = username
            st.session_state.logged_in = True
            st.success("Login Successful!")
            show_notebook()  # Redirect to Notebook
        else:
            st.error("Invalid Username or Password")


# Streamlit sign-up page
def sign_up():
    st.title("Sign-Up Screen")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if password == confirm_password:
            try:
                add_user(username, password)
                st.success("Account created successfully! Please log in.")
            except:
                st.error("Username already exists.")
        else:
            st.error("Passwords do not match.")


# Streamlit daily notebook (CRUD)
def show_notebook():
    if not st.session_state.get('logged_in', False):
        st.error("You must be logged in to view the notebook.")
        return

    st.title(f"Welcome, {st.session_state.username}!")

    action = st.selectbox("Choose an action", ["Add Note", "View Notes", "Update Note", "Delete Note"])

    if action == "Add Note":
        add_note()
    elif action == "View Notes":
        view_notes()
    elif action == "Update Note":
        update_note()
    elif action == "Delete Note":
        delete_note()

    if st.button("Back to Dashboard"):
        st.session_state.logged_in = False
        login()


def add_note():
    date = st.date_input("Date")
    note = st.text_area("Note")

    if st.button("Save Note"):
        if note:
            add_note_to_db(st.session_state.username, date.strftime("%Y-%m-%d"), note)
            st.success("Note added successfully!")
        else:
            st.error("Please enter a note.")


def view_notes():
    notes = get_notes(st.session_state.username)
    if notes:
        st.subheader("Your Notes:")
        for note in notes:
            st.write(f"**Date**: {note[2]}")
            st.write(f"**Note**: {note[3]}")
            st.write("---")
    else:
        st.warning("You have no notes to display.")


def update_note():
    notes = get_notes(st.session_state.username)
    note_ids = [note[0] for note in notes]

    if notes:
        note_id = st.selectbox("Select a note to update", note_ids)
        new_note = st.text_area("Updated Note")

        if st.button("Update Note"):
            if new_note:
                update_note_in_db(note_id, new_note)
                st.success("Note updated successfully!")
            else:
                st.error("Please enter a new note.")
    else:
        st.warning("You have no notes to update.")


def delete_note():
    notes = get_notes(st.session_state.username)
    note_ids = [note[0] for note in notes]

    if notes:
        note_id = st.selectbox("Select a note to delete", note_ids)

        if st.button("Delete Note"):
            delete_note_from_db(note_id)
            st.success("Note deleted successfully!")
    else:
        st.warning("You have no notes to delete.")


# Main function to run the app
def main():
    init_db()  # Initialize the database

    # Set the login session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        show_notebook()
    else:
        action = st.sidebar.radio("Select Page", ["Login", "Sign Up"])

        if action == "Login":
            login()
        elif action == "Sign Up":
            sign_up()


if __name__ == "__main__":
    main()
