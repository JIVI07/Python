from flask import Flask, render_template, url_for, flash, redirect, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max file size

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# HTML Templates
base_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Blog{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">
    <style>
        .navbar-brand { font-weight: bold; }
        .article-content { white-space: pre-line; }
        .post-img { max-height: 300px; object-fit: cover; }
        .account-img { width: 125px; height: 125px; object-fit: cover; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('home') }}">📰 FlaskBlog</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('home') }}">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('about') }}">About</a>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    {% if current_user.is_authenticated %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('new_post') }}">New Post</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('account') }}">Account</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('logout') }}">Logout</a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('login') }}">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('register') }}">Register</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-md-8">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category }} alert-dismissible fade show">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                {% block content %}{% endblock %}
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Our Sidebar</h5>
                        <p class="card-text">You can put any information here you'd like.</p>
                        <ul class="list-group">
                            <li class="list-group-item">Latest Posts</li>
                            <li class="list-group-item">Announcements</li>
                            <li class="list-group-item">Calendars</li>
                            <li class="list-group-item">Etc</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

home_template = '''
{% extends "base.html" %}
{% block content %}
    {% for post in posts.items %}
        <article class="media content-section mb-4">
            <img class="rounded-circle article-img me-3" src="{{ url_for('static', filename='uploads/' + post.author.image_file) }}">
            <div class="media-body">
                <div class="article-metadata">
                    <a class="me-2" href="{{ url_for('user_posts', username=post.author.username) }}">{{ post.author.username }}</a>
                    <small class="text-muted">{{ post.date_posted.strftime('%Y-%m-%d') }}</small>
                </div>
                <h2><a class="article-title text-decoration-none" href="{{ url_for('post', post_id=post.id) }}">{{ post.title }}</a></h2>
                <p class="article-content">{{ post.content[:200] }}...</p>
            </div>
        </article>
    {% endfor %}
    
    {% for page_num in posts.iter_pages(left_edge=1, right_edge=1, left_current=1, right_current=2) %}
        {% if page_num %}
            {% if posts.page == page_num %}
                <a class="btn btn-primary mb-4" href="{{ url_for('home', page=page_num) }}">{{ page_num }}</a>
            {% else %}
                <a class="btn btn-outline-primary mb-4" href="{{ url_for('home', page=page_num) }}">{{ page_num }}</a>
            {% endif %}
        {% else %}
            ...
        {% endif %}
    {% endfor %}
{% endblock %}
'''

post_template = '''
{% extends "base.html" %}
{% block content %}
    <article class="media content-section">
        <img class="rounded-circle article-img me-3" src="{{ url_for('static', filename='uploads/' + post.author.image_file) }}">
        <div class="media-body">
            <div class="article-metadata">
                <a class="me-2" href="{{ url_for('user_posts', username=post.author.username) }}">{{ post.author.username }}</a>
                <small class="text-muted">{{ post.date_posted.strftime('%Y-%m-%d') }}</small>
                {% if post.author == current_user %}
                    <div>
                        <a class="btn btn-secondary btn-sm mt-1 mb-1" href="{{ url_for('update_post', post_id=post.id) }}">Update</a>
                        <button type="button" class="btn btn-danger btn-sm m-1" data-bs-toggle="modal" data-bs-target="#deleteModal">Delete</button>
                    </div>
                {% endif %}
            </div>
            <h2 class="article-title">{{ post.title }}</h2>
            <p class="article-content">{{ post.content }}</p>
        </div>
    </article>

    <div class="modal fade" id="deleteModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Delete Post?</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>Are you sure you want to delete this post?</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <form action="{{ url_for('delete_post', post_id=post.id) }}" method="POST">
                        <input class="btn btn-danger" type="submit" value="Delete">
                    </form>
                </div>
            </div>
        </div>
    </div>
{% endblock %}
'''

create_post_template = '''
{% extends "base.html" %}
{% block content %}
    <div class="content-section">
        <form method="POST">
            <fieldset class="form-group">
                <legend class="border-bottom mb-4">{{ title }}</legend>
                <div class="form-group mb-3">
                    <label for="title" class="form-label">Title</label>
                    <input type="text" class="form-control" id="title" name="title" value="{{ post.title if post }}">
                </div>
                <div class="form-group mb-3">
                    <label for="content" class="form-label">Content</label>
                    <textarea class="form-control" id="content" name="content" rows="10">{{ post.content if post }}</textarea>
                </div>
            </fieldset>
            <div class="form-group">
                <button type="submit" class="btn btn-primary">Submit</button>
            </div>
        </form>
    </div>
{% endblock %}
'''

login_template = '''
{% extends "base.html" %}
{% block content %}
    <div class="content-section">
        <form method="POST">
            <fieldset class="form-group">
                <legend class="border-bottom mb-4">Log In</legend>
                <div class="form-group mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" name="email">
                </div>
                <div class="form-group mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" class="form-control" id="password" name="password">
                </div>
                <div class="form-check mb-3">
                    <input type="checkbox" class="form-check-input" id="remember" name="remember">
                    <label class="form-check-label" for="remember">Remember Me</label>
                </div>
            </fieldset>
            <div class="form-group">
                <button type="submit" class="btn btn-primary">Login</button>
            </div>
        </form>
        <div class="border-top pt-3">
            <small class="text-muted">
                Need An Account? <a class="ml-2" href="{{ url_for('register') }}">Sign Up Now</a>
            </small>
        </div>
    </div>
{% endblock %}
'''

