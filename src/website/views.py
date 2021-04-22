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
from math import ceil, floor
from decimal import Decimal
from random import shuffle

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
        meal_plans = []
        calories = ""
        name_dict = {}
        email = current_user.get_id()
        calorie_goal = None
        calorie_total = None
        try :
            content = progress_db.query_user(email)
            calories = content['content']['weekly_cals']
            if 'weekly_calorie_total' in content['content'] and 'weekly_calorie_goal' in content['content']:
                calorie_goal = content['content']['weekly_calorie_goal']
                calorie_total = content['content']['weekly_calorie_total']
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
        workout_recs = dict()
        diet_recs = dict()
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
                item_email = current_content['email']
                item_user = user_db.query_user(item_email)
                name_dict[item_email] = '{} {}'.format(item_user['first_name'], item_user['last_name'])
            elif item_content['mode_of_instruction'] == 'Workout plan' and current_content['approved']:
                workout_plans.append(current_content)
                item_email = current_content['email']
                item_user = user_db.query_user(item_email)
                name_dict[item_email] = '{} {}'.format(item_user['first_name'], item_user['last_name'])
            elif item_content['mode_of_instruction'] == 'Video' and current_content['approved']:
                fitness_videos.append(current_content)
                item_email = current_content['email']
                item_user = user_db.query_user(item_email)
                name_dict[item_email] = '{} {}'.format(item_user['first_name'], item_user['last_name'])
            elif item_content['mode_of_instruction'] == 'Meal plan' and current_content['approved']:
                fitness_videos.append(current_content)    
            if 'workout_difficulty' in item_content and current_content['approved']:
                if item_content['workout_difficulty'] not in workout_recs:
                    workout_recs[item_content['workout_difficulty']] = [current_content]
                else:
                    workout_recs_list = workout_recs[item_content['workout_difficulty']]
                    workout_recs_list.append(current_content)
                    workout_recs[item_content['workout_difficulty']] = workout_recs_list

            if 'diet_cal' in item_content and current_content['approved']:
                if item_content['diet_cal'] not in diet_recs:
                    diet_recs[item_content['diet_cal']] = [current_content]
                else:
                    diet_recs_list = diet_recs[item_content['diet_cal']]
                    diet_recs_list.append(current_content)
                    diet_recs[item_content['diet_cal']] = diet_recs_list

        user_values = user_db.query_user(email)
        custom_workouts = dict()
        recommended_diets = []
        recommended_workouts = []
        if user_values['role'] == 'client':
            client_content = user_values['content']
            if 'current_custom_workout' in client_content and client_content['current_custom_workout']:
                custom_workouts = client_content['current_custom_workout']
            if calorie_goal and calorie_total and Decimal(calorie_goal) > 0:
                if ((calorie_total * 100) / Decimal(calorie_goal)) <= 33 and 'High Calorie' in diet_recs:
                    recommended_diets = diet_recs['High Calorie']
                elif ((calorie_total * 100) / Decimal(calorie_goal)) <= 66 and 'Medium Calorie' in diet_recs:
                    recommended_diets = diet_recs['Medium Calorie']
                elif 'Low Calorie' in diet_recs:
                    recommended_diets = diet_recs['Low Calorie']
            if 'custom_workout' in client_content:
                custom_workouts_rec = client_content['custom_workout']
                workout_difficulty_avg = 0.0
                for key, item in custom_workouts_rec.items():
                    try:
                        workout_difficulty_avg += int(item['difficulty'])
                    except Exception as e:
                        continue
                workout_difficulty_avg /= (len(custom_workouts_rec) + 1)
                difficulty_ceiling = ceil(workout_difficulty_avg)
                difficulty_floor = floor(workout_difficulty_avg)
                if str(difficulty_ceiling) in workout_recs:
                    recommended_workouts.extend(workout_recs[str(difficulty_ceiling)])
                if str(difficulty_floor) in workout_recs:
                    recommended_workouts.extend(workout_recs[str(difficulty_floor)])
        recommended_diets.sort(key=sort_by_rating, reverse=True)
        recommended_workouts.sort(key=sort_by_rating, reverse=True)
        recommended_fp = []
        for diet in recommended_diets:
            fp = user_db.get_fitness_professional(diet['email'])
            if fp not in recommended_fp:
                recommended_fp.append(fp)
        for workout in recommended_workouts:
            fp = user_db.get_fitness_professional(workout['email'])
            if fp not in recommended_fp:
                recommended_fp.append(fp)
        shuffle(recommended_fp)
        subscribed_content = []
        if 'subscribed_accounts' in user_values['content']:
            subscribed_accounts = user_values['content']['subscribed_accounts']
            for account in subscribed_accounts:
                subscribed_content.extend(content_db.scan_content_by_email(account))
                item_user = user_db.query_user(account)
                name_dict[account] = '{} {}'.format(item_user['first_name'], item_user['last_name'])
        todays_views = metrics_bucket.get_todays_views()
        total_views = metrics_bucket.get_total_view_count()

        return render_template("dashboard.html", user=current_user, total_users=total_users, total_content=total_content, 
            uploaded_today=uploaded_today_approved, type_count=type_count, subscribed_content=subscribed_content,
            diet_plans=diet_plans, workout_plans=workout_plans, fitness_videos=fitness_videos, uploaded_today_len=uploaded_today_count, 
            calories=calories, todays_views=todays_views, total_views = total_views, custom_workouts=custom_workouts, names=name_dict,
            recommended_workouts=recommended_workouts, recommended_diets=recommended_diets, recommended_fp=recommended_fp)
    else: 
        return render_template("landing.html")

