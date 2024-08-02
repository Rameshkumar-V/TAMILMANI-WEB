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

app = Flask(__name__)

# CONFIGURATIONS
app.config['SECRET_KEY'] = 'your_secret_key'  # secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmproject.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'  # Temporary upload folder
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx'}  # Allowed file extensions

db = SQLAlchemy(app)

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

# For DOCUMENTS in Flask-Admin
class DocumentView(ModelView):
    form_overrides = {
        'document_filename': FileUploadField
    }
    form_args = {
        'document_filename': {
            'base_path': app.config['UPLOAD_FOLDER']
        }
    }
    column_exclude_list = ['document_filename']
    form_excluded_columns = ['upl_date']  # Exclude upl_date from the form
    # Show document_filename in the view area
    # column_list = ['id', 'document_filename', 'category', 'upl_date']
    column_labels = {
        'document_filename': 'Upload Document  here',
      
    }

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
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    file.save(file_path)  # Save the file to the uploads folder
                    model.document_filename = filename  # Store only the filename in the database
                except Exception as e:
                    # Handle file save errors
                    print(f"Error saving file: {e}")
            else:
                # Handle invalid file type
                print("Invalid file type.")
        else:
            # Handle missing file
            print("No file selected.")

# Admin interface setup
admin = Admin(app, name='MyApp', template_mode='bootstrap3')
admin.add_view(DocumentView(Document, db.session))
# Add more views as needed

if __name__ == '__main__':
    app.run(debug=True)
