"""This creates a Blueprint named 'auth'."""

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
            "SELECT id FROM user WHERE username = ?",
            (username, )
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