def sort_by_rating(e):
    return Decimal(e['content']['rating'])


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
    del client_content['current_custom_workout'][delete_workout]
    user_db.update_client_content(current_user.get_id(), client_content)
    return client_content

def delete_custom_meal(delete_meal, client_content):
    """
    This function takes a meal_id and the current client's content and removes the meal from the client and content.
    """
    del client_content['meals'][delete_meal]
    del client_content['current_meals'][delete_meal]
    user_db.update_client_content(current_user.get_id(), client_content)
    return client_content

def delete_custom_sleep(delete_sleep, client_content):
    """
    This function takes a sleep_id and the current client's content and removes the sleep from the client and content.
    """
    del client_content['sleep'][delete_sleep]
    del client_content['current_sleep'][delete_sleep]
    user_db.update_client_content(current_user.get_id(), client_content)
    return client_content

def complete_custom_workout(complete_workout, client_content):
    """
        removes complete_workout's custom workout id from the list of current custom workouts
    """
    del client_content['current_custom_workout'][complete_workout]
    user_db.update_client_content(current_user.get_id(), client_content)
    return client_content

def complete_custom_meal(complete_meal, client_content):
    """
        removes complete_meal's custom meal id from the list of current custom meals
    """
    del client_content['current_meals'][complete_meal]
    meal = client_content['meals'][complete_meal]
    user_db.update_client_content(current_user.get_id(), client_content)
    email = current_user.get_id()
    day_of_week = datetime.today().strftime('%A')
    new_cals = meal['total_calories']
    calorie_progress = progress_db.get_content(email)['content']
    split = calorie_progress["weekly_cals"].split(",")
    add_cals(email, day_of_week, new_cals, split, calorie_progress['weekly_calorie_goal'], calorie_progress['weekly_calorie_total'], calorie_progress['last_reset'])

def complete_custom_sleep(complete_sleep, client_content):
    """
        removes complete_sleeps's custom sleep id from the list of current custom sleeps
    """
    del client_content['current_sleep'][complete_sleep]
    user_db.update_client_content(current_user.get_id(), client_content)
    return client_content

