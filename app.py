import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB = 'database.db'


# ---------- Database Helpers ----------
def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER
        )
    ''')

    # Insert sample users only if the table is empty
    count = conn.execute(
        'SELECT COUNT(*) FROM users'
    ).fetchone()[0]

    if count == 0:
        conn.executemany(
            'INSERT INTO users (name, email, age) VALUES (?, ?, ?)',
            [
                ('Ravi', 'ravi@example.com', 25),
                ('Priya', 'priya@example.com', 30),
                ('Arjun', 'arjun@example.com', 22)
            ]
        )

    conn.commit()
    conn.close()


init_db()


# ---------- 1. Simple Interest Calculator ----------
@app.route('/', methods=['GET', 'POST'])
def users():
    result = None
    r = None
    t = None
    total = None
    p = None

    if request.method == 'POST':
        try:
            p = float(request.form['p'])
            t = float(request.form['t'])
            r = float(request.form['r'])

            if p < 0 or r < 0 or t < 0:
                return render_template(
                    'index.html',
                    result=None,
                    r=None,
                    t=None,
                    total=None,
                    p=None,
                    error='Values cannot be negative.'
                )

            result = (p * t * r) / 100
            total = p + result

        except (ValueError, KeyError):
            return render_template(
                'index.html',
                result=None,
                r=None,
                t=None,
                total=None,
                p=None,
                error='Please enter valid numbers.'
            )

    return render_template(
        'index.html',
        result=result,
        r=r,
        t=t,
        total=total,
        p=p,
        error=None
    )


# ---------- 2. Show Add-User Form ----------
@app.route('/add', methods=['GET'])
def add_form():
    return render_template('add_user.html')


# ---------- 3. Add User to Database ----------
@app.route('/add', methods=['POST'])
def add_user():
    name = request.form['name'].strip()
    email = request.form['email'].strip()
    age = request.form.get('age', '').strip()

    if not name or not email:
        return 'Name and email are required.', 400

    try:
        age_value = int(age) if age else None

        if age_value is not None and age_value < 0:
            return 'Age cannot be negative.', 400

    except ValueError:
        return 'Please enter a valid age.', 400

    conn = get_conn()

    try:
        conn.execute(
            'INSERT INTO users (name, email, age) VALUES (?, ?, ?)',
            (name, email, age_value)
        )
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for('users'))


# ---------- 4. Run Flask Application ----------
if __name__ == '__main__':
    app.run(debug=True)