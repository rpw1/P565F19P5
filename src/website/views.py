from flask import Flask, Blueprint, redirect, url_for, render_template, request, flash, Markup
from flask_login import login_required, current_user
from src.database.user_database import UserDatabase
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from .models import User
from src.database.content_database import ContentDatabase
from src.buckets.content_bucket import ContentBucket
import uuid, os, shutil
from datetime import date
from decouple import config

views = Blueprint("views", __name__)
user_db = UserDatabase()
content_db = ContentDatabase()
content_bucket = ContentBucket()
roles = ['client', 'fitness_professional', 'admin']

@views.route("/")
#@login_required
def home():
    if current_user.is_authenticated:
        total_users = user_db.get_user_count()
        total_content = content_db.get_content_count()
        return render_template("dashboard.html", user=current_user, total_users=total_users, total_content=total_content)
    else: 
        return render_template("landing.html")

@views.route("/profile")
@login_required
def profile():
    user_values = user_db.query_user(current_user.get_id())
    user_image = user_values['image']
    return render_template("profile.html", user=current_user, user_image = user_image)

@views.route("/calendar")
@login_required
def calendar():
    return render_template("calendar.html", user=current_user)
    
@views.route("/user/<id>")
@login_required
def user_page(id):
    user_values = user_db.query_user(id)
    if user_values:
        user_image = user_values['image']
        profile_user = User(
                user_values['email'], user_values['password'], user_values['first_name'], user_values['last_name'], user_values['role']
                )
        return render_template("profile.html", user=profile_user, user_image = user_image)
    else:
        flash("That user does not exist!", category="error")
        return redirect(url_for("views.home"))

@views.route("/content/<id>")
@login_required
def content(id):
    query_content = content_db.query_content_by_id(id)
    if query_content:
        if 'content' in query_content:
            current_content = query_content['content']
            title = current_content['title']
            description = current_content['description']
            thumbnail_link, content_link = content_bucket.get_file_link(current_content['bucket_info'])
            content_type = current_content['content_type']
            content_date = current_content['date']
            created_user = query_content['email']
            user_path = url_for("views.user_page", id = created_user)
            return render_template("content.html", created_user = created_user, title = title, description = description, 
                content_link = content_link, content_date = content_date, user_path = user_page, content_type = content_type)
    flash("Content did not show correctly", category="error")
    return redirect(url_for("views.home"))

@views.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == "POST":
        try:
            os.mkdir(config('UPLOAD_FOLDER'))
        except Exception as e:
            print('Failed to create folder %s. Reason: %s' % (config('UPLOAD_FOLDER'), e))
        content_file_name = None
        thumbnail_name = None
        if 'content_file' in request.files:
            content_file = request.files['content_file']
            if content_file != '':
                content_file_name = secure_filename(content_file.filename)
                content_file_path = os.path.join(config('UPLOAD_FOLDER'), content_file_name)
                content_file.save(content_file_path)
            else:
                flash("Contetnt file was not uploaded successfully", category="error")
                return render_template("upload.html")
        else:
            flash("Contetnt file was not uploaded successfully", category="error")
            return render_template("upload.html")

        if 'thumbnail' in request.files:
            thumbnail = request.files['thumbnail']
            if thumbnail != '':
                thumbnail_name = secure_filename(thumbnail.filename)
                thumbnail_path = os.path.join(config('UPLOAD_FOLDER'), thumbnail_name)
                thumbnail.save(thumbnail_path)
            else:
                flash("Contetnt file was not uploaded successfully", category="error")
                return render_template("upload.html")
        else:
            flash("Contetnt file was not uploaded successfully", category="error")
            return render_template("upload.html")
                
        content_id = str(uuid.uuid4())
        email = current_user.get_id()
        active_user = user_db.get_fitness_professional(email)
        if active_user:
            old_content = active_user['content']
            if 'user_content' in old_content:
                videos = old_content['user_content']
                videos.append(content_id)
                old_content['user_content'] = videos
            else:
                old_content['user_content'] = [content_id]
            title = request.form.get("title")
            content_type_val = int(request.form.get("ContentType"))
            content_type = ""
            if content_type_val == 1:
                content_type = 'image/*'
            elif content_type_val == 2:
                content_type = 'application/pdf'
            else:
                content_type = 'video/mp4'
            user_db.update_fitness_professional_content(email, old_content)
            description = request.form.get("description")
            current_date = date.today().strftime("%m/%d/%Y")
            bucket_info = content_bucket.add_file(content_id, email, content_file_name, thumbnail_name, content_type)
            try:
                shutil.rmtree(config('UPLOAD_FOLDER'))
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (config('UPLOAD_FOLDER'), e))
            uploaded_content = {
                "title": title,
                "content_type": content_type,
                "description": description,
                "date": current_date,
                "bucket_info": bucket_info,
                "amount_viewed": 0
            }
            content_db.insert_content(content_id, email, uploaded_content)
            flash("Upload successful")
            return redirect(url_for("views.content", id = content_id))
        else:
            flash("You do not have permission to upload content")
            return redirect(url_for("views.home"))
    return render_template("upload.html")

@views.route("/update_password", methods=["GET","POST"])
@login_required
def update_password():
    if request.method == "POST":
        new_password = request.form.get("password")
        confirm = request.form.get("confirm")
        email = current_user.get_id()
        password = generate_password_hash(new_password, method="sha256")
        if new_password != confirm:
            flash("Password must equal confirmation", category="error")
        else:
            user_db.update_client_password(email, password)
            flash("Password successfully changed!", category="success")
    return render_template("update_password.html", user=current_user)


@views.route("/progress_tracking", methods=["GET","POST"])
@login_required
def progress_tracking():
    if request.method == "POST_1":
        legend = 'Calories'
        temperatures = [10.2, 3.2, 69]
        times = ['Monday', 'Tuesaday', 'Wed']
        return render_template('progress_tracking.html', values=temperatures, labels=times, legend=legend, user=current_user)
    return render_template('progress_tracking.html', user=current_user)

@views.route("/search", methods=["GET","POST"])
@login_required
def search():
    #if request.method == "POST":
        query = request.form.get("search")
        if query == "":
            flash("Query cannot be empty!", category="error")
            return redirect(request.referrer)
        return redirect(url_for("views.search_query", query=query, page=1))
        #users = user_db.search_user_by_email(query)
        #if users:
         #   users_len = len(users)
         #   return render_template("search.html", query=query, users=users, users_len = users_len)
        #else:
         #   flash("Query had no results", category="error")
          #  return redirect(url_for("views.home"))
    #else:
     #   flash("You must search using the search bar!", category="error")
      #  return redirect(url_for("views.home"))

@views.route("/search/<query>/<page>")
@login_required
def search_query(query, page):
    return render_template("search.html", query=query, users=[], users_len=0)

@views.route("/moderate", methods=["GET","POST"])
@login_required
def moderate():
    if current_user.role == 'admin':
        if request.method == "POST":
            action = request.form.get("moderate")
            content_id = request.form.get("content_id")
            if action == "approve":
                message = Markup("<b>Content Title</b> approved!")
                flash(message, category="success")
            else:
                message = Markup("<b>Content Title</b> deleted")
                flash(message, category="error")
        return render_template("moderate.html")
    else:
        flash("You do not have permission to access that page!", category="error")
        return redirect(url_for("views.home"))

@views.route("/messages")
@login_required
def messages():
    #get a list of all conversations user is involved in
    #all senders are clients, so we can check the user's role to see what fields to look for
    #pass that list of conversations to the template
    return render_template("messages.html")