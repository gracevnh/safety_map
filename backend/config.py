import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://safety_map_user:your_password@localhost/safety_map'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
