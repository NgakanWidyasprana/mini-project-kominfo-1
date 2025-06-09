
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

def handle_restore_choice():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        data = st.session_state.temp_book_data
        choice = st.session_state.restore_or_update_choice

        if choice == "Use old data":
            cursor.execute("UPDATE books SET is_delete = 0 WHERE id = %s", (data["id"],))
            conn.commit()
            st.toast(f"✅ Book '{data['title']}' restored successfully!")

        elif choice == "Use new data":
            cursor.execute("""
                UPDATE books 
                SET judul = %s, penulis = %s, status = %s, is_delete = 0 
                WHERE id = %s
            """, (data["title"], data["author"], data["status"], data["id"]))
            conn.commit()
            st.toast(f"✅ Book '{data['title']}' updated and restored successfully!")

        # Reset states
        st.session_state.awaiting_restore_choice = False
        st.session_state.restore_choice_submitted = False
        st.session_state.form_submitted = True
        st.rerun()

    except mysql.connector.Error as e:
        st.error(f"❌ Error restoring book: {e}")
    finally:
        cursor.close()
        conn.close()

# -------------------- Streamlit App --------------------
#
# Simple Library Management App - Kominfo Mini Project
# Features:
# - Borrow and return books
# - Add, edit, and delete books
# - Update book information (title, author, etc.)
# - Add and manage users
# - Track borrowing activity in DB
#
# -------------------------------------------------------

st.title("📚 Library Borrow System")

# ------------------------------
#  1. ADD BOOK SECTION
# 
#  --> Add new Book
#  --> Restore/Update Old Book
# ------------------------------

# -- Step 1: Initialize the default state of add book function --
default_states = {
    "show_add_form": False,
    "form_submitted": False,
    "book_id": "",
    "book_title": "",
    "book_author": "",
    "book_status": "Available",
    "restore_or_update_choice": None,
    "restore_choice_submitted": False,
    "temp_book_data": {},
    "awaiting_restore_choice": False,
}

for key, default in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = default

# -- Step 2: Initialize reset state after successful submission to clear input or cancel restore--
if st.session_state.form_submitted:
    for key in ["show_add_form", "form_submitted"]: st.session_state[key] = False
    st.session_state.book_id = ""
    st.session_state.book_title = ""
    st.session_state.book_author = ""
    st.session_state.book_status = "Available"
    st.rerun()

if st.session_state.get("_cancel_restore"):
    st.session_state.awaiting_restore_choice = False
    st.session_state.temp_book_data = {}
    st.session_state.restore_choice_submitted = False
    st.session_state.restore_or_update_choice = None  # SAFE: runs before widget renders
    st.session_state._cancel_restore = False
    st.rerun()

# -- Step 3: Pop-up book form to write new book data --
with st.expander("➕ Add New Book", expanded=st.session_state.show_add_form):
    if not st.session_state.show_add_form:
        st.session_state.show_add_form = True

    # Input field
    new_book_id = st.text_input("Book ID", key="book_id")
    new_book_title = st.text_input("Book Title", key="book_title")
    new_book_author = st.text_input("Book Author", key="book_author")

    book_status_options = ["Available", "Borrowed"]
    new_book_status = st.selectbox(
        "Book Status",
        options=book_status_options,
        index=book_status_options.index(st.session_state.book_status),
        key="book_status"
    )

    # Button logic
    if st.button("Add Book"):
        if new_book_id and new_book_title and new_book_author:

            ## Change input status and define connection database 
            status_value = 1 if new_book_status == "Available" else 0
            conn = get_connection()
            cursor = conn.cursor()

            try:
                ## Check for existing ID is soft-delete or not
                cursor.execute("SELECT is_delete FROM books WHERE id = %s", (new_book_id,))
                existing = cursor.fetchone()

                if existing: # --> Soft Delete
                    if existing[0] == 1:
                        st.session_state.temp_book_data = {
                            "id": new_book_id,
                            "title": new_book_title,
                            "author": new_book_author,
                            "status": status_value,
                        }
                        st.session_state.awaiting_restore_choice = True
                        st.rerun()
                    else: 
                        st.warning("⚠️ A book with this ID already exists and is active. Please use a different ID.")

                else: # --> Fresh Book
                    cursor.execute("""
                        INSERT INTO books (id, judul, penulis, status)
                        VALUES (%s, %s, %s, %s)
                    """, (new_book_id, new_book_title, new_book_author, status_value))
                    conn.commit()
                    st.success(f"✅ Book {new_book_title} added successfully!")
                    st.session_state.form_submitted = True
                    st.rerun()

            except mysql.connector.Error as e:
                st.error(f"❌ Error adding book: {e}")

            finally:
                cursor.close()
                conn.close()
        else:
            st.warning("❌ Please fill in all fields.")

    # -- Step 3-1: If soft delete, do restore options --
    if st.session_state.awaiting_restore_choice:
        st.warning("⚠️ This book ID exists but was deleted. Choose an action below:")
        st.radio("What do you want to do with this book ID?",
                 ["Use old data", "Use new data"],
                 key="restore_or_update_choice")

        col1, col2 = st.columns([1, 1])
        with col1: # --> Do soft delete
            if st.button("Submit Choice"):
                if st.session_state.restore_or_update_choice:
                    st.session_state.restore_choice_submitted = True
                    st.rerun()

        with col2:
            if st.button("Cancel"): # --> Cancel soft reset
                st.session_state._cancel_restore = True
                st.rerun()

