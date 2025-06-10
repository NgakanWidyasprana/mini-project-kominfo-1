
# 📚 Book Management System – Mini Project Kominfo

[![Streamlit](https://img.shields.io/badge/Streamlit-0E1117?style=for-the-badge&logo=streamlit&logoColor=FF4B4B)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Google Colab](https://img.shields.io/badge/Colab-Notebooks-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white)](https://colab.research.google.com/)
[![ngrok](https://img.shields.io/badge/ngrok-Secure%20Tunnels-1F1F1F?style=for-the-badge&logo=ngrok&logoColor=white)](https://ngrok.com)
[![filess.io](https://img.shields.io/badge/filess.io-MySQL%20Hosting-16A085?style=for-the-badge)](https://filess.io)

This is a simple web application built with **Streamlit** that allows users to manage a collection of books. It includes full **CRUD** functionality and a **borrowing system** to track book lending activity.

---

## ✨ Features

### 📘 Book Management (CRUD)
- Add new books to the collection  
- View a list of all books  
- Update book details  
- Soft delete (mark as deleted) books  

### 🔄 Borrowing System
- Borrow available books  
- Return borrowed books  
- Track the status of each book (borrowed/available)

---

## 🛠️ Technology Stack

- **Python**
- **Streamlit** (for the user interface)
- **MySQL** (remote database via [filess.io](https://filess.io))
- **mysql-connector-python** (for database communication)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/mini-project-kominfo.git
cd mini-project-kominfo
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Add Your Database Secrets

Create a file called `secrets.toml` inside the `.streamlit/` folder with your database credentials:

```toml
[database]
host = "your-filess-host"
name = "your-database-name"
port = your-port
user = "your-username"
password = "your-password"
```

> ⚠️ **Note:** Do not upload this file to GitHub. Add `.streamlit/secrets.toml` to your `.gitignore`.

If you're using this in **Google Colab**, you can use an uploader script to insert `secrets.toml` securely.

---

### 4. Run the App Locally

```bash
streamlit run dashboard.py
```

---

## 🌐 Live Demo

🖥️ You can try the deployed version here: 🔥 [Mini Project Kominfo – Live App](https://mini-project-kominfo-1-xouthdkhsbxf2dtyxhtsi4.streamlit.app/)

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 🙋‍♀️ Need Access to the Database?

This project connects to a remote MySQL database hosted on filess.io.
To set up your own database for development or testing:

1. Create a free account at filess.io

2. Create a new MySQL database from the dashboard

3. Upload the provided schema.sql file (located in the database/ folder of this project) to initialize the database structure

4. Use the generated credentials (host, port, username, password, database name) to configure your .streamlit/secrets.toml file

```
🔐 This allows you to work with your own remote MySQL instance without needing local setup.s