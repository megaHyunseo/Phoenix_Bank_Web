from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    registration_number = db.Column(db.String(14), primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'
