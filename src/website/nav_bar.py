from flask import Flask, Blueprint, redirect, url_for, render_template, request, flash, Markup
from flask_login import login_required, current_user
from src.database.user_database import UserDatabase
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from .models import User
from src.database.content_database import ContentDatabase
from src.database.messages_database import MessagesDatabase
from src.buckets.content_bucket import ContentBucket
from src.buckets.metrics_bucket import MetricsBucket
import uuid, os, shutil
from datetime import datetime, timedelta, date
from decouple import config
from src.database.scan_tables import ScanTables
from iso3166 import countries_by_alpha2
from src.database.progress_tracking_database import ProgressTrackingDatabase

nav_bar = Blueprint("nav_bar", __name__)
user_db = UserDatabase()
content_db = ContentDatabase()
messages_db = MessagesDatabase()
content_bucket = ContentBucket()
metrics_bucket = MetricsBucket()
scan_tb = ScanTables()
progress_db = ProgressTrackingDatabase()
roles = ['client', 'fitness_professional', 'admin']


def add_notification(email, message, reason = ""):
    message = str(message).replace("<b>", "").replace("</b>", "")
    user = user_db.query_user(email)
    notification_id = str(uuid.uuid4())
    now = datetime.now()
    user_content = user['content']
    if 'notification' not in user_content:
        user_content['notification'] = dict()
    if 'len' not in user_content['notification']:
        user_content['notification']['len'] = 0
    user_content['notification']['len'] += 1
    user_content['notification'][notification_id] = {
        'time_stamp': now.strftime("%m/%d/%Y %H:%M:%S"),
        'has_read': False,
        'message': message,
        'reason': reason
    }
    user_db.query_update_content(user['email'], user_content)

def delete_notification(email, notification_id):
    user = user_db.query_user(email)
    user_content = user['content']
    del user_content['notification'][notification_id]
    user_content['notification']['len'] -= 1
    user_db.query_update_content(user['email'], user_content)

@nav_bar.route("/notifs", methods=['GET', 'POST'])
@login_required
def notifications():
    #messages_db.insert_conversation(str(uuid.uuid4()), 'testuser@iu.edu', 'testprof@iu.edu', 'hello')
    #messages_db.delete_conversation('2ad62398-4c8f-49fe-8d7e-40a8a73da0f3')
    if request.method == 'POST':
        notification_id = request.form['id']
        delete_notification(current_user.email, notification_id)
    user = user_db.query_user(current_user.get_id())
    if 'notification' not in user['content']:
        notifications = dict()
    else:
        notifications = user['content']['notification']
    return render_template("notification.html", notifications = notifications)


@nav_bar.route("/moderate", methods=["GET","POST"])
@login_required
def moderate():
    if current_user.role == 'admin':
        unapproved = content_db.query_content_unapproved()
        print(unapproved)
        if request.method == "POST":
            action = request.form.get("moderate")
            content_id = request.form.get("content_id")
            email = request.form.get("email")
            title = request.form.get("title")
            uploader = user_db.get_fitness_professional(email)
            if action == "approve":
                message = Markup("<b>{}</b> approved!".format(title))
                notification_message = Markup("Your content, <a href='/content/{}' target='_blank'>{}</a>, was approved!".format(content_id, title))
                content_db.update_approval(content_id, email, True)
                add_notification(email, notification_message)
                subscriber_list = user_db.scan_for_subscribers(email)
                for subscriber in subscriber_list:
                    notification_message = Markup("{} {} just uploaded {}. <a href='/content/{}' target='_blank'>Go check it out now!</a>").format(uploader['first_name'], uploader['last_name'], title, content_id)
                    add_notification(subscriber['email'], notification_message)
                flash(message, category="success")
                return redirect(url_for("nav_bar.moderate"))
            elif action == "delete":
                reason = request.form.get("reason")
                content_db.delete_content(content_id, email)
                message = Markup("<b>{}</b> deleted for reason: {}".format(title, reason))
                notification_message = Markup("{} was deleted for reason: {}".format(title, reason))
                add_notification(email, notification_message)
                flash(message, category="error")
                return redirect(url_for("nav_bar.moderate"))
        return render_template("moderate.html", unapproved=unapproved)
    else:
        flash("You do not have permission to access that page!", category="error")
        return redirect(url_for("views.home"))


@nav_bar.route("/search", methods=["GET","POST"])
@login_required
def search():
    if request.method == "POST":
        query = request.form.get("search")
        if query == "" or query == None:
            flash("Query cannot be empty!", category="error")
            return render_template("search.html", query="", results=list(), results_len=0, item_len = 0)
        type_filter = ['users', 'content']
        gender_filters = ['male', 'female', 'non_binary', 'prefer']
        date_filters_temp = ['today', 'week', 'month', 'year']
        date_filters = date_filters_temp[::-1]
        instruction_filters = ['video', 'diet_plan', 'workout_plan']
        workout_type_filters = ['home', 'gym', 'fitness_center', 'track']
        user_filters = {
            "gender": gender_filters
            }
        content_filters = {
            "date": date_filters, 
            "mode_of_instruction": instruction_filters, 
            "workout_type": workout_type_filters
        }
        users_val = request.form.get('users')
        content_val = request.form.get('content')
        for key, items in user_filters.items():
            temp_list = []
            for uf in items:
                if request.form.get(uf):
                    users_val = True
                    temp_list.append(uf)
            user_filters[key] = temp_list
        
        for key, items in content_filters.items():
            temp_list = []
            for cf in items:
                if request.form.get(cf):
                    content_val = True
                    temp_list.append(cf)
            content_filters[key] = temp_list
        
        if users_val and not content_val:
            results = scan_tb.full_scan(query, user_filters, None)
        elif not users_val and content_val:
            results = scan_tb.full_scan(query, None, content_filters)
        else:
            results = scan_tb.full_scan(query, user_filters, content_filters)
        query_results = []
        for item in results:
            item_group = []
            if "@" in item:
                current_user = user_db.query_user(item)
                item_group.append(current_user['first_name'] + " " + current_user['last_name'])
                item_group.append(current_user['username'])
                if 'country' in current_user and 'name' in current_user['country']:
                    item_group.append(current_user['country']['name'])
                else:
                    item_group.append("")
                item_group.append(current_user['gender'])
                if 'specialty' in current_user:
                    item_group.append(current_user['specialty'])
                else:
                    item_group.append("")
                item_group.append(current_user['image'])
                item_group.append(url_for("users.user_page", id = item))
            else:
                current_content = content_db.query_content_by_id(item)
                item_content = current_content['content']
                item_group.append(item_content['title'])
                item_group.append(item_content['mode_of_instruction'])
                item_group.append(item_content['workout_type'])
                item_group.append(item_content['date'])
                item_group.append("")
                item_group.append(item_content['bucket_info']['thumbnail_link'])
                item_group.append(url_for("views.content", id = item))
            query_results.append(item_group)
        if len(query_results) != 0:
            return render_template("search.html", query=query, results=query_results, results_len=len(query_results), item_len = len(query_results[0]))
        else:
            return render_template("search.html", query=query, results=list(), results_len=0, item_len = 0)

@nav_bar.route("/conversation/<id>", methods=["GET", "POST"])
@login_required
def conversation(id):
    if request.method == "POST":
        messages_db.add_message(id, current_user.email, 'hellooo')
    conversation = messages_db.get_conversation_by_id(id)
    print(conversation[0])
    return render_template("conversation.html", id=id, conversation=conversation[0])