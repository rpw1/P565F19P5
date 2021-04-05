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

views = Blueprint("views", __name__)
user_db = UserDatabase()
content_db = ContentDatabase()
content_bucket = ContentBucket()
metrics_bucket = MetricsBucket()
scan_tb = ScanTables()
progress_db = ProgressTrackingDatabase()
roles = ['client', 'fitness_professional', 'admin']

@views.route("/")
def home():
    if current_user.is_authenticated:
        total_users = user_db.get_user_count()
        todays_date = datetime.now()
        uploaded_today_approved = []
        uploaded_today_count = 0
        type_count = [user_db.get_trainee_count(), user_db.get_trainer_count(), user_db.get_admin_count()]
        all_content = content_db.scan_everything()
        total_content = len(all_content)
        diet_plans = []
        workout_plans = []
        fitness_videos = []
        calories = ""
        email = current_user.get_id()
        try :
            content = progress_db.query_user(email)
            calories = content['content']['weekly_cals']
            print(calories)
        except:
            weekly_cals = "0,0,0,0,0,0,0"
            base_content = {
                "weekly_cals": weekly_cals
            }
            progress_db.insert_content(email,base_content)
            progress_db.query_user(email)
            content = progress_db.query_user(email)
            calories = content['content']['weekly_cals']   
        for current_content in all_content:
            item_content = current_content['content']
            uploaded_date = datetime.strptime(item_content['date'], "%m/%d/%Y")
            if (todays_date - timedelta(days=1)) <= uploaded_date:
                uploaded_today_count += 1
                if current_content['approved']:
                    uploaded_today_approved.append(current_content)
                else:
                    continue
            if item_content['mode_of_instruction'] == 'Diet plan' and current_content['approved']:
                diet_plans.append(current_content)
            elif item_content['mode_of_instruction'] == 'Workout plan' and current_content['approved']:
                workout_plans.append(current_content)
            elif item_content['mode_of_instruction'] == 'Video' and current_content['approved']:
                fitness_videos.append(current_content)
        user_values = user_db.query_user(email)
        subscribed_content = []
        if 'subscribed_accounts' in user_values['content']:
            subscribed_accounts = user_values['content']['subscribed_accounts']
            for account in subscribed_accounts:
                subscribed_content.extend(content_db.scan_content_by_email(account))
        todays_views = metrics_bucket.get_todays_views()
        total_views = metrics_bucket.get_total_view_count()
        return render_template("dashboard.html", user=current_user, total_users=total_users, total_content=total_content, 
            uploaded_today=uploaded_today_approved, type_count=type_count, subscribed_content=subscribed_content,
            diet_plans=diet_plans, workout_plans=workout_plans, fitness_videos=fitness_videos, uploaded_today_len=uploaded_today_count, 
            calories=calories, todays_views=todays_views, total_views = total_views)
    else: 
        return render_template("landing.html")

@views.route("/profile", methods=["GET", "POST"])
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
        return redirect(url_for("views.profile"))
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

@views.route("/calendar", methods=["GET","POST"])
@login_required
def calendar():
    if request.method == 'POST':
        print("In Post method")
        data = request.data
        print(data)
        print(type(data))
        if data: 
            print(data['workout_data'])
        pass
    return render_template("calendar.html", user=current_user, post_url = url_for('views.calendar'))
    
@views.route("/user/<id>", methods = ["GET", "POST"])
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
                return redirect(url_for("views.user_page", id=id))
            elif action == "unsubscribe":
                user_db.unsubscribe(current_user.email, user_values['email'])
                return redirect(url_for("views.user_page", id=id))
        if id == current_user.get_id():
            return redirect(url_for("views.profile"))
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

