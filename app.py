from flask import *
import hashlib
import sqlite3
import datetime

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'

@app.route("/")
def index():
    if 'logged_in' in session and session['logged_in']:
        logged_in = session['logged_in']
        username = session['username']
        admin = session.get('admin', False)
        return render_template('index.html', username=username, admin=admin, logged_in=logged_in)
    else:
        return redirect(url_for('login'))
    
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        brukernavn = request.form['brukernavn']
        passord = request.form['passord']

        con = sqlite3.connect('database.db')
        c = con.cursor()
        c.execute("SELECT * FROM brukere WHERE brukernavn=?", (brukernavn,))
        user = c.fetchone()
        con.close()


        if user:
            lagret_passord = user[3]
            hashed_passord = hashlib.sha256(passord.encode()).hexdigest()
            if lagret_passord == hashed_passord:
                session['username'] = brukernavn
                session['logged_in'] = True
                session['admin'] = bool(user[4])
                session['telenr'] = user[2]
                return redirect(url_for('index'))

        return 'Invalid password or username'

    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        brukernavn = request.form['brukernavn']
        passord = request.form['passord']
        telenr = request.form['telenr']

        hashed_passord = hashlib.sha256(passord.encode()).hexdigest()

        con = sqlite3.connect('database.db', check_same_thread=False, uri=True)
        c = con.cursor()
        c.execute("INSERT INTO brukere (brukernavn, passord, admin, telenr) VALUES (?, ?, ?, ?)", (brukernavn, hashed_passord, 0, telenr))
        con.commit()
        con.close()
        session['username'] = brukernavn
        session['telenr'] = telenr
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route("/problemer", methods=['GET', 'POST'])
def problemer():
    if 'logged_in' in session and session['logged_in']:
        if request.method == 'POST':
            navn = session['username']
            telenr = session['telenr']
            kortbes = request.form['kortbes']
            langbes = request.form['langbes']

            con = sqlite3.connect('database.db')
            c = con.cursor()
            c.execute("INSERT INTO problemer (helenavn, telenr, time, body, kort_bes, status) VALUES (?, ?, ?, ?, ?, ?)", (navn, telenr, datetime.datetime.now(), langbes, kortbes, 'Uløst'))
            con.commit()
            con.close()
        username = session['username']
        admin = session['admin']
        logged_in = session['logged_in']
        return render_template('lag-henved.html', username=username, admin=admin, logged_in=logged_in)
    else:
        return redirect(url_for('login'))

@app.route('/arbeid')
def arbeid():
    if 'admin' in session and session['admin']:
        username = session['username']
        admin = session['admin']
        logged_in = session['logged_in']
        return render_template('arbeid.html', username=username, admin=admin, logged_in=logged_in)

@app.route("/logout", methods=['POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('telenr', None)
    return redirect(url_for('login'))
    

app.run(host="0.0.0.0", port=5001, debug=True)