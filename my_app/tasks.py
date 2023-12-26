import os

from flask_mail import Message
from flask import render_template, current_app
from werkzeug.utils import secure_filename
import boto3

from my_app import app, mail, celery
from my_app.catalog.models import Category


@celery.task()
def send_mail(category_id, category_name):
    with app.app_context():
        category = Category(category_name)
        category.id = category_id
        message = Message(
            "New category added",
            recipients=[app.config['RECEIVER_EMAIL']])
        message.body = render_template(
            "category-create-email-text.html",
            category=category
        )
        message.html = render_template(
            "category-create-email-html.html",
            category=category
        )
        mail.send(message)


@celery.task()
def save_image_async(image_path, filename):
    with open(image_path, 'rb') as f:
        session = boto3.Session(
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
        )
        s3 = session.resource('s3')
        bucket = s3.Bucket(current_app.config['AWS_BUCKET'])
        if bucket not in list(s3.buckets.all()):
            bucket = s3.create_bucket(
                Bucket=current_app.config['AWS_BUCKET'],
                CreateBucketConfiguration={
                    'LocationConstraint':
                        'ap-south-1'},
            )
        bucket.upload_fileobj(
            f,
            filename,
            ExtraArgs={'ACL': 'public-read'}
        )
    os.remove(image_path)