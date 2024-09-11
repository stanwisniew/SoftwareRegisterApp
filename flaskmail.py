from flask_mail import Mail

mail = Mail()  # Initialize the Mail object without linking it to any Flask app yet

def init_mail(app):
    # Configure mail settings and bind the Mail object to the app
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'softwareregister999@gmail.com'
    app.config['MAIL_PASSWORD'] = 'eskd ylxa proc odhh'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_DEFAULT_SENDER'] = 'softwareregister999@gmail.com'

    mail.init_app(app)  # Bind the Mail object to the existing Flask app
