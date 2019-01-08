import os
from flask import Flask
from dotenv import load_dotenv
from . import db, auth, blog


def create_app(test_config=None):
    """The Application Factory.

    Args:
        test_config: A configuration mapping.

    Returns:
        The configured application instance.

    Instead of creating a Flask instance globally, you will create it
    inside a function. This function is known as the application factory.
    Any configuration, registration, and other setup the application
    needs will happen inside the function, then the application
    will be returned.
    """

    """Load environment variables from a file named .env in the current
    directory or any of its parents or from the path specificied
    """
    load_dotenv(verbose=True)

    # create and configure the app
    app = Flask(__name__,  instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    # Register DB with the Application
    db.init_app(app)

    # Import and register the blueprint
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="index")

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Helo world!"

    return app
