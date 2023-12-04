from flask import Blueprint, render_template, request
# from my_app.hello.models import MESSAGES

hello = Blueprint('hello', __name__)


@hello.route('/')
@hello.route('/hello')
def hello_world():
    user = request.args.get('user', 'Mike')
    return render_template('index.html', user=user)


# @hello.route('/show/<key>')
# def get_message(key):
#     return MESSAGES.get(key) or f"{key} not found!"
#
#
# @hello.route('/add/<key>/<message>')
# def add_or_update_message(key, message):
#     MESSAGES[key] = message
#     return f"{key} Added/Updated"
