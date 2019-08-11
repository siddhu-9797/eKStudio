from flask import Flask, render_template, url_for, flash, redirect, request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, TextAreaField, RadioField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import login_user, current_user, logout_user, login_required,UserMixin
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    dob = db.Column(db.String(60), nullable=False)
    post = db.relationship('Post', backref='creator', lazy=True)
    

    def __repr__(self):
        return f"User('{self.username}', '{self.email}',  '{self.dob}', '{self.password}' )"




class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable = False)
    persontodo = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.String(100), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    branch = db.Column(db.String(10), nullable = False)
    accordion = db.Column(db.String(10), nullable = False, default = '1')
    dependencies = db.Column(db.String(6), nullable=False)
    filename = db.Column(db.String(300), nullable=True)
    filedata = db.Column(db.LargeBinary)
    story = db.Column(db.String(100), nullable=False)

    
    def __repr__(self):
        return f"Post('{self.title}')"
db.create_all()



    

class Rgsterfom(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=1, max=50)])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(),EqualTo('password')])
    dob = StringField('Date Of Birth', validators=[DataRequired()] )
    submit = SubmitField('Samarpinchu')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Sorry, this username is not available... Please choose another one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email already exists... Try signing in.')
    

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign-In')


class create_task(FlaskForm):
    title = StringField('Title', validators=[DataRequired()] )
    
    description = TextAreaField('Description', validators=[DataRequired()])
    priority = StringField('priority', validators=[DataRequired()])
    story = StringField('Select A Story', validators=[DataRequired()])
    persontodo = StringField('Person Name', validators=[DataRequired()])
    dependencies = RadioField('Dependencies', choices = [('B','Before'),('A','After')])
    submit = SubmitField('Create Task')

class place(FlaskForm):
    branch = StringField('branch',validators=[DataRequired()])
    


@app.route("/")
def wel():
    return redirect('home')

@app.route("/home", methods=['GET', 'POST'])
def home():
    branc = place()
    tasks = Post.query.all()
    if request.method == "POST":
        if (request.form["update3"]):
            update1 = request.form["update1"]
            #update2 = request.form["update3"]
            admin = Post.query.filter_by(id= update1).first()
            #print('Updates is ' + update1 + " " + update2)
            update = int(admin.accordion) + 1
            admin.accordion = str(update) 
            admin.branch = "todo"
            db.session.commit()

        else:   
            update1 = request.form["update1"]
            update2 = request.form["update2"]
            print('Updates is ' + update1 + " " + update2)
            admin = Post.query.filter_by(id= update1).first()
            admin.branch = update2
            db.session.commit()
                
    l = len(tasks)
    return render_template('home.html', tasks= tasks, i=1, l=l, branc = branc)
@app.route("/registe", methods=['GET', 'POST'])
def register():
    frm = Rgsterfom()
    if frm.validate_on_submit():
        user = User(username=frm.username.data, email=frm.email.data, password=frm.password.data, dob = frm.dob.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created.', 'success')
        logout_user()
        return redirect('login')
    return render_template('register.html', form=frm, title="Register")


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if (user and (form.password.data == user.password)):
            flash(f'You have successfully logged in!!', 'success')
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
            
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/new", methods=['GET', 'POST'])
def new():  
    return render_template('newstory.html')





@app.route("/create_task", methods=['GET', 'POST'])
@login_required
def create():

    task = create_task()
    poster = Post.query.all()
    user = User.query.all()
    l = len(poster)
    m = len(user)
    if task.validate_on_submit():
        fle = request.files['filess']
        
        if fle:
            post= Post(title= task.title.data,description = task.description.data,filename = fle.filename, filedata = fle.read(), priority = task.priority.data, story = task.story.data, persontodo= task.persontodo.data, dependencies = task.dependencies.data, creator=current_user, branch = 'todo')
            db.session.add(post)
            db.session.commit()
        else:
            post= Post(title= task.title.data,description = task.description.data, priority = task.priority.data, story = task.story.data, persontodo= task.persontodo.data, dependencies = task.dependencies.data, creator=current_user, branch = 'todo')
            db.session.add(post)
            db.session.commit()
        flash('New Task has been Added!!', 'success')
        return redirect(url_for('home'))
    return render_template('create_task.html',title = 'New Task',  form=task, l=l, poster = poster,user = user, m =m)




@app.route("/logout")
def logout():
    logout_user()
    flash(f'You have been successfully logged out', 'danger')
    return redirect(url_for('home'))

@app.route('/home2', methods=['POST', 'GET'])
def home2():
    tasks = Post.query.all()
    

    l = len(tasks)
    print('Recieved from client: {}'.format(request.data))
    return render_template('home2.html', tasks= tasks, i=1, k=l)



@app.route('/news')
def news():
    tasks = Post.query.all()
    return render_template('newstory.html', tasks= tasks)

@app.route('/board')
def board():
    tasks = Post.query.all()
    return render_template('board.html', tasks= tasks)

@app.route('/hori')
def hori():
    tasks = Post.query.all()
    return render_template('horizontal.html', tasks= tasks)

@app.route("/secondary")
def secondary():
    branc = place()
    tasks = Post.query.all()
    l = len(tasks)
    return render_template('secondary.html', tasks= tasks, i=1, l=l, branc = branc)



@app.route("/task/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('task.html', title=post.title, post=post)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')


