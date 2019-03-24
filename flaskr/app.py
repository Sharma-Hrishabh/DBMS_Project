from flask import Flask,render_template,request
import sqlite3
from flask import g
import hashlib
DATABASE = '../database.db'

app = Flask(__name__)

# def get_db():
#     db = getattr(g, '_database', None)
#     if db is None:
#         db = g._database = sqlite3.connect(DATABASE)
#         print('db connected')
#     return db

# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()

conn = sqlite3.connect(DATABASE)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS blog (id integer, title varchar(64), slug varchar(32),
        body text, date text, PRIMARY KEY (id));''')

c.execute('''CREATE TABLE IF NOT EXISTS users(username varchar(16), password varchar(64),
        email varchar(64), name varchar(32), PRIMARY KEY(username), UNIQUE(email));''')

c.execute('''CREATE TABLE IF NOT EXISTS postedby (id integer, username varchar(16),
        FOREIGN KEY(id) REFERENCES blog(id), FOREIGN KEY(username) REFERENCES users(username));''')

# c.execute("INSERT INTO users VALUES ('hri','abc','xyz@gmail.com','Hrishabh');")
# c.execute("INSERT INTO blog VALUES ('1','qwe','qwe','dvfdvfdvfdvdfvfdv','2006-01-05');")
# c.execute('SELECT * FROM blog;')

conn.commit()
# print(c.fetchone())
@app.route('/')
def hello():
    return "Hello World!"

@app.route('/signup/',methods=['POST', 'GET'])
def signup():
    if request.method=='POST':
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            username=request.form['username']
            password=request.form['password']
            email=request.form['emailid']
            name=request.form['name']
            salt = '5xy'
            actualpass=password+salt
            h = hashlib.md5(actualpass.encode())
            cur.execute('INSERT INTO users VALUES(?, ?, ?, ?);',(username,actualpass,email,name))
            con.commit()
            # con.close()
            print(name)
            return "Name : "+request.method+"  "+username
    else:
        return render_template('signup.html')

@app.route('/login/')
def login():
    error = ''
    if request.method == 'POST':
        with sqlite3.connect(DATABASE) as c:
            cur = c.cursor()
            username = request.form['username']
            password = request.form['password']
            received_pass = password+'5xy'
            h = hashlib.md5(received_pass.encode())
            data = cur.execute("SELECT * FROM users WHERE username = (%s)",username)
            data = c.fetchone()[2]
            if h == data:
                session['logged_in']=True
                session['username']=username

                flash('You are now logged in')
                print('You are logged in')
            else:
                error="Invalid credentials"

    else:
        return render_template('login.html')


if __name__ == '__main__':
    app.run(port=5001,debug = True)
