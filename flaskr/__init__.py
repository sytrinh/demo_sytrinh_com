import os

from flask import Flask, render_template, redirect

def page_not_found(e):
  return render_template('404.html'), 404

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )
    app.url_map.strict_slashes = False # make url with / and without /, both working
    app.register_error_handler(404, page_not_found)

    # Application 1
    from . import digit_recognizer
    app.register_blueprint(digit_recognizer.bp)

    from . import pancake_token_info
    app.register_blueprint(pancake_token_info.bp)

    # a simple page that says hello
    @app.route('/')
    def index():
        return redirect("https://sytrinh.com")

    return app
