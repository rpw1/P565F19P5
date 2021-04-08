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

views = Blueprint("views", __name__)
user_db = UserDatabase()
content_db = ContentDatabase()
messages_db = MessagesDatabase()
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
        custom_workouts = dict()
        if user_values['role'] == 'client':
            client_content = user_values['content']
            if 'current_custom_workout' in client_content and client_content['current_custom_workout']:
                custom_workouts = client_content['current_custom_workout']
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
            calories=calories, todays_views=todays_views, total_views = total_views, custom_workouts=custom_workouts)
    else: 
        return render_template("landing.html")


def delete_custom_workout(delete_workout, client_content):
    """
    This function takes a workout_id and the current client's content and removes the workout from the client and content.
    """
    current_workout = client_content['custom_workout'][delete_workout]
    current_content = content_db.query_content_by_id(current_workout['content_id'])
    if current_content:
        current_content_content = current_content['content']
        if 'workout_plans' not in current_content_content or not current_content_content['workout_plans']:
            current_content_content['workout_plans'] = []
        if delete_workout in current_content_content['workout_plans']:
            current_content_content['workout_plans'] = current_content_content['workout_plans'].remove(delete_workout)
            content_db.update_content(current_content['content_id'], current_content['email'], current_content_content)
    del client_content['custom_workout'][delete_workout]
    del client_content['current_workout_plans'][delete_workout]
    user_db.update_client_content(current_user.get_id(), client_content)
    return client_content['current_custom_workout']

def complete_custom_workout(complete_workout, client_content):
    """
        removes complete_workout's custom workout id from the list of current custom workouts
    """
    del client_content['current_custom_workout'][complete_workout]
    user_db.update_client_content(current_user.get_id(), client_content)
    return client_content['current_custom_workout']

def add_custom_workout(title, description, difficulty, duration, training_type, content_id, client_content):
    url_content = content_db.query_content_by_id(content_id)
    if not url_content and content_id:
        flash("Error: Content ID was incorrect")
        return render_template("calendar.html", user=current_user, isWorkout=True, 
            custom_workouts=client_content['current_custom_workout'])
    else:
        workout_id = str(uuid.uuid4())
        custom_workout = {
            "workout_id": workout_id,
            "title": title,
            "description": description,
            "difficulty": difficulty,
            "duration": duration,
            "training_type": training_type,
            "content_id": content_id,
        }
        client_content['custom_workout'][workout_id] = custom_workout
        client_content['current_custom_workout'][workout_id] = custom_workout
        user_db.update_client_content(current_user.get_id(), client_content)
        if url_content:
            content_url = url_content['content']
            if 'workout_plans' in content_url and content_url['workout_plans']:
                workout_plans = content_url['workout_plans']
                workout_plans.append(workout_id)
                content_url['workout_plans'] = workout_plans
            else:
                content_url['workout_plans'] = [workout_id]
            content_db.update_content(url_content['content_id'], url_content['email'], content_url)
        return client_content

@views.route("/calendar", methods=["GET","POST"])
@login_required
def calendar():
    current_user_values = user_db.query_user(current_user.get_id())
    client_content = current_user_values['content']
    if 'custom_workout' not in client_content:
        client_content['custom_workout'] = dict()
    if 'current_custom_workout' not in client_content:
        client_content['current_custom_workout'] = dict()
    if request.method == 'POST':
        complete_workout = request.form.get("complete_workout")
        if complete_workout:
            current_custom_workouts = complete_custom_workout(complete_workout, client_content)
            return render_template("calendar.html", user=current_user, tab="workout", 
                custom_workouts=current_custom_workouts)
        delete_workout = request.form.get("delete_workout")
        if delete_workout:
            current_custom_workouts = delete_custom_workout(delete_workout, client_content)
            return render_template("calendar.html", user=current_user, tab="workout", 
                custom_workouts=current_custom_workouts)
        url_content = request.form.get("content_button")
        if url_content:
            return redirect(url_for('views.content', id=url_content))
        create_workout_button = request.form.get("create_workout_button")
        create_meal_button = request.form.get("create_meal_button")
        if create_workout_button:
            title = request.form.get("title")
            description = request.form.get("description2")
            difficulty = request.form.get("difficulty")
            duration = request.form.get("duration")
            training_type = request.form.get("training_type")
            content_id = request.form.get("content_id")
            client_content = add_custom_workout(title, description, difficulty, duration, training_type, content_id, client_content)
            return render_template("calendar.html", user=current_user, tab="workout", 
                custom_workouts=client_content['current_custom_workout'])
        elif create_meal_button:
            return render_template("calendar.html", user=current_user, tab="meal", 
                custom_workouts=client_content['current_custom_workout'])
    return render_template("calendar.html", user=current_user, tab="appointment", 
        custom_workouts=client_content['current_custom_workout'])
    
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
            if 'workout_plans' in current_content:
                workout_plans = current_content['workout_plans']
            else:
                workout_plans = None
            if workout_plans:
                plan_count = len(workout_plans)
            else:
                plan_count = 0
            user_path = url_for("users.user_page", id = created_user)
            return render_template("content.html", created_user = created_user, title = title, description = description, 
                content_link = content_link, content_date = content_date, user_path = user_path, content_type = content_type, view_count=view_count, approved=approved,
                mode_of_instruction=mode_of_instruction, workout_type=workout_type, workout_plans=plan_count)
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


@views.route("/messages")
@login_required
def messages():
    #get a list of all conversations user is involved in
    #all senders are clients, so we can check the user's role to see what fields to look for
    #pass that list of conversations to the template
    conversations = None
    if current_user.role == roles[0]:
        conversations = messages_db.get_client_conversations(current_user.email)
    elif current_user.role == roles[1]:
        conversations = messages_db.get_professional_conversations(current_user.email)
    elif current_user.role == roles[2]:
        conversations = messages_db.get_admin_conversations()
    return render_template("messages.html", conversations=conversations)


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

