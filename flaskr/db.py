from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from mongoengine import (DateField, Document, IntField, ObjectIdField,
                         StringField, connect)


class User(Document):
   username = StringField(required=True)
   password = StringField(required=True)
   email = StringField(required=True)
   createdAt = DateField(required=True)
   updatedAt = DateField(required=False)

class Post(Document):
   content = StringField(required=True)
   author = StringField(required=True)
   createdAt = DateField(required=True)
   updatedAt = DateField(required=False)

class Comment(Document):
   content = StringField(required=True)
   author = StringField(required=True)
   createdAt = DateField(required=True)
   updatedAt = DateField(required=False)
   replyToCommentId = ObjectIdField(required=False)
   upvoteCount = IntField(required=True)
   downvoteCount = IntField(required=True)
   postId = ObjectIdField(required=True)
