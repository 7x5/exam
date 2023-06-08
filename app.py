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

@app.route('/ulost')
def ulost():
    if 'admin' in session and session['admin']:
        con = sqlite3.connect('database.db')
        c = con.cursor()
        c.execute("SELECT * FROM problemer WHERE status = 'Uløst'")
        problems = c.fetchall()
        con.close()

        username = session['username']
        admin = session['admin']
        logged_in = session['logged_in']
        return render_template('ulost.html', username=username, admin=admin, logged_in=logged_in, problems=problems)
    
@app.route('/arbeid', methods=['POST'])
def arbeid():
    if 'admin' in session and session['admin']:
        problem_id = request.form['problem_id']
        bruker = session['username']

        con = sqlite3.connect('database.db')
        c = con.cursor()
        c.execute("INSERT INTO arbeid (problem_id, person, time) VALUES (?, ?, ?)", (problem_id, bruker, datetime.datetime.now()))
        c.execute("UPDATE problemer SET status = 'Under arbeid' WHERE problem_id = ?", (problem_id))
        con.commit()
        con.close()

        return redirect(url_for('ulost'))
    
@app.route('/underarbeid')
def underarbeid():
    if 'admin' in session and session['admin']:
        con = sqlite3.connect('database.db')
        c = con.cursor()
        c.execute("SELECT * FROM problemer WHERE status = 'Under arbeid'")
        under = c.fetchall()
        con.close()

        time = []
        if under:
            con = sqlite3.connect('database.db')
            c = con.cursor()
            c.execute("SELECT time FROM arbeid WHERE problem_id = ?", (under[0][0],))
            time = c.fetchone()
            con.close()

            
            time_str = time[0]
            time_obj = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
            formatted_time = time_obj.strftime('%d-%m-%Y %H:%M:%S')
            time = formatted_time

        username = session['username']
        admin = session['admin']
        logged_in = session['logged_in']
        return render_template('underarbeid.html', username=username, admin=admin, logged_in=logged_in, under=under, time=time)

@app.route("/logout", methods=['POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('telenr', None)
    return redirect(url_for('login'))
    

app.run(host="0.0.0.0", port=5001, debug=True)