"""This creates a Blueprint named 'auth'."""

import functools
from flask import (
    Blueprint, request, redirect, url_for, flash, render_template, g, session
)
from werkzeug.security import generate_password_hash, check_password_hash
from flaskr.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register new users view.

    When the user visits the /auth/register URL, the register view will
    return HTML with a form for them to fill out. When they submit the form,
    it will validate their input and either show the form again with an error
    message or create the new user and go to the login page.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Username is requered."
        elif not password:
            error = "Password is requered."
        elif db.execute(
            "SELECT id FROM user WHERE username = ?", (username, )
        ).fetchone() is not None:
            error = "User {} is already registered".format(username)
        else:
            db.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            db.commit()
            return redirect(url_for("auth.login"))

        flash(error)
    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Login user view."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT id FROM user WHERE username = ?", (username, )
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password"

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")

@bp.before_app_request
def load_logged_in_user():
    """Get session's user info from DB for the length of the request."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()

@bp.route("/logout")
def logout():
    """Remove the user id from the session."""
    session.clear()
    return redirect(url_for("index"))

def login_required(view):
    """Require Authentication in Other Views.

    This decorator returns a new view function that wraps the original
    view it’s applied to. The new function checks if a user is loaded
    and redirects to the login page otherwise. If a user is loaded
    the original view is called and continues normally.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view