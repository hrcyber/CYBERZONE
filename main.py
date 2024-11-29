import streamlit as st
import sqlite3
import pandas as pd

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('school_diary.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS qa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT,
                question TEXT,
                answer TEXT
                )''')
    conn.commit()
    conn.close()

# Save or update a question-answer pair
def save_qa(class_name, question, answer):
    conn = sqlite3.connect('school_diary.db')
    c = conn.cursor()
    c.execute('''INSERT INTO qa (class_name, question, answer) VALUES (?, ?, ?)''',
              (class_name, question, answer))
    conn.commit()
    conn.close()

# Fetch all question-answer pairs for a specific class
def fetch_qa(class_name):
    conn = sqlite3.connect('school_diary.db')
    c = conn.cursor()
    c.execute('SELECT * FROM qa WHERE class_name = ?', (class_name,))
    data = c.fetchall()
    conn.close()
    return data

# Update a question-answer pair
def update_qa(id, question, answer):
    conn = sqlite3.connect('school_diary.db')
    c = conn.cursor()
    c.execute('''UPDATE qa SET question = ?, answer = ? WHERE id = ?''', (question, answer, id))
    conn.commit()
    conn.close()

# Delete a question-answer pair
def delete_qa(id):
    conn = sqlite3.connect('school_diary.db')
    c = conn.cursor()
    c.execute('DELETE FROM qa WHERE id = ?', (id,))
    conn.commit()
    conn.close()

# Convert data to CSV
def convert_to_csv(data):
    df = pd.DataFrame(data, columns=["ID", "Class", "Question", "Answer"])
    return df.to_csv(index=False)

# Main function
def main():
    # Initialize the database
    init_db()

    # Main page header
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="main-header">School Diary:</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    class_selected = st.sidebar.selectbox("Select Class", [f"Class {i}" for i in range(1, 11)])
    action = st.sidebar.radio(
        "Choose an Action",
        ["Add Q&A", "View Q&A", "Update Q&A", "Delete Q&A", "Download Q&A"]
    )

    class_name = class_selected

    # Add Question & Answer
    if action == "Add Q&A":
        st.subheader(f"Add Question & Answer for {class_name}")
        question = st.text_input("Enter Question")
        answer = st.text_area("Enter Answer")
        if st.button("Save"):
            if question and answer:
                save_qa(class_name, question, answer)
                st.success("Q&A added successfully!")
            else:
                st.error("Please provide both question and answer.")

    # View Questions & Answers
    elif action == "View Q&A":
        st.subheader(f"View Questions & Answers for {class_name}")
        data = fetch_qa(class_name)
        if data:
            for record in data:
                st.write(f"**Q:** {record[2]}")
                st.write(f"**A:** {record[3]}")
                st.markdown("---")
        else:
            st.info(f"No Q&A available for {class_name}.")

    # Update Question & Answer
    elif action == "Update Q&A":
        st.subheader(f"Update Question & Answer for {class_name}")
        data = fetch_qa(class_name)
        if data:
            qa_ids = [record[0] for record in data]
            selected_id = st.selectbox("Select Q&A to Update", qa_ids)
            selected_qa = next((record for record in data if record[0] == selected_id), None)
            if selected_qa:
                question = st.text_input("Edit Question", value=selected_qa[2])
                answer = st.text_area("Edit Answer", value=selected_qa[3])
                if st.button("Update"):
                    update_qa(selected_id, question, answer)
                    st.success("Q&A updated successfully!")
        else:
            st.info(f"No Q&A available for {class_name}.")

    # Delete Question & Answer
    elif action == "Delete Q&A":
        st.subheader(f"Delete Question & Answer for {class_name}")
        data = fetch_qa(class_name)
        if data:
            qa_ids = [record[0] for record in data]
            selected_id = st.selectbox("Select Q&A to Delete", qa_ids)
            if st.button("Delete"):
                delete_qa(selected_id)
                st.success("Q&A deleted successfully!")
        else:
            st.info(f"No Q&A available for {class_name}.")

    # Download Questions & Answers
    elif action == "Download Q&A":
        st.subheader(f"Download Questions & Answers for {class_name}")
        data = fetch_qa(class_name)
        if data:
            csv = convert_to_csv(data)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f"{class_name.lower().replace(' ', '_')}_qa.csv",
                mime="text/csv"
            )
        else:
            st.info(f"No Q&A available for {class_name}.")

if __name__ == "__main__":
    main()
