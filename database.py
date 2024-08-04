from flask import Flask, request
import os
from flask_admin import Admin
from flask_admin.form.upload import FileUploadField
from flask_admin.contrib.sqla import ModelView
from wtforms.fields import SelectField
from flask_admin.form import Select2Widget
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
from wtforms.fields import FileField

app = Flask(__name__)

# CONFIGURATIONS
app.config['SECRET_KEY'] = 'your_secret_key'  # secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmproject.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['IMAGE_FOLDER']= 'img'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx','jpg','png'}  # Allowed file extensions

db = SQLAlchemy(app)

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['IMAGE_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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






def save_file_local(file,file_path):
    if file and file.filename and file_path:
            if True:
                filename = secure_filename(file.filename)
                file_path = file_path
                try:
                    file.save(file_path)           
                except Exception as e:
                    print(f"Error saving file: {e}")
            else:
               print("Invalid file type.")
    else:
        print("No file selected.")

# For DOCUMENTS in Flask-Admin
class DocumentView(ModelView):
    column_list = ['id', 'document_filename']
    form_overrides = {'document_filename': FileField}
    
    column_labels = {
        'document_filename': 'Upload Document  here',
      
    }

    # THIS CUSTOM MODEL FOR CUSTOM FORM FOR CATEGORIES

    def scaffold_form(self):
        form_class = super(DocumentView, self).scaffold_form()
        form_class.category_id = SelectField('Category', widget=Select2Widget())
        return form_class

    def edit_form(self, obj=None):
        form = super(DocumentView, self).edit_form(obj)
        form.category_id.choices = [(c.c_id, c.category) for c in Category.query.all()]
        return form

    def create_form(self, obj=None):
        form = super(DocumentView, self).create_form(obj)
        categories = [(c.c_id, c.category) for c in Category.query.all()]

        if categories:
            form.category_id.choices = categories
        else:
            # Provide a single choice with a placeholder message
            form.category_id.choices =[]
            
        return form

    def on_model_change(self, form, model, is_created):
        # Handle file upload and save file locally
        file = request.files.get('document_filename')
        if file and file.filename:
            file_path= os.path.join('static',app.config['UPLOAD_FOLDER'], file.filename)
            save_file_local(file,file_path)
            
    def on_model_delete(self, model):
        try:
      
            file_path = os.path.join('static',app.config['UPLOAD_FOLDER'], model.document_filename)
            
            # Delete the file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
         
        except Exception as e:
            print(f"Error deleting file: {e}")







# CUSTOM PAGE INFORMATION VIEW
class PageInformationView(ModelView):
    form_overrides = {
        'profile_url': FileField,
        'about_me_url': FileField
    }
   

    def on_model_change(self, form, model, is_created):
        file = request.files.get('profile_url')

        def save(file):
   
            if file and file.filename:
                file_path = os.path.join('static',app.config['UPLOAD_FOLDER'], file.filename)
                model.profile_url=file.filename
                model.about_me_url=file.filename
                save_file_local(file,file_path)
                filename = secure_filename(file.filename)
        save(file)
    def on_model_delete(self, model):
        try:
      
            file_path = os.path.join('static',app.config['UPLOAD_FOLDER'], model.document_filename)
            
            # Delete the file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
         
        except Exception as e:
            print(f"Error deleting file: {e}")
            
            
       
            





