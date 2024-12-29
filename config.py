import os
#This variable defines the base directory of the application, which is the directory that contains the app package.
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    #This variable is the URL that points to the database file.
    #We define it as an environment variable, so it can be set from the outside when needed.
    #If it is not defined, we configure a default database named app.db located in the main directory of the application, which is stored in the basedir variable.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
