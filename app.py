from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = "sua_chave_secreta_aqui"  # Insira uma chave secreta forte


# Inicializa o banco de dados
def init_db():
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    # Tabela de livros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL
        )
    """)

    # Tabela de anotações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            book_id INTEGER,
            FOREIGN KEY (book_id) REFERENCES books (id)
        )
    """)
    conn.commit()
    conn.close()


# Busca no site worldhistory.org
def search_worldhistory(query):
    url = f"https://www.www.google.com/search/?q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('div', class_='search-result')
    return [{"title": r.find('h3').text, "link": "https://www.google.com" + r.find('a')['href']} for r in results]


# Página inicial: lista de livros
@app.route("/")
def index():
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM books")
    books = cursor.fetchall()
    conn.close()
    return render_template("index.html", books=books)


# Adicionar livro
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["book_name"]
        conn = sqlite3.connect("notes.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO books (title) VALUES (?)", (title,))
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("add_book.html")


# Gerenciar anotações de um livro
@app.route("/book/<int:book_id>")
def book(book_id):
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()

    cursor.execute("SELECT id, content FROM notes WHERE book_id = ?", (book_id,))
    notes = cursor.fetchall()
    conn.close()
    return render_template("book.html", book=book, notes=notes)


# Adicionar nota a um livro
@app.route("/book/<int:book_id>/add_note", methods=["GET", "POST"])
def add_note_to_book(book_id):
    if request.method == "POST":
        content = request.form["content"]
        conn = sqlite3.connect("notes.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (content, book_id) VALUES (?, ?)", (content, book_id))
        conn.commit()
        conn.close()
        return redirect(url_for("book", book_id=book_id))
    return render_template("add_note.html", book_id=book_id)


# Editar nota
@app.route("/note/<int:note_id>/edit", methods=["GET", "POST"])
def edit_note(note_id):
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    if request.method == "POST":
        new_content = request.form["content"]
        # Atualiza a nota no banco de dados
        cursor.execute("UPDATE notes SET content = ? WHERE id = ?", (new_content, note_id))
        conn.commit()

        # Obtém o book_id da nota para redirecionar corretamente
        cursor.execute("SELECT book_id FROM notes WHERE id = ?", (note_id,))
        book_id = cursor.fetchone()[0]
        conn.close()

        return redirect(url_for("book", book_id=book_id))

    # Carrega a nota para edição
    cursor.execute("SELECT id, content FROM notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()
    conn.close()
    return render_template("edit_note.html", note=note)



# Excluir livro
@app.route("/book/<int:book_id>/delete")
def delete_book(book_id):
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    cursor.execute("DELETE FROM notes WHERE book_id = ?", (book_id,))
    conn.commit()
    conn.close()
    return redirect("/")


# Excluir nota
@app.route("/note/<int:note_id>/delete")
def delete_note(note_id):
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    return redirect("/")


# Redirecionar busca no worldhistory.org
@app.route("/note/<int:note_id>/search")
def search_note_on_worldhistory(note_id):
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()
    conn.close()

    if note:
        query = note[0]
        search_url = f"https://www.google.com/search/?q={query}"
        return redirect(search_url)
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