register_template = '''
{% extends "base.html" %}
{% block content %}
    <div class="content-section">
        <form method="POST">
            <fieldset class="form-group">
                <legend class="border-bottom mb-4">Join Today</legend>
                <div class="form-group mb-3">
                    <label for="username" class="form-label">Username</label>
                    <input type="text" class="form-control" id="username" name="username">
                </div>
                <div class="form-group mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" name="email">
                </div>
                <div class="form-group mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" class="form-control" id="password" name="password">
                </div>
                <div class="form-group mb-3">
                    <label for="confirm_password" class="form-label">Confirm Password</label>
                    <input type="password" class="form-control" id="confirm_password" name="confirm_password">
                </div>
            </fieldset>
            <div class="form-group">
                <button type="submit" class="btn btn-primary">Sign Up</button>
            </div>
        </form>
        <div class="border-top pt-3">
            <small class="text-muted">
                Already Have An Account? <a class="ml-2" href="{{ url_for('login') }}">Sign In</a>
            </small>
        </div>
    </div>
{% endblock %}
'''

account_template = '''
{% extends "base.html" %}
{% block content %}
    <div class="content-section">
        <div class="media">
            <img class="rounded-circle account-img" src="{{ url_for('static', filename='uploads/' + current_user.image_file) }}">
            <div class="media-body">
                <h2 class="account-heading">{{ current_user.username }}</h2>
                <p class="text-secondary">{{ current_user.email }}</p>
            </div>
        </div>
        <form method="POST" enctype="multipart/form-data">
            <fieldset class="form-group">
                <legend class="border-bottom mb-4">Account Info</legend>
                <div class="form-group mb-3">
                    <label for="username" class="form-label">Username</label>
                    <input type="text" class="form-control" id="username" name="username" value="{{ current_user.username }}">
                </div>
                <div class="form-group mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" name="email" value="{{ current_user.email }}">
                </div>
                <div class="form-group mb-3">
                    <label for="picture" class="form-label">Update Profile Picture</label>
                    <input type="file" class="form-control" id="picture" name="picture">
                </div>
            </fieldset>
            <div class="form-group">
                <button type="submit" class="btn btn-primary">Update</button>
            </div>
        </form>
    </div>
{% endblock %}
'''

about_template = '''
{% extends "base.html" %}
{% block content %}
    <h1>About Page</h1>
    <p>This is a blog application built with Flask. It includes user authentication, CRUD operations for blog posts, and a clean, responsive design.</p>
{% endblock %}
'''

user_posts_template = '''
{% extends "base.html" %}
{% block content %}
    <h1 class="mb-3">Posts by {{ user.username }} ({{ posts.total }})</h1>
    {% for post in posts.items %}
        <article class="media content-section mb-4">
            <img class="rounded-circle article-img me-3" src="{{ url_for('static', filename='uploads/' + post.author.image_file) }}">
            <div class="media-body">
                <div class="article-metadata">
                    <a class="me-2" href="{{ url_for('user_posts', username=post.author.username) }}">{{ post.author.username }}</a>
                    <small class="text-muted">{{ post.date_posted.strftime('%Y-%m-%d') }}</small>
                </div>
                <h2><a class="article-title text-decoration-none" href="{{ url_for('post', post_id=post.id) }}">{{ post.title }}</a></h2>
                <p class="article-content">{{ post.content[:200] }}...</p>
            </div>
        </article>
    {% endfor %}
    
    {% for page_num in posts.iter_pages(left_edge=1, right_edge=1, left_current=1, right_current=2) %}
        {% if page_num %}
            {% if posts.page == page_num %}
                <a class="btn btn-primary mb-4" href="{{ url_for('user_posts', username=user.username, page=page_num) }}">{{ page_num }}</a>
            {% else %}
                <a class="btn btn-outline-primary mb-4" href="{{ url_for('user_posts', username=user.username, page=page_num) }}">{{ page_num }}</a>
            {% endif %}
        {% else %}
            ...
        {% endif %}
    {% endfor %}
{% endblock %}
'''

# Custom render function to use our string templates
def render_template_string(template_string, **context):
    from flask import render_template_string as flask_render_template_string
    return flask_render_template_string(template_string, **context)

# Routes
@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template_string(home_template, posts=posts)

@app.route("/about")
def about():
    return render_template_string(about_template, title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in', 'success')
            return redirect(url_for('login'))
        except:
            flash('Username or email already exists', 'danger')
    
    return render_template_string(register_template, title='Register')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            flash('You have been logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    
    return render_template_string(login_template, title='Login')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        if 'picture' in request.files:
            file = request.files['picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_ext = filename.rsplit('.', 1)[1].lower()
                filename = f"{current_user.username}_profile.{file_ext}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                current_user.image_file = filename
                
        username = request.form.get('username')
        email = request.form.get('email')
        
        if username != current_user.username:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists', 'danger')
                return redirect(url_for('account'))
            current_user.username = username
        
        if email != current_user.email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash('Email already exists', 'danger')
                return redirect(url_for('account'))
            current_user.email = email
        
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    
    return render_template_string(account_template, title='Account')

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        post = Post(title=title, content=content, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template_string(create_post_template, title='New Post')

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template_string(post_template, title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    
    return render_template_string(create_post_template, title='Update Post', post=post)

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template_string(user_posts_template, posts=posts, user=user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create uploads directory if it doesn't exist
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)