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
        email = request.form['email']
        passord = request.form['passord']

        con = sqlite3.connect('database.db', check_same_thread=False, uri=True)
        c = con.cursor()
        c.execute("SELECT * FROM brukere WHERE email=?", (email,))
        user = c.fetchone()
        con.close()


        if user:
            lagret_passord = user[3]
            hashed_passord = hashlib.sha256(passord.encode()).hexdigest()
            if lagret_passord == hashed_passord:
                session['username'] = user[1]
                session['logged_in'] = True
                session['admin'] = bool(user[4])
                session['telenr'] = user[2]
                session['email'] = email
                return redirect(url_for('index'))

        return 'Invalid password or username'

    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        brukernavn = request.form['brukernavn']
        passord = request.form['passord']
        telenr = request.form['telenr']
        email = request.form['email']

        hashed_passord = hashlib.sha256(passord.encode()).hexdigest()

        con = sqlite3.connect('database.db', check_same_thread=False, uri=True)
        c = con.cursor()
        c.execute("INSERT INTO brukere (brukernavn, passord, admin, telenr, email) VALUES (?, ?, ?, ?, ?)", (brukernavn, hashed_passord, 0, telenr, email))
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
            email = session['email']

            con = sqlite3.connect('database.db', check_same_thread=False, uri=True)
            c = con.cursor()
            c.execute("INSERT INTO problemer (helenavn, telenr, time, body, kort_bes, status, email) VALUES (?, ?, ?, ?, ?, ?, ?)", (navn, telenr, datetime.datetime.now(), langbes, kortbes, 'Uløst', email))
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
        con = sqlite3.connect('database.db', check_same_thread=False, uri=True)
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

        con = sqlite3.connect('database.db', check_same_thread=True, uri=True)
        c = con.cursor()
        c.execute("INSERT INTO arbeid (problem_id, person, time) VALUES (?, ?, ?)", (problem_id, bruker, datetime.datetime.now()))
        c.execute("UPDATE problemer SET status = 'Under arbeid' WHERE problem_id = ?", (problem_id,))
        con.commit()
        con.close()

        return redirect(url_for('ulost'))
    
@app.route('/underarbeid')
def underarbeid():
    if 'admin' in session and session['admin']:
        con = sqlite3.connect('database.db', check_same_thread=False, uri=True)
        c = con.cursor()
        c.execute("SELECT * FROM problemer WHERE status = 'Under arbeid'")
        under = c.fetchall()
        con.close()

        arbeid_data = []
        if under:
            con = sqlite3.connect('database.db')
            c = con.cursor()
            for problem in under:
                problem_id = problem[0]
                c.execute("SELECT problem_id, person, time FROM arbeid WHERE problem_id = ?", (problem_id,))
                arbeid_row = c.fetchone()
                if arbeid_row:
                    person = arbeid_row[0]
                    time = arbeid_row[1]
                    problem_id = arbeid_row[2]
                    arbeid_data.append((person, time, problem_id))
            con.close()
            
            # time_str = time[0]
            # time_obj = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
            # formatted_time = time_obj.strftime('%d-%m-%Y %H:%M:%S')
            # time = formatted_time

        username = session['username']
        admin = session['admin']
        logged_in = session['logged_in']
        return render_template('underarbeid.html', username=username, admin=admin, logged_in=logged_in, under=under, arbeid_data=arbeid_data)
    
@app.route('/dineproblemer')
def dineproblemer():
    if 'logged_in' in session and session['logged_in']:
        con = sqlite3.connect('database.db', check_same_thread=False, uri=True)
        c = con.cursor()
        c.execute("SELECT * FROM problemer WHERE helenavn = ?", (session['username'],))
        problems = c.fetchall()
        con.close()

        admin = session['admin']
        username = session['username']
        logged_in = session['logged_in']
        return render_template('dineproblemer.html', username=username, admin=admin, logged_in=logged_in, problems=problems)



@app.route("/logout", methods=['POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('telenr', None)
    return redirect(url_for('login'))
    

app.run(host="0.0.0.0", port=5001, debug=True)