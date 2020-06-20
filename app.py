from flask import Flask,session,render_template,flash,request,redirect,url_for,send_from_directory,send_file,Response
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt


app = Flask(__name__,template_folder="./templates")

app.secret_key='secretapp123'


# Config MYSQL
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///home/manish/Desktop/sem_2/study_mat/iwp/j_comp/Vnotes/myflaskdb.db'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Barik7004'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init mysql
mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('index.html')

class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=4, max=50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords do not match')
	])
	confirm = PasswordField('Confirm Password', [
		validators.DataRequired(),
		validators.EqualTo('password', message='Passwords do not match')])


@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))
		
		# Creating a cursor
		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",(name, email, username, password) )
		
		# Commit to DB
		mysql.connection.commit()

		# Close the connection
		cur.close()

		flash('Great! You are now registered and can login.', 'success')
		
		redirect(url_for('register'))

	return render_template('register.html', form = form)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password_candidate = request.form['password']

		# Creating a cursor
		cur = mysql.connection.cursor()
		result = cur.execute("SELECT * FROM users WHERE username= %s",[username] )
		
		if result>0:
			# Get stored hash
			data = cur.fetchone()
			password = data['password']

			# Compare passwords
			if sha256_crypt.verify(password_candidate, password):
				app.logger.info('PASSWORD MATCHED')

			else:
				error = 'Passwords did not match'
				return render_template('login.html')
		else:
			app.logger.info('NO USER')
			return render_template('login.html')

		# # Commit to DB
		# mysql.connection.commit()

		# Close the connection

		flash('Great! You are now logged in!', 'success')
		

	return render_template('login.html')
