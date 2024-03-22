from mongoengine import (DateField, Document, IntField, ObjectIdField,
                         StringField)


class User(Document):
   username = StringField(required=True)
   password = StringField(required=True, min_length=2)
   email = StringField(required=True, unique=True)
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
