from flask import Flask, render_template, current_app
from flask_login import LoginManager

from src import mailgun, token, google_recaptcha

login_manager = LoginManager()


def error_404_page(error):
    return render_template('error/404.html'), 404


def error_500_page(error):
    return render_template('error/500.html'), 500


def create_app(config: str):
    app = Flask(__name__)
    app.config.from_object(f'src.channelry.config.{config.title()}')

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'danger'
    login_manager.init_app(app)

    mailgun.api_key = app.config.get('MAILGUN_API_KEY')
    token.salt = app.config.get('PASSWORD_SALT')
    token.secret_key = app.config.get('SECRET_KEY')
    google_recaptcha.site_key = app.config.get('RECAPTCHA_SITE_KEY')
    google_recaptcha.secret_key = app.config.get('RECAPTCHA_SECRET_KEY')

    from .models import db
    db.init_app(app)

    from .models.auth import User

    @login_manager.user_loader
    def load_user(user_id: int):
        return User.query.get(int(user_id))

    app.register_error_handler(404, error_404_page)
    app.register_error_handler(500, error_500_page)

    @app.before_first_request
    def create_db():
        db.create_all(app=app)

    from .views.auth import auth_bp
    from .views.home import home_bp
    from .views.dashboard import dashboard_bp
    from .views.inventory import inventory_bp
    from .views.profile import profile_bp
    from .views.account import account_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(account_bp)

    return app