@views.route("/content/<id>", methods=["GET","POST"])
@login_required
def content(id):
    if request.method == "POST":
        has_editted = request.form.get("edit_val")
        print(has_editted)
        action = request.form.get("moderate")
        title = request.form.get("title")
        email = request.form.get("email")
        if action == "delete":
            content_db.delete_content(id, email)
            message = Markup("<b>{}</b> successfully deleted".format(title))
            flash(message, category="success")
            return redirect(url_for("views.home"))
        elif has_editted == "edit_val":
            print("here")
            query_content = content_db.query_content_by_id(id)
            title = request.form.get("edit_title")
            description = request.form.get("edit_description")
            mode_of_instruction = request.form.get("edit_mode_of_instruction")
            workout_type = request.form.get("edit_workout_type")
            query_content['content']['title'] = title
            query_content['content']['description'] = description
            query_content['content']['mode_of_instruction'] = mode_of_instruction
            query_content['content']['workout_type'] = workout_type
            content_db.update_content(id, query_content['email'], query_content['content'])
            message = Markup("<b>{}</b> successfully updated".format(title))
            flash(message, category="success")
            return redirect(url_for("views.content", id = id))
    query_content = content_db.query_content_by_id(id)
    content_email = query_content['email']
    content_user = user_db.get_fitness_professional(content_email)
    total_views = 0
    has_editted = request

    if 'total_views' in content_user['content']:
        total_views = content_user['content']['total_views']
    user_email = current_user.get_id()
    if query_content:
        if 'content' in query_content:
            current_content = query_content['content']
            if 'views' in current_content:
                views = current_content['views']
                if user_email not in views:
                    views.append(user_email)
                    current_content['views'] = views
                    total_views += 1
                    metrics_bucket.add_daily_view()
            else:
                current_content['views'] = [user_email]
                total_views += 1
                metrics_bucket.add_daily_view()
            metrics_bucket.check_most_viewed_content(id, len(current_content['views']))
            content_db.update_content(id, content_email, current_content)
            approved = query_content['approved']
            content_user['content']['total_views'] = total_views
            metrics_bucket.check_most_viewed_user(content_email, int(total_views))
            user_db.update_fitness_professional_content(content_email, content_user['content'])
            view_count = len(current_content['views'])
            title = current_content['title']
            description = current_content['description']
            thumbnail_link, content_link = content_bucket.get_file_link(current_content['bucket_info'])
            content_type = current_content['content_type']
            content_date = current_content['date']
            workout_type = current_content['workout_type']
            mode_of_instruction = current_content['mode_of_instruction']
            created_user = query_content['email']
            user_path = url_for("views.user_page", id = created_user)
            return render_template("content.html", created_user = created_user, title = title, description = description, 
                content_link = content_link, content_date = content_date, user_path = user_page, content_type = content_type, view_count=view_count, approved=approved,
                mode_of_instruction=mode_of_instruction, workout_type=workout_type)
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
                flash("Content file was not uploaded successfully", category="error")
                return render_template("upload.html")
        else:
            flash("Content file was not uploaded successfully", category="error")
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
            moi = request.form.get("Instruction")
            workout_type = request.form.get("WorkoutType")
            bucket_info = content_bucket.add_file(content_id, email, content_file_name, thumbnail_name, content_type)
            try:
                shutil.rmtree(config('UPLOAD_FOLDER'))
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (config('UPLOAD_FOLDER'), e))
            uploaded_content = {
                "title": title,
                "content_type": content_type,
                "workout_type": workout_type,
                "mode_of_instruction": moi,
                "description": description,
                "date": current_date,
                "bucket_info": bucket_info,
                "amount_viewed": 0
            }
            content_db.insert_content(content_id, email, uploaded_content)
            flash("Upload successful!", category="success")
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
    now = datetime.now()
    today = date.today()
    weekday = datetime.today().strftime('%A')
    wk = today.isocalendar()[1]
    todays_date = today
    email = current_user.get_id()
    calories = ""
    weekly_calorie_goal= ""
    weekly_calorie_total= ""
    calorie_string = ""
    last_reset = ""
    try :
        progress_db.query_user(email)
        content = progress_db.query_user(email)
        calories = content['content']['weekly_cals']
        weekly_calorie_goal= content['content']['weekly_calorie_goal']
        weekly_calorie_total= content['content']['weekly_calorie_total']
        last_reset = str(content['content']['last_reset'])
    except:
        weekly_cals = "0,0,0,0,0,0,0"
        weekly_calorie_goal = "0"
        weekly_calorie_total = "0"
        last_reset = str(now)
        base_content = {
            "weekly_cals": weekly_cals,
            "weekly_calorie_goal": weekly_calorie_goal,
            "weekly_calorie_total": weekly_calorie_total,
            "last_reset": last_reset
        }
        progress_db.insert_content(email,base_content)
        progress_db.query_user(email)
        content = progress_db.query_user(email)
        calories = content['content']['weekly_cals']   
        weekly_calorie_goal= content['content']['weekly_calorie_goal']
        weekly_calorie_total= content['content']['weekly_calorie_total']
        last_reset = str(content['content']['last_reset'])
    print(last_reset)
    if (str(last_reset).startswith(str(today)) == False) and weekday == "Monday":
        weekly_cals = "0,0,0,0,0,0,0"
        weekly_calorie_goal = "0"
        weekly_calorie_total = "0"
        last_reset = str(now)
        base_content = {
            "weekly_cals": weekly_cals,
            "weekly_calorie_goal": weekly_calorie_goal,
            "weekly_calorie_total": weekly_calorie_total,
            "last_reset": last_reset
        }
        progress_db.insert_content(email,base_content)
        progress_db.query_user(email)
        content = progress_db.query_user(email)
        calories = content['content']['weekly_cals']   
        weekly_calorie_goal= content['content']['weekly_calorie_goal']
        weekly_calorie_total= content['content']['weekly_calorie_total']
        last_reset = str(content['content']['last_reset'])
        print("shouldnt start with today")
   
    if(weekly_calorie_goal == "0"):
        calorie_string = "Try setting a weekly calorie goal!"
    elif(int(weekly_calorie_goal)<=int(weekly_calorie_total)):
        calorie_string = "Congrats! You reached your goal!"
    elif(int(weekly_calorie_goal)*(3/4)<=int(weekly_calorie_total)):
        calorie_string = "Almost there! Keep Going!"
    elif(int(weekly_calorie_goal)*(1/2)<=int(weekly_calorie_total)):
        calorie_string = "You're over halfway to your goal!"
    else:
        calorie_string = "Log more calories to meet your goal!"

    if request.method == "POST":
        action = request.form.get("progress")
        print(action)
        if action == "add_cals":
            split = calories.split(",")
            day_of_week = request.form.get("day_of_week")
            new_cals = request.form.get("calories")
            print(day_of_week)
            print(new_cals)
            print(split[0])
            weekly_calorie_total = int(weekly_calorie_total) + int(new_cals)
            if(day_of_week == "Monday"):
                updates_cals = int(split[0]) + int(new_cals)
                split[0] = str(updates_cals)
            elif(day_of_week == "Tuesday"):
                updates_cals = int(split[1]) + int(new_cals)
                split[1] = str(updates_cals)
            elif(day_of_week == "Wednesday"):
                updates_cals = int(split[2]) + int(new_cals)
                split[2] = str(updates_cals)
            elif(day_of_week == "Thursday"):
                updates_cals = int(split[3]) + int(new_cals)
                split[3] = str(updates_cals)
            elif(day_of_week == "Friday"):
                updates_cals = int(split[4]) + int(new_cals)
                split[4] = str(updates_cals)
            elif(day_of_week == "Saturday"):
                updates_cals = int(split[5]) + int(new_cals)
                split[5] = str(updates_cals)
            elif(day_of_week == "Sunday"):
                updates_cals = int(split[6]) + int(new_cals)
                split[6] = str(updates_cals)
            calories = ""
            i=0
            for x in split:
                if(i==7):
                    calories = calories + x
                else:
                    calories = calories + x + ","
                i = i+1
            print(calories)
            base_content = {
                "weekly_cals": calories,
                "weekly_calorie_goal": weekly_calorie_goal,
                "weekly_calorie_total": weekly_calorie_total,
                "last_reset": last_reset
            }
            progress_db.insert_content(email,base_content)
            if(weekly_calorie_goal == "0"):
                calorie_string = "Try setting a weekly calorie goal!"
            elif(int(weekly_calorie_goal)<=int(weekly_calorie_total)):
                calorie_string = "Congrats! You reached your goal!"
            elif(int(weekly_calorie_goal)*(3/4)<=int(weekly_calorie_total)):
                calorie_string = "Almost there! Keep Going!"
            elif(int(weekly_calorie_goal)*(1/2)<=int(weekly_calorie_total)):
                calorie_string = "You're over halfway to your goal!"
            else:
                calorie_string = "Log more calories to meet your goal!"
        elif action == "add_goal":
            calorie_goal = request.form.get("calorie_goal")
            try:
                weekly_calorie_goal = int(calorie_goal)
                if(weekly_calorie_goal >= 0):
                    base_content = {
                        "weekly_cals": calories,
                        "weekly_calorie_goal": weekly_calorie_goal,
                        "weekly_calorie_total": weekly_calorie_total,
                        "last_reset": last_reset
                    }
                    progress_db.insert_content(email,base_content)
                    if(weekly_calorie_goal == "0"):
                        calorie_string = "Try setting a weekly calorie goal!"
                    elif(int(weekly_calorie_goal)<=int(weekly_calorie_total)):
                        calorie_string = "Congrats! You reached your goal!"
                    elif(int(weekly_calorie_goal)*(3/4)<=int(weekly_calorie_total)):
                        calorie_string = "Almost there! Keep Going!"
                    elif(int(weekly_calorie_goal)*(1/2)<=int(weekly_calorie_total)):
                        calorie_string = "You're over halfway to your goal!"
                    else:
                        calorie_string = "Log more calories to meet your goal!" 
                else:
                    flash("Please enter a positive whole number", category="error")
            except:
                flash("Please enter a whole number", category="error")
        return render_template('progress_tracking.html', user=current_user, todays_date = todays_date, calories = calories, calorie_string= calorie_string, calorie_goal = weekly_calorie_goal, calorie_total = weekly_calorie_total)
    return render_template('progress_tracking.html', user=current_user, todays_date = todays_date, calories = calories, calorie_string= calorie_string, calorie_goal = weekly_calorie_goal, calorie_total = weekly_calorie_total)

