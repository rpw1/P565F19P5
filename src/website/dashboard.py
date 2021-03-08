from database.user_database import UserDatabase
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.content_database import ContentDatabase

user_db = UserDatabase()
content_db = ContentDatabase
auth = Blueprint("dashboard", __name__)

