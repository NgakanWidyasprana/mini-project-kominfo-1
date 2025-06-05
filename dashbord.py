
import streamlit as st
import mysql.connector
import pandas as pd
import mysql.connector
from urllib.parse import quote
import random
import math

# --- DB Connection ---
def get_connection():
    return mysql.connector.connect(
        host="dh726.h.filess.io",
        database="Testing_oxygenlove",
        user="Testing_oxygenlove",
        password="7aa784e9040d7312bd35fcfe577ad9bdf7553593",
        port=61001
    )

def fetch_books():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    conn.close()
    return pd.DataFrame(rows, columns=cols)

def get_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    conn.close()
    return pd.DataFrame(rows, columns=cols)

@st.dialog("🏹 Add New Users")
def add_users():
    name = st.text_input("Fullname: ")
    user_id = st.text_input("User ID: ")
    if st.button("Submit"):
        if name and user_id:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (id, nama) VALUES (%s, %s)", (user_id, name))
            conn.commit()
            cursor.close()
            conn.close()
            st.toast(f"User {name} with ID {user_id} success added!", icon='🎉')
            st.rerun()
        else:
            st.warning("Please fill out all fields.")


# --- Streamlit App ---
st.title("📚 Library Borrow System")

# Add new books
for key, default in {
    "show_add_form": False,
    "form_submitted": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

if st.session_state.form_submitted:
    # Reset only control values
    st.session_state.show_add_form = False
    st.session_state.form_submitted = False

    # Clear the input widgets by resetting Streamlit keys
    st.session_state.new_book_id = ""
    st.session_state.new_book_title = ""
    st.session_state.new_book_author = ""
    st.session_state.new_book_status = "Available"
    st.rerun()

with st.expander("➕ Add New Book", expanded=st.session_state.show_add_form):

    if not st.session_state.show_add_form:
      st.session_state.show_add_form = True

    new_book_id = st.text_input("Book ID", key="book_id")
    new_book_title = st.text_input("Book Title", key="book_title")
    new_book_author = st.text_input("Book Author", key="book_author")
    book_status_options = ["Available", "Borrowed"]
    new_book_status = st.selectbox(
      "Book Status", 
      options=book_status_options,
      index=book_status_options.index(st.session_state.get("book_status", "Available")), 
      key="book_status"
    )

    if st.button("Add Book"):
        if new_book_id and new_book_title and new_book_author:
            status_value = 1 if new_book_status == "Available" else 0
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO books (id, judul, penulis, status) VALUES (%s, %s, %s, %s)",
                    (
                        new_book_id,
                        new_book_title,
                        new_book_author,
                        status_value,
                    )
                )
                conn.commit()
                st.success(f"✅ Book '{new_book_title}' added successfully!")

                # Clear form state after successful submission
                st.session_state.form_submitted = True
                st.rerun()  

            except mysql.connector.Error as e:
                st.error(f"❌ Error adding book: {e}")

            cursor.close()
            conn.close()
        else:
            st.warning("❌ Please fill in all fields.")

# View All Books
st.header("📋 Book List")
books_df = fetch_books()
books_df["status"] = books_df["status"].map({1: "Available", 0: "Borrowed"})

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# Add a search bar
search_query = st.text_input("🔍 Search by title or author")

# Filter the dataframe
if search_query:
    books_df = books_df[
        books_df["judul"].str.contains(search_query, case=False, na=False) |
        books_df["penulis"].str.contains(search_query, case=False, na=False)
    ]