def add_custom_workout(title, description, difficulty, duration, training_type, content_id, client_content):
    url_content = content_db.query_content_by_id(content_id)
    if not url_content and content_id:
        flash("Error: Content ID was incorrect")
        return render_template("calendar.html", user=current_user, isWorkout=True, 
            custom_workouts=client_content['current_custom_workout'])
    else:
        now = datetime.now()
        today = now.strftime("%m/%d/%Y")
        workout_id = str(uuid.uuid4())
        custom_workout = {
            "workout_id": workout_id,
            "title": title,
            "description": description,
            "difficulty": difficulty,
            "duration": duration,
            "training_type": training_type,
            "content_id": content_id,
            "date": today
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

def add_meal(entree, sides, drink, total_calories, client_content):
    now = datetime.now()
    today = now.strftime("%m/%d/%Y")
    meal_id = str(uuid.uuid4())
    meal = {
        "entree": entree,
        "sides": sides,
        "drink": drink,
        "total_calories": total_calories,
        "date": today
    }
    client_content['meals'][meal_id] = meal
    client_content['current_meals'][meal_id] = meal
    user_db.update_client_content(current_user.get_id(), client_content)
    return client_content

def add_sleep(sleep_date, start_sleep, end_sleep, client_content):
    sleep_id = str(uuid.uuid4())
    ss_split = start_sleep.split(":")
    es_split = end_sleep.split(":")
    start_hours = int(ss_split[0])
    end_hours = int(es_split[0])
    start_minutes = int(ss_split[1])
    end_minutes = int(es_split[1])
    start_hours -= 24
    current_hours = end_hours - start_hours
    minutes = end_minutes - start_minutes
    if minutes < 0:
        current_hours -= 1
        minutes = 60 + minutes

    sleep = {
        "sleep_date": sleep_date,
        "hours": current_hours,
        "start_sleep": start_sleep,
        "end_sleep": end_sleep,
        "minutes": minutes
    }
    client_content['sleep'][sleep_id] = sleep
    client_content['current_sleep'][sleep_id] = sleep
    user_db.update_client_content(current_user.get_id(), client_content)
    return client_content

def meal_recommend():
        '''
        Recommends low calorie meal for user
        '''


@views.route("/calendar", methods=["GET","POST"])
@login_required
def calendar():
    current_user_values = user_db.query_user(current_user.get_id())
    client_content = current_user_values['content']
    if 'custom_workout' not in client_content:
        client_content['custom_workout'] = dict()
    if 'current_custom_workout' not in client_content:
        client_content['current_custom_workout'] = dict()
    if 'meals' not in client_content:
        client_content['meals'] = dict()
    if 'current_meals' not in client_content:
        client_content['current_meals'] = dict()
    if 'sleep' not in client_content:
        client_content['sleep'] = dict()
    if 'current_sleep' not in client_content:
        client_content['current_sleep'] = dict()
    if request.method == 'POST':
        complete_workout = request.form.get("complete_workout")
        if complete_workout:
            client_content = complete_custom_workout(complete_workout, client_content)
            return render_template("calendar.html", user=current_user, tab="workout", workout_chart_data = get_workout_chart_data(1, client_content),
                custom_workouts=client_content['current_custom_workout'], meals = client_content['current_meals'],
                sleep=client_content['current_sleep'])
        delete_workout = request.form.get("delete_workout")
        if delete_workout:
            client_content = delete_custom_workout(delete_workout, client_content)
            return render_template("calendar.html", user=current_user, tab="workout", workout_chart_data = get_workout_chart_data(1, client_content),
                custom_workouts=client_content['current_custom_workout'], meals = client_content['current_meals'],
                sleep=client_content['current_sleep'])
        
        complete_meal = request.form.get("complete_meal")
        if complete_meal:
            client_content = complete_custom_meal(complete_meal, client_content)
            return redirect(url_for('views.progress_tracking'))
        delete_meal = request.form.get("delete_meal")
        if delete_meal:
            client_content = delete_custom_meal(delete_meal, client_content)
            return render_template("calendar.html", user=current_user, tab="meal", workout_chart_data = get_workout_chart_data(1, client_content),
                custom_workouts=client_content['current_custom_workout'], meals = client_content['current_meals'],
                sleep=client_content['current_sleep'])

        # total_cal = request.form.get("total_calories")
        # weekly_goal = request.form.get("calorie_goal")
        # if total_cal > weekly_goal:
        #     client_content = meal_recommend()
        
        complete_sleep = request.form.get("complete_sleep")
        if complete_sleep:
            client_content = complete_custom_sleep(complete_sleep, client_content)
            return render_template("calendar.html", user=current_user, tab="sleep", workout_chart_data = get_workout_chart_data(1, client_content),
                custom_workouts=client_content['current_custom_workout'], meals = client_content['current_meals'],
                sleep=client_content['current_sleep'])
        delete_sleep = request.form.get("delete_sleep")
        if delete_sleep:
            client_content = delete_custom_sleep(delete_sleep, client_content)
            return render_template("calendar.html", user=current_user, tab="sleep", workout_chart_data = get_workout_chart_data(1, client_content),
                custom_workouts=client_content['current_custom_workout'], meals = client_content['current_meals'],
                sleep=client_content['current_sleep'])

        url_content = request.form.get("content_button")
        if url_content:
            return redirect(url_for('views.content', id=url_content))
        create_workout_button = request.form.get("create_workout_button")
        create_meal_button = request.form.get("create_meal_button")
        create_sleep_button = request.form.get("create_sleep_button")
        if create_workout_button:
            title = request.form.get("title")
            description = request.form.get("description2")
            difficulty = request.form.get("difficulty")
            duration = request.form.get("duration")
            training_type = request.form.get("training_type")
            content_id = request.form.get("content_id")
            client_content = add_custom_workout(title, description, difficulty, duration, training_type, content_id, client_content)
            return render_template("calendar.html", user=current_user, tab="workout", workout_chart_data = get_workout_chart_data(1, client_content),
                custom_workouts=client_content['current_custom_workout'], meals = client_content['current_meals'],
                sleep=client_content['current_sleep'])
        elif create_meal_button:
            entree = request.form.get("entree")
            sides = request.form.get("sides")
            drink = request.form.get("drink")
            total_calories = request.form.get("total_calories")
            client_content = add_meal(entree, sides, drink, total_calories, client_content)
            return render_template("calendar.html", user=current_user, tab="meal", workout_chart_data = get_workout_chart_data(1, client_content),
                custom_workouts=client_content['current_custom_workout'], meals = client_content['current_meals'],
                sleep=client_content['current_sleep'])
        elif create_sleep_button:
            date = request.form.get("sleep_date")
            start_sleep = request.form.get("start_sleep")
            end_sleep = request.form.get("end_sleep")
            client_content = add_sleep(date, start_sleep, end_sleep, client_content)
            return render_template("calendar.html", user=current_user, tab="sleep", workout_chart_data = get_workout_chart_data(1, client_content),
                custom_workouts=client_content['current_custom_workout'], meals = client_content['current_meals'],
                sleep=client_content['current_sleep'])
    return render_template("calendar.html", user=current_user, tab="appointment", workout_chart_data = get_workout_chart_data(1, client_content),
        custom_workouts=client_content['current_custom_workout'], meals = client_content['current_meals'],
            sleep=client_content['current_sleep'])

def get_workout_chart_data(month : int, client_content):
    workout_data = client_content['custom_workout']
    labels = ['Cardio', 'Strength Training', 'Flexibility', 'Endurance Training', 'Core Training', 'Other']
    workout_minutes = dict()
    workout_count = dict()
    for label in labels:
        workout_count[label] = 0
        workout_minutes[label] = 0
    present = datetime.now()
    for key, items in workout_data.items():
        if 'date' in items:
            created = datetime.strptime(items['date'], "%m/%d/%Y")
            if (present - timedelta(days=month * 30)) <= created:
                workout_minutes[items['training_type']] += int(items['duration'])
                workout_count[items['training_type']] += 1
    # print(workout_count)
    # print(workout_minutes)
    return workout_count, workout_minutes
    
    
@views.route("/content/<id>", methods=["GET","POST"])
@login_required
def content(id):
    average_rating = 0.0
    query_content = content_db.query_content_by_id(id)
    uploader = user_db.query_user(query_content['email'])
    uploader_name = '{} {}'.format(uploader['first_name'], uploader['last_name'])
    if request.method == "POST":
        has_editted = request.form.get("edit_val")
        #print(has_editted)
        action = request.form.get("moderate")
        title = request.form.get("title")
        email = request.form.get("email")
        if action == "delete":
            content_db.delete_content(id, email)
            message = Markup("<b>{}</b> successfully deleted".format(title))
            flash(message, category="success")
            return redirect(url_for("views.home"))
        if action == "rate":
            rating = request.form.get('rating')
            review = request.form.get('review')
            content_db.add_review(id, query_content['email'], current_user.email, rating, review)
            total_rating = 0
            query_content = content_db.query_content_by_id(id)
            reviews = query_content['content']['reviews']
            for reviewer in reviews:
                total_rating += int(reviews[reviewer][0])
            average_rating = total_rating/(len(reviews))
            content_db.update_rating(id, query_content['email'], str(average_rating))
        elif has_editted == "edit_val":
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
    reviews = {}
    reviewer_names = []
    has_editted = request

    if 'total_views' in content_user['content']:
        total_views = content_user['content']['total_views']
    user_email = current_user.get_id()
    if query_content:
        if 'content' in query_content:
            current_content = query_content['content']
            if 'reviews' in current_content:
                reviews = current_content['reviews']
                reviews = dict(sorted(reviews.items(), key = lambda i: i[1][2], reverse=True))
                total_rating = 0
                for reviewer in reviews:
                    total_rating += int(reviews[reviewer][0])
                    reviewer_info = user_db.query_user(reviewer)
                    reviewer_name = '{} {}'.format(reviewer_info['first_name'], reviewer_info['last_name'])
                    reviewer_names.append(reviewer_name)
                average_rating = total_rating/(len(reviews))
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
                mode_of_instruction=mode_of_instruction, workout_type=workout_type, workout_plans=plan_count, reviews=reviews, average_rating=average_rating, 
                reviewer_names=reviewer_names, uploader_name=uploader_name)
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
                "amount_viewed": 0,
                "rating": '0.0'
            }
            if moi == "Diet plan":
                diet_cal = request.form.get("dietCal")
                uploaded_content['diet_cal'] = diet_cal
            elif moi == "Workout plan":
                workout_difficulty = request.form.get("workoutDifficulty")
                uploaded_content['workout_difficulty'] = workout_difficulty
            content_db.insert_content(content_id, email, uploaded_content)
            flash("Upload successful!", category="success")
            return redirect(url_for("views.content", id = content_id))
        else:
            flash("You do not have permission to upload content")
            return redirect(url_for("views.home"))
    return render_template("upload.html")


