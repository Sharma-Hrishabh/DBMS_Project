from flask import Flask,render_template,request, session, flash,redirect
import sqlite3
import json
import datetime, time
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
c.execute('''CREATE TABLE IF NOT EXISTS blog (id integer NOT NULL, title varchar(64) NOT NULL,
        slug varchar(32) NOT NULL, body text NOT NULL, date text, username varchar(16) NOT NULL,
        PRIMARY KEY (id), FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE ON UPDATE CASCADE);''')

c.execute('''CREATE TABLE IF NOT EXISTS users(username varchar(16) NOT NULL, password varchar(64) NOT NULL,
        join_date text, name varchar(32) NOT NULL, PRIMARY KEY(username));''')

c.execute('''CREATE TABLE IF NOT EXISTS email (mail varchar(64) NOT NULL, username varchar(16),
        FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE ON UPDATE CASCADE ,
        PRIMARY KEY(mail, username), UNIQUE(mail, username));''')

c.execute('''CREATE TABLE IF NOT EXISTS wow (blog_id integer NOT NULL, username varchar(16) NOT NULL,
        status integer NOT NULL, FOREIGN KEY(blog_id) REFERENCES blog(id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE ON UPDATE CASCADE,
        PRIMARY KEY(blog_id, username));''')

c.execute('''CREATE TABLE IF NOT EXISTS comment (id integer NOT NULL, username varchar(16) NOT NULL,
        data text NOT NULL, blog_id integer NOT NULL, date text NOT NULL,
        PRIMARY KEY(id), FOREIGN KEY(blog_id) REFERENCES blog(id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE ON UPDATE CASCADE)''')

c.execute('''CREATE TABLE IF NOT EXISTS category (blog_id integer NOT NULL, type varchar(16) NOT NULL,
        FOREIGN KEY(blog_id) REFERENCES blog(id) ON DELETE CASCADE ON UPDATE CASCADE, PRIMARY KEY(blog_id, type));''')


# Indexing

c.execute('CREATE INDEX IF NOT EXISTS idx_id_blog on blog(id);')
c.execute('CREATE INDEX IF NOT EXISTS idx_username_users on users(username);')
c.execute('CREATE INDEX IF NOT EXISTS idx_title_blog on blog(title);')
# c.execute("INSERT INTO users VALUES ('hri','abc','xyz@gmail.com','Hrishabh');")
# c.execute("INSERT INTO blog VALUES ('1','qwe','qwe','dvfdvfdvfdvdfvfdv','2006-01-05');")
# c.execute('SELECT * FROM blog;')

