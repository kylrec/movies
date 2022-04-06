import uuid, os
from flask import Flask, request, render_template, redirect, url_for
app = Flask(__name__)

# Register the setup page and import create_connection()
from utils import create_connection, setup
app.register_blueprint(setup)


@app.route('/')
def home():
    return render_template("index.html")


# TODO: Add a '/register' (add_user) route that uses INSERT
@app.route('/register', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':

        if request.files['avatar'].filename:
            avatar_image = request.files["avatar"]
            ext = os.path.splitext(avatar_image.filename)[1]
            avatar_filename = str(uuid.uuid4())[:8] + ext
            avatar_image.save("static/images/" + avatar_filename)
        else:
            avatar_filename = None

        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = """INSERT INTO users
                    (first_name, last_name, email, password, avatar)
                    VALUES (%s, %s, %s, %s, %s)
                """
                values = (
                    request.form['first_name'],
                    request.form['last_name'],
                    request.form['email'],
                    request.form['password'],
                    avatar_filename
                )
                cursor.execute(sql, values)
                connection.commit()
        return redirect('/')
    return render_template('users_add.html')

# TODO: Add a '/dashboard' (list_users) route that uses SELECT
@app.route('/dashboard')
def list_users():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchall()
    return render_template('users_list.html', result=result)

# TODO: Add a '/profile' (view_user) route that uses SELECT
@app.route('/view')
def view_user():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", request.args['id'])
            result = cursor.fetchone()
    return render_template('users_view.html', result=result)

# TODO: Add a '/delete_user' route that uses DELETE
@app.route('/delete')
def delete_user():
    with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = """DELETE FROM users WHERE id = %s"""
                values = (request.args['id'])
                cursor.execute(sql, values)
                connection.commit()
    return redirect ('/dashboard')
# TODO: Add an '/edit_user' route that uses UPDATE
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':

        avatar_image = request.files["avatar"]
        ext = os.path.splitext(avatar_image.filename)[1]
        avatar_filename = str(uuid.uuid4())[:8] + ext
        avatar_image.save("static/images/" + avatar_filename)

        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = """UPDATE users SET
                first_name = %s,
                last_name = %s,
                email = %s,
                password = %s,
                avatar = %s
            WHERE id = %s"""
                values = (
                    request.form['first_name'], 
                    request.form['last_name'], 
                    request.form['email'],
                    request.form['password'],
                    avatar_filename,
                    request.form['id']
                )
                cursor.execute(sql, values)
                connection.commit()

        return redirect(url_for('home'))
    else:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE id = %s"
                values = (request.args['id'])
                cursor.execute(sql, values)
                result = cursor.fetchone()
        return render_template("users_edit.html", result=result)



if __name__ == '__main__':
    import os

    # This is required to allow flashing messages. We will cover this later.
    app.secret_key = os.urandom(32)

    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, debug=True)
