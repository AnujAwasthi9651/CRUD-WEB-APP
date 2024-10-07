from flask import Flask, render_template, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from email_validator import validate_email, EmailNotValidError
import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            phone_number TEXT PRIMARY KEY NOT NULL UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email_id TEXT NOT NULL UNIQUE,
            address TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

class UserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    email_id = StringField('Email ID', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Submit')

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('index.html', users=users)

@app.route('/add', methods=('GET', 'POST'))
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        email = form.email_id.data
        try:
            valid = validate_email(email)
            email = valid.email
            
            conn = get_db_connection()
            conn.execute('INSERT INTO users (first_name, last_name, phone_number, email_id, address) VALUES (?, ?, ?, ?, ?)',
                         (form.first_name.data, form.last_name.data, form.phone_number.data, email, form.address.data))
            conn.commit()
            conn.close()
            flash('User added successfully!', 'success')
            return redirect(url_for('index'))
        except EmailNotValidError as e:
            flash(str(e), 'danger')

    return render_template('add_user.html', form=form)

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit_user(id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (id,)).fetchone()
    conn.close()

    form = UserForm(obj=user)
    if form.validate_on_submit():
        email = form.email_id.data
        try:
            valid = validate_email(email)
            email = valid.email
            
            conn = get_db_connection()
            conn.execute('UPDATE users SET first_name = ?, last_name = ?, phone_number = ?, email_id = ?, address = ? WHERE id = ?',
                         (form.first_name.data, form.last_name.data, form.phone_number.data, email, form.address.data, id))
            conn.commit()
            conn.close()
            flash('User updated successfully!', 'success')
            return redirect(url_for('index'))
        except EmailNotValidError as e:
            flash(str(e), 'danger')

    return render_template('edit_user.html', form=form, user=user)

@app.route('/delete/<int:id>', methods=('POST',))
def delete_user(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