conn.commit()
conn.close()
# print(c.fetchone())
@app.route('/')
def index():
    with sqlite3.connect(DATABASE) as c:
        cur = c.cursor()
        cur.execute('SELECT * FROM blog ORDER BY date DESC LIMIT 10;')
        blogs = cur.fetchall()
        # print(blogs)
        if session.get('logged_in'):
            curruser = session['username']
            return render_template('index.html',blogs=blogs,loginstatus='True',curruser=curruser)
        else:
            return render_template('index.html',blogs=blogs,loginstatus='False')
        c.close()

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
    if session.get('logged_in'):
        return "<script>alert('You are already logged in');window.location = 'http://localhost:5000/';</script>"
    else:
        if request.method=='POST':
            with sqlite3.connect(DATABASE) as c:
                cur = c.cursor()
                username = request.form['username']
                password = request.form['password']
                received_pass = password+'5xy'
                h = hashlib.md5(received_pass.encode())
                print(h.hexdigest())
                data = cur.execute("SELECT * FROM users WHERE username = ?",[username])
                data = cur.fetchall()
                print(len(data))
                if len(data) > 0:
                    data = data[0][1]
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
                    return "User not registered"
                c.close()
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
    if request.method=='POST':
        with sqlite3.connect(DATABASE) as c:
            cur = c.cursor()
            title = request.form['title']
            slug = request.form['slug']
            body = request.form['body']
            art = request.form.getlist('art')
            science = request.form.getlist('science')
            technology = request.form.getlist('technology')
            computer = request.form.getlist('computer')
            if (session.get('username') != None):
                id = int(time.time()*1000)
                cur.execute('INSERT INTO blog VALUES(?, ?, ?, ?, ?, ?)',
                    (id, title, slug, body, str(datetime.datetime.now()), session['username'], ))
                print(cur.rowcount)
                if len(art) and art[0] == 'on':
                    i = cur.execute('INSERT INTO category VALUES(?, ?)', (id, 'art'))
                if len(science) and science[0] == 'on':
                    i = cur.execute('INSERT INTO category VALUES(?, ?)', (id, 'science'))
                if len(technology) and technology[0] == 'on':
                    i = cur.execute('INSERT INTO category VALUES(?, ?)', (id, 'technology'))
                if len(computer) and computer[0] == 'on':
                    i = cur.execute('INSERT INTO category VALUES(?, ?)', (id, 'computer'))
                c.commit()
                return "Created"
            else:
                return "You are not logged in."
            c.close()
    else:
        if (session.get('username') == None):
            return "You need to be logged in"
        else:
            return render_template('create_blog.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        author = request.form['author']
        title = request.form['title']
        year = request.form['year']
        category = request.form['category']

        if (author == "" and title == "" and year == "" and category == ""):
            return "No search query given"
        with sqlite3.connect(DATABASE) as c:
            cur = c.cursor()
            query = 'SELECT * FROM blog WHERE '
            if author != "":
                query += 'username LIKE \'%'+author+'%\''
            if title != "":
                if len(query) > 26:
                    query += ' ' + request.form['tcheck'] + ' '
                query += 'title LIKE \'%'+title+'%\''
            if year != "":
                if len(query) > 26:
                    query += ' ' + request.form['ycheck'] + ' '
                query += 'date LIKE \''+year+'%\''
            if category != "":
                if len(query) > 26:
                    query += ' ' + request.form['ccheck'] + ' '
                    query += 'id IN (SELECT blog_id FROM category WHERE type = ?)'
                if author != "":
                    query += ' OR username IN (SELECT username FROM users WHERE name LIKE ?);'
                    cur.execute(query, (category, author))
                else:
                    cur.execute(query + ';', [category])
            else:
                if author != "":
                    query += ' OR username IN (SELECT username FROM users WHERE name LIKE ?);'
                    cur.execute(query, [author])
                else:
                    cur.execute(query + ';')

            blogs = cur.fetchall()
            if len(blogs) == 0:
                return "No blogs match your search query"
            return render_template('search.html',blogs=blogs)
            c.close()

@app.route('/blog/<slug>/<id>', methods=['GET'])
def blog(slug, id):
    print(slug, id)
    with sqlite3.connect(DATABASE) as c:
        cur = c.cursor()
        cur.execute('SELECT * FROM blog where id = ?', [id])
        blog = cur.fetchall()[0]
        cur.execute('SELECT count(*) FROM wow WHERE blog_id = ?', [id])
        wows = cur.fetchone()[0]
        cur.execute('SELECT type FROM category WHERE blog_id = ?', [id])
        category = cur.fetchall()
        # print(wows)
        if session.get('logged_in'):
            curruser = session['username']
            return render_template('blog_view.html',blog=blog,wows=wows,category=category,loginstatus='True',curruser=curruser)
        else:
            return render_template('blog_view.html',blog=blog,wows=wows,category=category,loginstatus='False')

@app.route('/blog/<slug>/<id>/edit', methods=['GET', 'POST'])
def blogedit(slug, id):
    print(slug, id)
    if request.method == 'POST':
        with sqlite3.connect(DATABASE) as c:
            cur = c.cursor()
            title = request.form['title']
            slug1 = request.form['slug']
            body = request.form['body']
            art = request.form.getlist('art')
            science = request.form.getlist('science')
            technology = request.form.getlist('technology')
            computer = request.form.getlist('computer')
            cur.execute('UPDATE blog SET body = ?, title = ? , slug = ? where id = ?', (body, title , slug1 , id))

            cur.execute('DELETE FROM category WHERE blog_id = ?', [id])
            if len(art) and art[0] == 'on':
                i = cur.execute('INSERT INTO category VALUES(?, ?)', (id, 'art'))
            if len(science) and science[0] == 'on':
                i = cur.execute('INSERT INTO category VALUES(?, ?)', (id, 'science'))
            if len(technology) and technology[0] == 'on':
                i = cur.execute('INSERT INTO category VALUES(?, ?)', (id, 'technology'))
            if len(computer) and computer[0] == 'on':
                i = cur.execute('INSERT INTO category VALUES(?, ?)', (id, 'computer'))
            c.commit()
            return redirect("http://localhost:5000/blog/"+slug1+"/"+id, code=200)
            c.close()
    elif request.method == 'GET':
        with sqlite3.connect(DATABASE) as c:
            cur = c.cursor()
            cur.execute('SELECT * FROM blog where id = ?', [id])
            blog = cur.fetchall()[0]
            cur.execute('SELECT type FROM category WHERE blog_id = ?', [id])
            return render_template('blogedit.html',blog=blog, cat=cur.fetchall())
            c.close()

@app.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
    if request.method == 'GET':
        with sqlite3.connect(DATABASE) as c:
            if session.get('username'):
                username = session['username']
                print(username)
                cur = c.cursor()
                cur.execute('SELECT * FROM users NATURAL JOIN email WHERE username LIKE ?;', [username])
                print(cur.fetchall())
                if len(cur.fetchall()) == 0:
                    return "user not in database"
                else:
                    return cur.fetchone()
                c.close()
            else:
                return "User not logged in"
    elif request.method == 'POST':
        username = ""
        if session.get('username'):
            username = session['username']
        else:
            return "User not logged in"
        name = request.form['name']
        mail = request.form['mail']
        password = request.form['password']+'5xy'
        password = hashlib.md5(password.encode()).hexdigest()
        with sqlite3.connect(DATABASE) as c:
            cur = c.cursor()
            cur.execute('UPDATE email SET mail = ? WHERE username LIKE ?;', (mail, username))
            cur.execute('UPDATE users SET name = ?, password = ? WHERE username LIKE ?;', (name, password, username))
            c.commit()
            return redirect("http://localhost:5000/user/"+username, code=200)
            c.close()

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    print(session.keys())
    session.clear()
    print(session.keys())
    return redirect("http://localhost:5000")
    
@app.route('/blog/<slug>/<id>/wow/', methods=['POST'])
def wow(slug, id):
    if session.get('username'):
        with sqlite3.connect(DATABASE) as c:
            cur = c.cursor()
            val = 0
            cur.execute('SELECT * FROM wow WHERE username LIKE ? AND blog_id = ?;', (session['username'], id))
            data = cur.fetchall()
            if len(data) > 0:
                cur.execute('DELETE FROM wow WHERE username LIKE ? AND blog_id = ?;', (session['username'], id))
                val = -1
            else:
                cur.execute('INSERT INTO wow VALUES (?, ?, ?)', (id, session['username'], 1))
                val = 1
            c.commit()
            return str(val)
            c.close()
    else:
        print("user not logged in")
        return str(0)

# @app.route('/wow', methods=['POST'])
# def www():
#     print('Caught you')
#     return "done"

if __name__ == '__main__':
    app.run(port=5001,debug = True)
