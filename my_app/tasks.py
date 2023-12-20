from flask_mail import Message
from flask import render_template


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