@views.route("/search", methods=["GET","POST"])
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
                item_group.append(url_for("views.user_page", id = item))
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

@views.route("/moderate", methods=["GET","POST"])
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
                return redirect(url_for("views.moderate"))
            elif action == "delete":
                reason = request.form.get("reason")
                content_db.delete_content(content_id, email)
                message = Markup("<b>{}</b> deleted for reason: {}".format(title, reason))
                notification_message = Markup("{} was deleted for reason: {}".format(title, reason))
                add_notification(email, notification_message)
                flash(message, category="error")
                return redirect(url_for("views.moderate"))
        return render_template("moderate.html", unapproved=unapproved)
    else:
        flash("You do not have permission to access that page!", category="error")
        return redirect(url_for("views.home"))


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

@views.route("/notifs", methods=['GET', 'POST'])
@login_required
def notifications():
    if request.method == 'POST':
        notification_id = request.form['id']
        delete_notification(current_user.email, notification_id)
    user = user_db.query_user(current_user.get_id())
    if 'notification' not in user['content']:
        notifications = dict()
    else:
        notifications = user['content']['notification']
    return render_template("notification.html", notifications = notifications)

@views.route("/messages")
@login_required
def messages():
    #get a list of all conversations user is involved in
    #all senders are clients, so we can check the user's role to see what fields to look for
    #pass that list of conversations to the template
    return render_template("messages.html")