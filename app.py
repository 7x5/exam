from flask import *
import hashlib
import sqlite3
import datetime
from datetime import timedelta

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
    else:
        return redirect(url_for('/'))
    
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
    else:
        return redirect(url_for('/'))
    
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
    else:
        return redirect(url_for('/'))
    
@app.route('/fulfor', methods=['POST'])
def fulfor():
    if 'admin' in session and session['admin']:
        problem_id = request.form['problem_id']
        losning = request.form['losning']

        con = sqlite3.connect('database.db', check_same_thread=True, uri=True)
        c = con.cursor()
        c.execute("UPDATE arbeid SET fulforttime = ?, losning = ? WHERE problem_id = ?", (datetime.datetime.now(), losning, problem_id))
        c.execute("UPDATE problemer SET status = 'Løst' WHERE problem_id = ?", (problem_id,))
        con.commit()
        con.close()

        return redirect(url_for('ulost'))
    else:
        return redirect(url_for('/'))

@app.route

    
@app.route('/dineproblemer')
def dineproblemer():
    if 'logged_in' in session and session['logged_in']:
        con = sqlite3.connect('database.db', check_same_thread=False, uri=True)
        c = con.cursor()
        c.execute("SELECT * FROM problemer WHERE helenavn = ?", (session['username'],))
        problems = c.fetchall()
        con.close()



        arbeid_data = []
        if problems:
            con = sqlite3.connect('database.db')
            c = con.cursor()
            for problem in problems:
                problem_id = problem[0]
                c.execute("SELECT person, time, fulforttime, losning FROM arbeid WHERE problem_id = ?", (problem_id,))
                arbeid_rows = c.fetchall()
                for arbeid_row in arbeid_rows:
                    person = arbeid_row[0]
                    time = arbeid_row[1]
                    fulfortime = arbeid_row[2]
                    losning = arbeid_row[3]
                    arbeid_data.append((problem_id, person, time, fulfortime, losning))
            con.close()
            
        print(problems[0][0])
        print(arbeid_data[0][0])

        admin = session['admin']
        username = session['username']
        logged_in = session['logged_in']
        return render_template('dineproblemer.html', username=username, admin=admin, logged_in=logged_in, problems=problems, arbeid_data=arbeid_data)

@app.route('/sok', methods=['GET', 'POST'])
def sok():
    if 'admin' in session and session['admin']:
        if request.method == 'POST':
            con = sqlite3.connect('database.db')
            c = con.cursor()
            telenr = request.form['telenr']
            filter_option = request.form.get('filter_option')

            if filter_option == 'Uløst':
                c.execute("SELECT * FROM problemer WHERE telenr=? AND status='Uløst'", (telenr,))
            elif filter_option == 'Under arbeid':
                c.execute("SELECT problemer.*, arbeid.person, arbeid.time FROM problemer LEFT JOIN arbeid ON problemer.problem_id = arbeid.problem_id WHERE problemer.telenr=? AND problemer.status='Under arbeid'", (telenr,))
            elif filter_option == 'Løst':
                c.execute("SELECT problemer.*, arbeid.person, arbeid.losning, arbeid.fulforttime FROM problemer LEFT JOIN arbeid ON problemer.problem_id = arbeid.problem_id WHERE problemer.telenr=? AND problemer.status='Løst'", (telenr,))
            else:
                c.execute("SELECT * FROM problemer WHERE telenr=?", (telenr,))

            resultat = c.fetchall()
            print(resultat)
            con.close()
            return render_template('sok.html', telenr=telenr, filter_option=filter_option, resultat=resultat)
        else:
            telenr = request.args.get('telenr')
            filter_option = request.args.get('filter_option')

            con = sqlite3.connect('database.db')
            c = con.cursor()

            if filter_option == 'Uløst':
                c.execute("SELECT * FROM problemer WHERE telenr=? AND status='Uløst'", (telenr,))
            elif filter_option == 'Under arbeid':
                c.execute("SELECT problemer.*, arbeid.person, arbeid.time FROM problemer LEFT JOIN arbeid ON problemer.problem_id = arbeid.problem_id WHERE problemer.telenr=? AND problemer.status='Under arbeid'", (telenr,))
            elif filter_option == 'Løst':
                c.execute("SELECT problemer.*, arbeid.person, arbeid.losning, arbeid.fulforttime FROM problemer LEFT JOIN arbeid ON problemer.problem_id = arbeid.problem_id WHERE problemer.telenr=? AND problemer.status='Løst'", (telenr,))
            else:
                c.execute("SELECT * FROM problemer WHERE telenr=?", (telenr,))

            resultat = c.fetchall()
            print(resultat)
            con.close()
            admin = session['admin']
            username = session['username']
            logged_in = session['logged_in']
            return render_template('sok.html', telenr=telenr, filter_option=filter_option, resultat=resultat, admin=admin, logged_in=logged_in, username=username)
    else:
        return redirect(url_for('/'))

