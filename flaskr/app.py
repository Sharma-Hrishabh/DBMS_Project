from flask import Flask,render_template,request, session, flash
import sqlite3
import datetime
from flask import g
import hashlib
DATABASE = '../database.db'

app = Flask(__name__)
app.secret_key = "thisisaserceretkey"

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
c.execute('''CREATE TABLE IF NOT EXISTS blog (id integer AUTO_INCREMENT, title varchar(64) NOT NULL,
        slug varchar(32) NOT NULL, body text NOT NULL, date text, username varchar(16) NOT NULL,
        PRIMARY KEY (id), FOREIGN KEY(username) REFERENCES users(username));''')

c.execute('''CREATE TABLE IF NOT EXISTS users(username varchar(16), password varchar(64) NOT NULL,
        join_date text, name varchar(32) NOT NULL, PRIMARY KEY(username));''')

c.execute('''CREATE TABLE IF NOT EXISTS email (mail varchar(64), username varchar(16),
        FOREIGN KEY(username) REFERENCES users(username), PRIMARY KEY(mail, username),
        UNIQUE(mail, username));''')

c.execute('''CREATE TABLE IF NOT EXISTS wow (blog_id integer NOT NULL, username varchar(16) NOT NULL,
        status integer NOT NULL, FOREIGN KEY(blog_id) REFERENCES blog(id),
        FOREIGN KEY(username) REFERENCES users(username), PRIMARY KEY(blog_id, username));''')

c.execute('''CREATE TABLE IF NOT EXISTS comment (id integer AUTO_INCREMENT, username varchar(16) NOT NULL,
        data text NOT NULL, blog_id integer NOT NULL, date text NOT NULL,
        PRIMARY KEY(id), FOREIGN KEY(blog_id) REFERENCES blog(id),
        FOREIGN KEY(username) REFERENCES users(username))''')

c.execute('''CREATE TABLE IF NOT EXISTS category (blog_id integer NOT NULL, type varchar(16) NOT NULL,
        FOREIGN KEY(blog_id) REFERENCES blog(id), PRIMARY KEY(blog_id, type));''')

# c.execute("INSERT INTO users VALUES ('hri','abc','xyz@gmail.com','Hrishabh');")
# c.execute("INSERT INTO blog VALUES ('1','qwe','qwe','dvfdvfdvfdvdfvfdv','2006-01-05');")
# c.execute('SELECT * FROM blog;')

conn.commit()
conn.close()
# print(c.fetchone())
@app.route('/')
def index():
    return render_template('index.html')

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
            print(h.hexdigest())
            cur.execute('INSERT INTO users VALUES(?, ?, ?, ?);',(username,h.hexdigest(),str(datetime.datetime.utcnow()),name))
            cur.execute('INSERT INTO email VALUES(?, ?);', (email, username))
            con.commit()
            print(name)
            return "Name : "+request.method+"  "+username
            con.close()
    else:
        return render_template('signup.html')

@app.route('/login/',methods=['POST', 'GET'])
def login():
    print(request.method+"")
    if request.method=='POST':
        with sqlite3.connect(DATABASE) as c:
            cur = c.cursor()
            username = request.form['username']
            password = request.form['password']
            received_pass = password+'5xy'
            h = hashlib.md5(received_pass.encode())
            print(h.hexdigest())
            data = cur.execute("SELECT * FROM users WHERE username = ?",[username])
            data = cur.fetchone()[1]
            print(data)
            if h.hexdigest() == data:
                session['logged_in']=True
                session['username']=username
                flash('You are now logged in')
                print('You are logged in')
                return('Login Successful!')
            else:
                return("Invalid credentials!")
    else:
        return render_template('login.html')

@app.route('/test/',methods=['GET'])
def test():
    if (session.get('logged_in') != None):
        if (session.get('logged_in') == True):
            return session['username'] + ' is Logged in'
        else:
            return session['username'] + ' is Logged Out'
    else:
        print(session.get('logged_in'))
        return 'Undefined User'


@app.route('/create_blog/',methods=['GET','POST'])
def create_blog():
    if request.method=="POST":
        with sqlite3.connect(DATABASE) as c:
            cur = c.cursor()
            title = request.form['title']
            slug = request.form['slug']
            body = request.form['body']
            print(title)
            return "HELLO"
    else:
        return render_template('create_blog.html')




if __name__ == '__main__':
    app.run(port=5001,debug = True)
