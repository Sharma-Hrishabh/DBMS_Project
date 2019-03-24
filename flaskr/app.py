from flask import Flask,render_template,request
import sqlite3
from flask import g

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
       username=request.form['username']
       password=request.form['password']
       email=request.form['email']
       name=request.form['name']
       print(name)
       return "Name : "+request.method+"  "+username
    else:
        return render_template('signup.html')

if __name__ == '__main__':
    app.run(port=8000,debug = True)
