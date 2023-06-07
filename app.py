from flask import *
import hashlib
import sqlite3

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'

@app.route("/")
def index():
    if 'logged_in' in session and session['logged_in']:
        return render_template('index.html')
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
        admin = c.fetchone()
        con.close()

        if admin:
            lagret_passord = admin[2]
            hashed_passord = hashlib.sha256(passord.encode()).hexdigest()
            if lagret_passord == hashed_passord:
                session['logged_in'] = True
                return redirect(url_for('index')) 
            
        return 'Invaild password or username'
    
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        brukernavn = request.form['brukernavn']
        passord = request.form['passord']

        hashed_passord = hashlib.sha256(passord.encode()).hexdigest()

        con = sqlite3.connect('database.db', check_same_thread=False, uri=True)
        c = con.cursor()
        c.execute("INSERT INTO brukere (brukernavn, passord, admin) VALUES (?, ?, ?)", (brukernavn, hashed_passord, 0))
        con.commit()
        con.close()
        return redirect(url_for('login'))
    
    return render_template('register.html')

    
    

app.run(host="0.0.0.0", port=5001, debug=True)