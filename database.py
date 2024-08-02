from flask import request, Flask
import os
# ADMIN HANDLER
from flask_admin import Admin
from flask_admin.form.upload import FileUploadField
from flask_admin.contrib.sqla import ModelView

# ADMIN INSIDE FORM EDITORS
from wtforms.fields import SelectField
from flask_admin.form import Select2Widget

# DATABASE HANDLER
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

# CONFIGURATIONS
app.config['SECRET_KEY'] = 'your_secret_key' # secret key
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmproject.db' # db path

app.config['SQLALCHEMY_DATABASE_URI'] ="mysql://rk:rk@localhost/blog"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'  # Temporary upload folder

db = SQLAlchemy(app)

# NOTE : This line help me for temporarily filefieldupload pdf stored and upl to db.
os.makedirs(app.config['UPLOAD_FOLDER'])

# CONTACT MODEL
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

# CATEGORY MODEL
class Category(db.Model):
    c_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(30), unique=True, nullable=False)

    def __repr__(self):
        return f"Category('{self.category}')"

# DOCUMENT MODEL
class Document(db.Model):
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_filename = db.Column(db.String(100), nullable=False)  # Storing original filename
    document = db.Column(db.LargeBinary, nullable=False)  # Storing document content directly
    category_id = db.Column(db.Integer, db.ForeignKey('category.c_id'), nullable=False)
    upl_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category = db.relationship('Category', backref=db.backref('documents', lazy=True))

    def __repr__(self):
        return f"Document('{self.document_filename}', '{self.upl_date}', '{self.category.category}')"
   



# PAGE INFORMATION MODEL
class PageInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    job = db.Column(db.String(100), nullable=False)
    slogan = db.Column(db.Text, nullable=False)
    aboutme = db.Column(db.Text, nullable=False)
    profile_url = db.Column(db.String(255), nullable=False)
    about_me_url = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"PageInformation('{self.name}', '{self.job}')"



# CONTACT INFO MODEL
class ContactInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_name = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"ContactInfo('{self.app_name}', '{self.link}')"
    

# PROFILE ABOUT MODEL
class ProfileAbout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    detail = db.Column(db.Text, nullable=False)


'''
 CUSTOMLY I AM SHOWING 
 ----------------------
'''
class DocumentView(ModelView):
    form_columns = ['document_filename', 'document', 'category']
    form_excluded_columns = ['upl_date']  # Exclude upl_date from form input
    column_editable_list = ['document_filename', 'category']  # Make these fields editable in the list view
    column_searchable_list = ['document_filename']  # Add search functionality if needed

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.upl_date = datetime.utcnow()  #