@views.route("/messages", methods=['GET', 'POST'])
@login_required
def messages():
    #get a list of all conversations user is involved in
    #all senders are clients, so we can check the user's role to see what fields to look for
    #pass that list of conversations to the template
    content_db.delete_content('5659bd95-4b14-4922-ae64-f345442aed6d', 'None')
    if request.method == 'POST':
        action = request.form['action']
        if action == 'new':
            message = request.form.get("message")
            messages_db.insert_conversation(str(uuid.uuid4()), current_user.email, 'admin', message)
        if action == 'delete':
            conversation_id = request.form['id']
            messages_db.delete_conversation(conversation_id)
    conversations = None
    if current_user.role == roles[0]:
        conversations = messages_db.get_client_conversations(current_user.email)
    elif current_user.role == roles[1]:
        conversations = messages_db.get_professional_conversations(current_user.email)
    elif current_user.role == roles[2]:
        conversations = messages_db.get_admin_conversations()
    conversations = sorted(conversations, key = lambda i: i['update_time'], reverse=True)
    names = []
    for conv in conversations:
        sender_info = user_db.query_user(conv['sender_id'])
        sender_name = '{} {}'.format(sender_info['first_name'], sender_info['last_name'])
        recipient_name = 'Admin'
        if(conv['recipient_id'] != 'admin'):
            recipient_info = user_db.query_user(conv['recipient_id'])
            recipient_name = '{} {}'.format(recipient_info['first_name'], recipient_info['last_name'])
        names.append([sender_name, recipient_name])
    return render_template("messages.html", conversations=conversations, names=names)


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
    history = ""
    last_30_days = ""
    last_100_days = ""
    all_time = ""
    try :
        progress_db.query_user(email)
        content = progress_db.query_user(email)
        calories = content['content']['weekly_cals']
        weekly_calorie_goal= content['content']['weekly_calorie_goal']
        weekly_calorie_total= content['content']['weekly_calorie_total']
        last_reset = str(content['content']['last_reset'])
        history = content['content']['history']
        last_30_days = get_last_30_days(history)
        last_100_days = get_last_100_days(history)
        all_time = get_all_time(history)
    except:
        weekly_cals = "0,0,0,0,0,0,0"
        weekly_calorie_goal = "0"
        weekly_calorie_total = "0"
        last_reset = str(now)
        history = "0,0,0,0,0,0,0"
        base_content = {
            "weekly_cals": weekly_cals,
            "weekly_calorie_goal": weekly_calorie_goal,
            "weekly_calorie_total": weekly_calorie_total,
            "last_reset": last_reset,
            "history":history
        }
        progress_db.insert_content(email,base_content)
        progress_db.query_user(email)
        content = progress_db.query_user(email)
        calories = content['content']['weekly_cals']   
        weekly_calorie_goal= content['content']['weekly_calorie_goal']
        weekly_calorie_total= content['content']['weekly_calorie_total']
        last_reset = str(content['content']['last_reset'])
        history = content['content']['history']
        last_30_days = get_last_30_days(history)
    if (str(last_reset).startswith(str(today)) == False) and weekday == "Monday":
        weekly_cals = "0,0,0,0,0,0,0"
        weekly_calorie_goal = "0"
        weekly_calorie_total = "0"
        last_reset = str(now)
        history = history + ",0,0,0,0,0,0,0"
        base_content = {
            "weekly_cals": weekly_cals,
            "weekly_calorie_goal": weekly_calorie_goal,
            "weekly_calorie_total": weekly_calorie_total,
            "last_reset": last_reset,
            "history":history
        }
        progress_db.insert_content(email,base_content)
        progress_db.query_user(email)
        content = progress_db.query_user(email)
        calories = content['content']['weekly_cals']   
        weekly_calorie_goal= content['content']['weekly_calorie_goal']
        weekly_calorie_total= content['content']['weekly_calorie_total']
        last_reset = str(content['content']['last_reset'])
        print("shouldn't start with today")
   
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
            my_list = add_cals(email, day_of_week, new_cals, split, weekly_calorie_goal, weekly_calorie_total, last_reset, history)
            weekly_calorie_total = my_list[0]
            weekly_calorie_goal = my_list[1]
            calories = my_list[2]
            calorie_string = my_list[3]
            history = my_list[4]
            last_30_days = get_last_30_days(history)
            last_100_days = get_last_100_days(history)
            all_time = get_all_time(history)
            print("last 30 days" + last_30_days)
        elif action == "add_goal":
            calorie_goal = request.form.get("calorie_goal")
            try:
                weekly_calorie_goal = int(calorie_goal)
                if(weekly_calorie_goal >= 0):
                    base_content = {
                        "weekly_cals": calories,
                        "weekly_calorie_goal": weekly_calorie_goal,
                        "weekly_calorie_total": weekly_calorie_total,
                        "last_reset": last_reset,
                        "history": history
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
    return render_template('progress_tracking.html', user=current_user, todays_date = todays_date, calories = calories, calorie_string= calorie_string, calorie_goal = weekly_calorie_goal, calorie_total = weekly_calorie_total, last_30_days = last_30_days, last_100_days =last_100_days, all_time = all_time)

def add_cals(email, day_of_week, new_cals, split, weekly_calorie_goal, weekly_calorie_total, last_reset, history):
    weekly_calorie_total = int(weekly_calorie_total) + int(new_cals)
    history_split = history.split(",")
    history_length = len(history_split)
    if(day_of_week == "Monday"):
        updates_cals = int(split[0]) + int(new_cals)
        split[0] = str(updates_cals)
        history_split[history_length-7] = split[0]
    elif(day_of_week == "Tuesday"):
        updates_cals = int(split[1]) + int(new_cals)
        split[1] = str(updates_cals)
        history_split[history_length-6] = split[1]
    elif(day_of_week == "Wednesday"):
        updates_cals = int(split[2]) + int(new_cals)
        split[2] = str(updates_cals)
        history_split[history_length-5] = split[2]
    elif(day_of_week == "Thursday"):
        updates_cals = int(split[3]) + int(new_cals)
        split[3] = str(updates_cals)
        history_split[history_length -4] = split[3]
    elif(day_of_week == "Friday"):
        updates_cals = int(split[4]) + int(new_cals)
        split[4] = str(updates_cals)
        history_split[history_length -3] = split[4]
    elif(day_of_week == "Saturday"):
        updates_cals = int(split[5]) + int(new_cals)
        split[5] = str(updates_cals)
        history_split[history_length -2] = split[5]
    elif(day_of_week == "Sunday"):
        updates_cals = int(split[6]) + int(new_cals)
        split[6] = str(updates_cals)
        history_split[history_length-1] = split[6]
    calories = ""
    history = ""
    i=0
    for x in split:
        if(i==7):
            calories = calories + x
        else:
            calories = calories + x + ","
        i = i+1
    i=0
    for y in history_split:
        if (i==history_length-1):
            history = history + y
        else:
            history = history + y + ","
        i = i+1
    print(history)
    base_content = {
        "weekly_cals": calories,
        "weekly_calorie_goal": weekly_calorie_goal,
        "weekly_calorie_total": weekly_calorie_total,
        "last_reset": last_reset,
        "history":history
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
    return [weekly_calorie_total, weekly_calorie_goal, calories, calorie_string, history]

def get_last_30_days(history):
    history_split = history.split(",")
    history_length = len(history_split)
    i = 0
    num_of_empty_slots = 30-history_length
    history = ""
    last_30_days = ""
    if history_length<30:
        while num_of_empty_slots>0:
            last_30_days = last_30_days +  "0,"
            num_of_empty_slots = num_of_empty_slots-1
            i=i+1
        for y in history_split:
            if (i==30):
                last_30_days = last_30_days + y
            else:
                last_30_days = last_30_days + y + ","
            i=i+1
        return last_30_days

    i = history_length 
    j=30
    last_30_days = ""
    while j>0:
        if j==1:
            last_30_days = last_30_days + history_split[i-j]
        else:
            last_30_days = last_30_days + history_split[i-j] + ","
        j= j-1
    return last_30_days
def get_last_100_days(history):
    history_split = history.split(",")
    history_length = len(history_split)
    i = 0
    num_of_empty_slots = 100-history_length
    history = ""
    last_100_days = ""
    if history_length<100:
        while num_of_empty_slots>0:
            last_100_days = last_100_days +  "0,"
            num_of_empty_slots = num_of_empty_slots-1
            i=i+1
        for y in history_split:
            if (i==30):
                last_100_days = last_100_days + y
            else:
                last_100_days = last_100_days + y + ","
            i=i+1
        return last_100_days

    i = history_length 
    j=100
    last_100_days = ""
    while j>0:
        if j==1:
            last_100_days = last_100_days + history_split[i-j]
        else:
            last_100_days = last_100_days + history_split[i-j] + ","
        j= j-1
    return last_100_days

def get_all_time(history):
    history_split = history.split(",")
    l = len(history_split)
    all_time = ""
    i=0
    for x in history_split:
        if(l==i):
            all_time = all_time + x
        else:
            all_time = all_time + x + ","
        i= i+1
    return all_time