for index, row in books_df.iterrows():
    cols = st.columns([1.5, 3, 3, 2, 3, 3])

    cols[0].write(row["id"])
    cols[1].write(row["judul"])
    cols[2].write(row["penulis"])
    cols[3].write(row["status"])

    if cols[4].button("🧺 Hapus", key=f"delete_{row['id']}"):
        conn = get_connection()
        cursor = conn.cursor()

        # Check if book is currently borrowed (status=0 or active transactions without return)
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE buku_id = %s", (row['id'],))
        active_borrow_count = cursor.fetchone()[0]

        if active_borrow_count > 0:
            st.warning(f"⚠️ Cannot delete '{row['judul']}' because it has borrowing history!")
        else:
            cursor.execute("DELETE FROM books WHERE id = %s", (row['id'],))
            conn.commit()
            st.success(f"✅ Book '{row['judul']}' deleted successfully!")
            st.rerun()

        cursor.close()
        conn.close()

    if cols[5].button("✏️ Edit", key=f"edit_{row['id']}"):
        # Check if book is currently borrowed
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE buku_id = %s AND tanggal_kembali IS NULL", (row['id'],))
        active_borrow_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        if active_borrow_count > 0:
            st.warning(f"⚠️ Cannot edit '{row['judul']}' because it is currently borrowed!")
        else:
            st.session_state.edit_id = row["id"]

        cursor.close()
        conn.close()

    if st.session_state.edit_id == row["id"]:
        st.subheader(f"✏️ Editing Book ID: {row['id']}")
        new_title = st.text_input("New Title", value=row["judul"], key=f"title_{row['id']}")
        new_author = st.text_input("New Author", value=row["penulis"], key=f"author_{row['id']}")

        if st.button("💾 Save Changes", key=f"save_{row['id']}"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE books SET judul = %s, penulis = %s WHERE id = %s", (new_title, new_author, row["id"]))
            conn.commit()
            cursor.close()
            conn.close()
            st.success(f"✅ Book '{new_title}' updated successfully!")
            st.session_state.edit_id = None
            st.rerun()

# Users Actions Example
st.header("🤼 Users Example")
users_df = get_users()
default_icon = "💂🏻‍♀️"
users_df["icon"] = default_icon
users_df["display"] = users_df["icon"] + " " + users_df["nama"]

# Init session state
if "selected_user_id" not in st.session_state:
    st.session_state.selected_user_id = None
if "selected_user_display" not in st.session_state:
    st.session_state.selected_user_display = ""
if "show_add_form_2" not in st.session_state:
    st.session_state.show_add_form_2 = False

# Layout users + add user button
num_columns = 3
total_buttons = len(users_df) + 1
num_rows = math.ceil(total_buttons / num_columns)

user_index = 0
for row_num in range(num_rows):
    cols = st.columns(num_columns)
    for col_num in range(num_columns):
        if user_index < len(users_df):
            row = users_df.iloc[user_index]
            with cols[col_num]:
                if st.button(row["display"], key=f"user_{row['id']}"):
                    st.session_state.selected_user_id = row.id
                    st.session_state.selected_user_display = row.display
            user_index += 1
        elif user_index == len(users_df):
            with cols[col_num]:
                if st.button("➕ Add User", key="show_add_user_btn"):
                    st.session_state.show_add_form = True
            user_index += 1

# Add Users Form
if st.session_state.show_add_form_2:
    add_users()
    st.session_state.show_add_form_2 = False

if st.session_state.selected_user_id:
    st.write(f"👤 Selected user: {st.session_state.selected_user_display}")
    user_id = int(st.session_state.selected_user_id)

    conn = get_connection()
    cursor = conn.cursor()

    tab1, tab2 = st.tabs(["📤 Return Book", "📥 Borrow Book"])

    with tab1:
        cursor.execute("""
            SELECT b.id, b.judul FROM books b
            JOIN transactions t ON b.id = t.buku_id
            WHERE t.user_id = %s AND t.tanggal_kembali IS NULL
        """, (user_id,))
        borrowed_books = cursor.fetchall()

        if borrowed_books:
            selected_return = st.selectbox("Select a book to return:", borrowed_books, format_func=lambda x: x[1])

            if st.button("🔄 Confirm Return", key="confirm_return", disabled=selected_return is None):
                cursor.execute("""
                    UPDATE transactions
                    SET tanggal_kembali = NOW()
                    WHERE buku_id = %s AND user_id = %s AND tanggal_kembali IS NULL
                """, (selected_return[0], user_id))
                cursor.execute("UPDATE books SET status = 1 WHERE id = %s", (selected_return[0],))
                conn.commit()
                st.success(f"✅ Book '{selected_return[1]}' returned successfully!")
                st.session_state.selected_user_id = None
                st.rerun()
        else:
            st.info("📚 No borrowed books to return.")

    with tab2:
        cursor.execute("SELECT id, judul FROM books WHERE status = 1")
        available_books = cursor.fetchall()

        if available_books:
            selected_borrow = st.selectbox("Select a book to borrow:", available_books, format_func=lambda x: x[1])

            if st.button("📩 Confirm Borrow", key="confirm_borrow", disabled=selected_borrow is None):
                cursor.execute("""
                    INSERT INTO transactions (buku_id, user_id, tanggal_pinjam)
                    VALUES (%s, %s, NOW())
                """, (selected_borrow[0], user_id))
                cursor.execute("UPDATE books SET status = 0 WHERE id = %s", (selected_borrow[0],))
                conn.commit()
                st.success(f"✅ Book '{selected_borrow[1]}' borrowed successfully!")
                st.session_state.selected_user_id = None
                st.rerun()
        else:
            st.warning("❌ No books available for borrowing.")

    cursor.close()
    conn.close()
