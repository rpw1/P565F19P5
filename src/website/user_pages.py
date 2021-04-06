from flask import Flask, Blueprint, redirect, url_for, render_template, request, flash, Markup
from flask_login import login_required, current_user
from src.database.user_database import UserDatabase
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from .models import User
from src.database.content_database import ContentDatabase
from src.buckets.content_bucket import ContentBucket
from src.buckets.metrics_bucket import MetricsBucket
import uuid, os, shutil
from datetime import datetime, timedelta, date
from decouple import config
from src.database.scan_tables import ScanTables
from iso3166 import countries_by_alpha2
from src.database.progress_tracking_database import ProgressTrackingDatabase

users = Blueprint("users", __name__)
user_db = UserDatabase()
content_db = ContentDatabase()
content_bucket = ContentBucket()
metrics_bucket = MetricsBucket()
scan_tb = ScanTables()
progress_db = ProgressTrackingDatabase()
roles = ['client', 'fitness_professional', 'admin']


@users.route("/user/<id>", methods = ["GET", "POST"])
@login_required
def user_page(id):
    user_values = user_db.query_user(id)
    if user_values != None:
        current_user_values = user_db.query_user(current_user.get_id())
        uploads = content_db.query_content_by_user(id)
        subscribed_to = []
        subscriber_count = 0
        if current_user_values['content'] and current_user.role != roles[2]:
            if 'subscribed_accounts' in current_user_values['content']:
                subscribed_to = current_user_values['content']['subscribed_accounts']
        if 'subscribers' in user_values['content']:
            if user_values['role'] == roles[1] and user_values['content'] and user_values['content']['subscribers']:
                subscriber_count = user_values['content']['subscribers']
        subscribed = False
        if id in subscribed_to:
            subscribed = True
        if request.method == "POST":
            action = request.form.get("subscribe")
            if action == "subscribe":
                user_db.subscribe(current_user.email, user_values['email'])
                return redirect(url_for("users.user_page", id=id))
            elif action == "unsubscribe":
                user_db.unsubscribe(current_user.email, user_values['email'])
                return redirect(url_for("users.user_page", id=id))
        if id == current_user.get_id():
            return redirect(url_for("users.profile"))
        user_image = user_values['image']
        specialty = ""
        flag_src = ""
        bio = user_values['bio']
        gender = user_values['gender']
        profile_user = User(
                    user_values['email'], user_values['password'], user_values['first_name'], user_values['last_name'], user_values['role']
                )
        if user_values and user_values['role'] == roles[1]:
            if 'country' in user_values:
                country_info = user_values['country']
                if 'flag' in country_info:
                    flag_src = country_info['flag']
            if 'specialty' in user_values:
                specialty = user_values['specialty']
    else:
        flash("That user does not exist!", category="error")
        return redirect(url_for("views.home"))
    return render_template("profile.html", user=profile_user, user_image = user_image, uploads=uploads,
                specialty = specialty, gender = gender, bio = bio, flag_src = flag_src,
                countries=dict(), country_codes=list(), length=0, subscribed=subscribed, subscriber_count=subscriber_count)


@users.route("/update_password", methods=["GET","POST"])
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


@users.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_email = current_user.get_id()
    subscriber_list = user_db.scan_for_subscribers(current_user.email)
    if request.method == "POST":
        bio = request.form.get("bio")
        if bio != "":
            user_db._update_bio(user_email, bio, current_user.get_role())
        if current_user.get_role() == roles[1]:
            country_code = request.form.get("country")
            gender = request.form.get("gender")
            specialty = request.form.get("specialty")
            # info on flags found on https://flagpedia.net/download/api
            if country_code != "":
                chosen_country = countries_by_alpha2[country_code]
                country_info = {
                    "code": country_code,
                    "name": chosen_country[0],
                    "flag": "https://flagcdn.com/16x12/" + country_code.lower() + ".png"
                }
                user_db.update_fitness_professional_country(user_email, country_info)
            if specialty != "":
                user_db.update_fitness_professional_specialty(user_email, specialty)
            if gender != "":
                user_db.update_fitness_professional_gender(user_email, gender)
        flash("Successfully edited profile!", category="success")
        return redirect(url_for("users.profile"))
    user_values = user_db.query_user(user_email)
    subscriber_count = 0
    if 'subscribers' in user_values['content']:
        if user_values['role'] == roles[1] and user_values['content'] and user_values['content']['subscribers']:
            subscriber_count = user_values['content']['subscribers']
    user_image = user_values['image']
    flag_src = ""
    country_name = ""
    bio = user_values['bio']
    specialty = ""
    gender = user_values['gender']
    uploads = []
    pending = []
    subscriptions = []
    subscriptions_count = 0
    subscription_emails = []
    if 'subscribed_accounts' in user_values['content']:
        subscription_emails = user_values['content']['subscribed_accounts']
        for subscription in subscription_emails:
            subscriptions.append(user_db.query_user(subscription))
    subscriptions_count = len(subscription_emails)
    if user_values['role'] == roles[1]:
        uploads = content_db.query_content_by_user(user_email)
        pending = content_db.query_unapproved_content_by_user(user_email)
        if 'country' in user_values:
            if user_values['country']:
                country_info = user_values['country']
                country_name = country_info['code']
                if 'flag' in country_info:
                    flag_src = country_info['flag']
        if 'specialty' in user_values:
            specialty = user_values['specialty']
    country_codes = list(countries_by_alpha2.keys())
    return render_template("profile.html", user=current_user, user_image=user_image, 
        uploads=uploads, countries=countries_by_alpha2, country_codes=country_codes, length=len(country_codes),
        specialty = specialty, gender = gender, bio = bio, flag_src = flag_src, country_name=country_name, subscriber_count=subscriber_count, 
        subscriber_list=subscriber_list, pending=pending, subscriptions=subscriptions, subscriptions_count=subscriptions_count)