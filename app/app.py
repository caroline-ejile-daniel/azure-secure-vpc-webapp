from flask import Flask, request, render_template_string
import psycopg2
import os

app = Flask(__name__)

# Database connection
def get_db():
    return psycopg2.connect(
        host="10.0.2.4",        # private IP of your DB VM
        database="registrationdb",
        user="appuser",
        password="StrongPassword123"
    )

# Create table if it doesn't exist
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Registration Form</title>
    <style>
        body { font-family: Arial; max-width: 500px; 
               margin: 50px auto; padding: 20px; }
        input { width: 100%; padding: 10px; 
                margin: 10px 0; box-sizing: border-box; }
        button { width: 100%; padding: 10px; 
                 background: #007bff; color: white; 
                 border: none; cursor: pointer; }
        .success { color: green; }
        .error { color: red; }
    </style>
</head>
<body>
    <h2>User Registration</h2>
    {% if message %}
        <p class="{{ message_class }}">{{ message }}</p>
    {% endif %}
    <form method="POST" action="/register">
        <input type="text" name="name" 
               placeholder="Full Name" required>
        <input type="email" name="email" 
               placeholder="Email Address" required>
        <button type="submit">Register</button>
    </form>
    {% if users %}
        <h3>Registered Users</h3>
        {% for user in users %}
            <p>{{ user[0] }} - {{ user[1] }}</p>
        {% endfor %}
    {% endif %}
</body>
</html>
'''

@app.route('/')
def home():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT name, email FROM users ORDER BY created_at DESC')
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template_string(HTML_TEMPLATE, users=users)

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO users (name, email) VALUES (%s, %s)',
            (name, email)
        )
        conn.commit()
        cur.close()
        conn.close()

        # Fetch updated list
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'SELECT name, email FROM users ORDER BY created_at DESC'
        )
        users = cur.fetchall()
        cur.close()
        conn.close()

        return render_template_string(
            HTML_TEMPLATE,
            message="Registration successful!",
            message_class="success",
            users=users
        )
    except Exception as e:
        return render_template_string(
            HTML_TEMPLATE,
            message=f"Error: {str(e)}",
            message_class="error"
        )

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