from datetime import datetime
from flask import render_template
import sqlite3

@app.route('/statistikk')
def statistikk():
    con = sqlite3.connect('database.db')
    c = con.cursor()

    c.execute("SELECT COUNT(*) FROM problemer")
    totalt_antall_hendelser = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM problemer WHERE status='Uløst'")
    antall_uloste_hendelser = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM problemer WHERE status='Under arbeid'")
    antall_saker_under_arbeid = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM problemer WHERE status='Løst'")
    antall_losede_saker = c.fetchone()[0]

    c.execute("SELECT arbeid.fulforttime, problemer.time FROM arbeid JOIN problemer ON arbeid.problem_id = problemer.problem_id WHERE problemer.status = 'Løst';")
    gjennomsnittforregning = c.fetchall()

    c.execute("SELECT arbeid.time, problemer.time FROM arbeid  JOIN problemer ON arbeid.problem_id = problemer.problem_id  WHERE problemer.status = 'Løst' OR problemer.status =  'Under arbeid';")
    gjennomsnittforregning2 = c.fetchall()

    tidsforskjeller = []
    for regninger in gjennomsnittforregning:
        tid1 = datetime.strptime(regninger[0], '%Y-%m-%d %H:%M:%S.%f')
        tid2 = datetime.strptime(regninger[1], '%Y-%m-%d %H:%M:%S.%f')
        tidsforskjell  = tid1 - tid2
        tidsforskjeller.append(tidsforskjell.total_seconds())

    snitt_tidsforskjell = sum(tidsforskjeller) / len(tidsforskjeller)
    snittferdig = timedelta(seconds=int(snitt_tidsforskjell))

    tidsforskjeller2 = []
    for regninger in gjennomsnittforregning2:
        tid1 = datetime.strptime(regninger[0], '%Y-%m-%d %H:%M:%S.%f')
        tid2 = datetime.strptime(regninger[1], '%Y-%m-%d %H:%M:%S.%f')
        tidsforskjell2  = tid1 - tid2
        tidsforskjeller2.append(tidsforskjell2.total_seconds())

    snitt_tidsforskjell2 = sum(tidsforskjeller2) / len(tidsforskjeller2)
    snittferdig2 = timedelta(seconds=int(snitt_tidsforskjell2))

    con.close()

    admin = session['admin']
    username = session['username']
    logged_in = session['logged_in']
    return render_template('statistikk.html', totalt_antall_hendelser=totalt_antall_hendelser, antall_uloste_hendelser=antall_uloste_hendelser, antall_saker_under_arbeid=antall_saker_under_arbeid, antall_losede_saker=antall_losede_saker, username=username, logged_in=logged_in, admin=admin, snittferdig=snittferdig, snittferdig2=snittferdig2)




@app.route("/logout", methods=['POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('telenr', None)
    return redirect(url_for('login'))
    

app.run(host="0.0.0.0", port=5001, debug=True)