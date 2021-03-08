from flask import Flask, Blueprint, redirect, url_for, render_template, request, flash
from flask_login import login_required, current_user
from database.user_database import UserDatabase
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from database.content_database import ContentDatabase
import uuid
from datetime import date

views = Blueprint("views", __name__)
user_db = UserDatabase()
content_db = ContentDatabase()
roles = ['client', 'fitness_professional', 'admin']

@views.route("/")
#@login_required
def home():
    if current_user.is_authenticated:
        return render_template("dashboard.html", user=current_user)
    else: 
        return redirect(url_for("auth.login"))

if __name__ == "__main__":
    app.run(debug=True)

@views.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@views.route("/user/<id>")
@login_required
def user_page(id):
    user_values = user_db.query_user(id)
    if user_values:
        profile_user = User(
                user_values['email'], user_values['password'], user_values['first_name'], user_values['last_name'], user_values['role']
                )
        return render_template("profile.html", user=profile_user)
    else:
        flash("That user does not exist!", category="error")
        return redirect(url_for("views.home"))

@views.route("/content/<id>")
@login_required
def content(id):
    current_content = content_db.query_content_by_id(id)
    if current_content:
        content_type = current_content['content_type']
        if content_type == "video":
            title = current_content['title']
            description = current_content['description']
            video_file = current_content['data']['video_file']
            video_date = current_content['date']
            created_user = current_content['email']
            user_path = url_for("views.user_page/" + created_user)
            return render_template("content.html", created_user = created_user, title = title, description = description, 
                video_file = video_file, video_date = video_date, user_path = user_page)
        elif content_type == "workout_plan":
            flash("Not implemented yet", category="error")
        elif content_type == "diet_plan":
            flash("Not implemented yet", category="error")
    return render_template("content.html", id=id)

@views.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == "POST":
        content_id = uuid.uuid4()
        email = current_user.get_id()
        active_user = user_db.get_fitness_professional(email)
        if active_user:
            old_content = active_user['content']
            if 'videos' in content:
                videos = old_content['videos']
                videos.append(content_id)
            else:
                old_content['videos'] = [content_id]
            active_user.update_fitness_professional_content(email, old_content)
            video_file = request.form.get("video_file")
            thumbnail = request.form.get("thumbnail")
            content_type = request.form.get("content_type")
            title = request.form.get("title")
            description = request.form.get("description")
            current_date = date.today().strftime("%m/%d/%Y")
            video_content = {
                "content_type": content_type,
                "title": title,
                "description": description,
                "thumbnail": thumbnail,
                "date": current_date,
                "data": {
                    "video_file": video_file,
                    "amount_viewed": 0
                }
            }
            content_db.insert_content(content_id, email, video_content)
            flash("Upload successful")
            redirect(url_for("views.home"))
        else:
            flash("You do not have permission to upload content")
            redirect(url_for("views.home"))
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
            user_db.update_password(email, password)
            flash("Password successfully changed!", category="success")
    return render_template("update_password.html", user=current_user)

