import os
from flask_sqlalchemy import SQLAlchemy
from flask import *
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = "nonflask"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


ALLOWED_EXTENSIONS = set(['txt'])

db = SQLAlchemy(app)


class users(db.Model):
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key=True)
    first_name = db.Column('first_name', db.String(100))
    last_name = db.Column('last_name', db.String(100))
    email = db.Column('email', db.String(100))
    password = db.Column('password', db.String(100))

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password

@app.route('/')
def index():
    if 'set' not in session:
        return render_template('login.html')
    else:
        first_name = session['first_name']
        last_name = session['last_name']
        email = session['email']
        return render_template('index.html', first_name=first_name, last_name=last_name, email=email)


@app.route('/login', methods=('GET','POST'))
def login():
    email = request.form['email']
    password = request.form['password']
    data = users.query.filter_by(email=email).all()
    if len(data)>0:
        for x in data:
            original_pass = x.password
            first_name = x.first_name
            last_name = x.last_name
        if password == original_pass:
            session['set'] = '1'
            session['email'] = email
            session['first_name'] = first_name
            session['last_name'] = last_name
            return redirect(url_for('index'))
        else:
            flash('Failed Login')
            return render_template('login.html')
    else:
        flash('User Not Found')
        return render_template('login.html')


@app.route('/signup/', methods=('GET','POST'))
def signup():
    if request.method == 'GET':
        return render_template('signup.html', first_name ='', last_name='', email='')
    elif request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']

        if password == confirm:
            data = users.query.filter_by(email=email).all()
            if len(data)<=0:
                user = users(first_name, last_name, email, password)
                db.session.add(user)
                db.session.commit()
                session['set'] = '1'
                session['email'] = email
                session['first_name'] = first_name
                session['last_name'] = last_name
                return redirect(url_for('index'))
            else:
                flash("Email Id exist")
                return render_template('signup.html', first_name=first_name, last_name=last_name, email='')
        else:
            flash("Confirm Password and Password dont match")
            return render_template('signup.html',first_name = first_name, last_name = last_name, email=email)


@app.route('/logout/')
def logout():
    session.pop('set')
    session.pop('first_name')
    session.pop('last_name')
    session.pop('email')
    return render_template('login.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')
            return redirect('/')
        else:
            flash('Allowed file types are: .txt')
            return redirect(request.url)

if __name__ == '__main__':
    db.create_all()
    app.run()