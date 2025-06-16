from flask import Flask, render_template, request, redirect, url_for, flash
import pymongo
import datetime
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri =###
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['addressbook']
contacts_collection = db['contacts']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'safe^&*hdgahksdg'

@app.route('/')
def index():
    contacts = list(contacts_collection.find())
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['POST'])
def add_contact():
    name = request.form.get('name')
    phone = request.form.get('phone')

    # Check if phone number already exists
    if contacts_collection.find_one({'phone': phone}):
        flash('Phone number already exists. Please use a different number.')
        return redirect(url_for('index'))

    if not name or len(name) < 3:
        flash('Name must be at least 3 characters long.')
        return redirect(url_for('index'))
    if "@" not in name and ".com" not in name:
        flash('Email Needed')
        return redirect(url_for('index'))

    if not phone.isdigit():
        flash('Phone number must be numeric.')
        return redirect(url_for('index'))

    contact = {
        "name": name,
        "phone": phone,
        "created_at": datetime.datetime.utcnow()
    }
    contacts_collection.insert_one(contact)

    flash('Contact added successfully!')
    return redirect(url_for('index'))

@app.route('/delete/<contact_id>', methods=['POST'])
def delete_contact(contact_id):
    result = contacts_collection.delete_one({'_id': ObjectId(contact_id)})
    if result.deleted_count > 0:
        flash('Contact deleted successfully!')
    else:
        flash('Contact not found.')

    return redirect(url_for('index'))

@app.route('/contact/<contact_id>', methods=['GET'])
def view_contact(contact_id):
    contact = contacts_collection.find_one({'_id': ObjectId(contact_id)})
    
    if contact:
        return render_template('view_contact.html', contact=contact)
    else:
        flash('Contact not found.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
