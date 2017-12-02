from peewee import *
import datetime
import os.path

db = SqliteDatabase('people.db')
db.connect()

class BaseModel(Model):
    class Meta:
        database = db

class Post(BaseModel):
    post_id = CharField(unique=True)
    message = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)

class Comment(BaseModel):
    post = ForeignKeyField(Post, related_name='parent_post')
    comment_id = CharField(unique=True)
    message = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)
    has_been_deleted = BooleanField(default=False)
    has_been_posted = BooleanField(default=False)