# -- Step 4: Process the restore choice if submitted --
if st.session_state.restore_choice_submitted:
    handle_restore_choice()

# ------------------------------
#  2. VIEW BOOK SECTION
#  
#  --> Edit new Book
#  --> Remove new Book
#  --> Restore Book
#  --> View Book Status
# ------------------------------

st.header("📋 Book List")
books_df = fetch_books()
books_df = books_df[books_df["is_delete"] == 0]
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

        # Check if the book is currently borrowed
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE buku_id = %s AND tanggal_kembali IS NULL", (row['id'],))
        active_borrow_count = cursor.fetchone()[0]

        if active_borrow_count > 0:
            st.warning(f"⚠️ Cannot delete '{row['judul']}' because it is currently borrowed!")
        else:
            # Soft delete: mark as deleted
            cursor.execute("UPDATE books SET is_delete = 1 WHERE id = %s", (row['id'],))
            conn.commit()
            st.success(f"✅ Book {row['judul']} marked as deleted successfully!")
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
            st.warning(f"⚠️ Cannot edit {row['judul']} because it is currently borrowed!")
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


# ------------------------------
#  3. USERS ACTION SECTION
#  
#  --> Add new users
#  --> Borrowing books
#  --> Returning books
#  --> Cart systems
#  --> Multiple select books
# ------------------------------

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
                    st.session_state.show_add_form_2 = True
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

    cart_key = f"cart_user_{user_id}"
    if cart_key not in st.session_state: st.session_state[cart_key] = []

    tab1, tab2 = st.tabs(["📤 Return Book", "📥 Borrow Book"])

    with tab1:
        cursor.execute("""SELECT b.id, b.judul FROM books b JOIN transactions t ON b.id = t.buku_id WHERE t.user_id = %s AND t.tanggal_kembali IS NULL""", (user_id,))
        borrowed_books = cursor.fetchall()

        if borrowed_books:
            selected_return = st.multiselect("Select a book to return:", borrowed_books, format_func=lambda x: x[1])
            
            if st.button("🔄 Confirm Return", key="confirm_return", disabled=len(selected_return) == 0):
                for book in selected_return:
                    cursor.execute("""UPDATE transactions SET tanggal_kembali = NOW() WHERE buku_id = %s AND user_id = %s AND tanggal_kembali IS NULL""", (book[0], user_id))
                    cursor.execute("UPDATE books SET status = 1 WHERE id = %s", (book[0],))

                conn.commit()
                st.toast(f"✅ {len(selected_return)} book(s) returned successfully!")
                st.session_state.selected_user_id = None
                st.rerun()
        else:
            st.info("📚 No borrowed books to return.")
        
    with tab2:

        user_cart = st.session_state[cart_key]

        valid_cart= []
        removed_books = []

        for book in user_cart:
            book_id, title = book
            cursor.execute("SELECT status FROM books WHERE id = %s AND is_delete = 0", (book_id,))
            result = cursor.fetchone()
            if result and result[0] == 1:
                valid_cart.append(book)
            else:
                removed_books.append(title)

        st.session_state[cart_key] = valid_cart
        user_cart = valid_cart

        for title in removed_books:
            st.warning(f"❌ Book '{title}' is not longer available and was removed from your cart.")

        cursor.execute("SELECT id, judul FROM books WHERE status = 1 AND is_delete = 0")
        available_books = cursor.fetchall()

        cart_ids = [b[0] for b in user_cart]
        display_books = [book for book in available_books if book[0] not in cart_ids]

        st.subheader("📚 Available Books")
        if display_books:
            for book in display_books:
              book_id, title = book

              # Show book title with Add to Cart button if not already added
              cols = st.columns([6, 1])
              with cols[0]:
                  st.markdown(f"**{title}**")
              with cols[1]:
                  if st.button("🛒", key=f"add_{user_id}_{book_id}"):
                      user_cart.append(book)
                      st.session_state[cart_key] = user_cart
                      st.rerun()
        else:
            st.warning("❌ No books available for borrowing.")

        st.divider()

        st.subheader("🛒 Cart")
        if user_cart:
            for book in user_cart:
                book_id, title = book
                cols = st.columns([6, 1])
                with cols[0]:
                  st.markdown(f"**{title}**")
                with cols[1]:
                  if st.button("❌", key=f"remove_{user_id}_{book_id}"):
                      st.session_state[cart_key] = [b for b in user_cart if b[0] != book_id]
                      st.rerun()
      
            if st.button("✅ Confirm Borrow", key=f"confirm_borrow_all_{user_id}"):
                with st.spinner("⏳ Processing your borrow..."):
                    for book in user_cart:
                        cursor.execute("""INSERT INTO transactions (buku_id, user_id, tanggal_pinjam) VALUES (%s, %s, NOW())""", (book[0], user_id))
                        cursor.execute("UPDATE books SET status = 0 WHERE id = %s", (book[0],))

                    conn.commit()

                borrow_titles = ", ".join([b[1] for b in user_cart])
                st.toast(f"✅ Books borrowed successfully: {borrow_titles}")
                st.session_state[cart_key].clear()
                st.session_state.selected_user_id = None
                st.rerun()
        else:
          st.info("🛒 Your cart is empty.")           

    cursor.close()
    conn.close()
