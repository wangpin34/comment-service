import json
import os
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from mongoengine import DoesNotExist, connect

from flaskr.db import Comment, Post, User
from flaskr.utils.jwt import gen_jwt, verify_jwt

load_dotenv()

app = Flask(__name__)

connect(host=os.environ.get('MONGODB_URI'))

JWT_SECRET = os.environ.get('JWT_SECRET')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            parts = auth_header.split(' ')
            if len(parts) == 2 and parts[0].lower() == 'bearer':
               _, jwt_token = auth_header.split(' ')
               try:
                  payload = verify_jwt(jwt_token, secret=JWT_SECRET)
                  g.user_id = payload.get('user_id')
                  g.username = payload.get('username')
                  g.email = payload.get('email')
               except jwt.ExpiredSignatureError:
                  return jsonify({'message': 'Token expired'}), 401
               except jwt.InvalidTokenError:
                  return jsonify({'message': 'Invalid token'}), 401
               except Exception as e:
                  return jsonify({'message': 'An unexpected error occurred: {}'.format(str(e))}), 500
            else:
               return jsonify({'message': 'Invalid auth header'}), 401
        else:
            return jsonify({'message': 'No auth header provided'}), 401
        return f(*args, **kwargs)
    return decorated

@app.get('/')
def hello_world():
  return f'Hello, {__name__}!'

@app.get('/ping')
def ping():
  return 'pong'

@app.get('/health')
def health():
   return 'ok'

@app.post('/sign-in')
def sign_in():
   email = request.get_json().get('email')
   password = request.get_json().get('password')
   user = User.objects(email=email, password=password).first()
   if not user:
      return 'invalid credentials or user not found', 400
   return {
      'username': user.username,
      'email': user.email,
      'token': gen_jwt(user, secret=JWT_SECRET)
   }, 200

def transform_post_json(obj):
   data = json.loads(obj.to_json())
   data['id'] = str(ObjectId(data['_id']['$oid']))
   del data['_id']
   if 'createdAt' in data:
      data['createdAt'] = data['createdAt']['$date']
   if 'updatedAt' in data:
      data['updatedAt'] = data['updatedAt']['$date']   
   return data

@app.get('/posts')
@token_required
def list_posts():
   posts = Post.objects.all()
   return [transform_post_json(post) for post in posts]

@app.post('/posts')
@token_required
def create_post():
   payload = request.get_json()
   post = Post(content=payload.get('content'), author=g.email, createdAt=datetime.now)
   post.save()
   return transform_post_json(post), 201

@app.get('/posts/<id>')
@token_required
def get_post(id):
   post = Post.objects.get(id=ObjectId(id))
   if not post:
      return 'post not found', 404
   return transform_post_json(post), 200

@app.put('/posts/<id>')
@token_required
def update_post(id):
   post = Post.objects.get(id=ObjectId(id), author=g.email)
   if not post:
      return 'post not found', 404
   payload = request.get_json()
   post.content = payload.get('content')
   return transform_post_json(post), 200

@app.delete('/posts/<id>')
@token_required
def delete_post(id):
   return 'not implemented', 501

def transform_comment_json(obj):
   data = json.loads(obj.to_json())
   data['id'] = str(ObjectId(data['_id']['$oid']))
   del data['_id']
   data['postId'] = str(ObjectId(data['postId']['$oid']))
   del data['postId']
   if 'createdAt' in data:
      data['createdAt'] = data['createdAt']['$date']
   if 'updatedAt' in data:
      data['updatedAt'] = data['updatedAt']['$date']   
   return data

@app.get('/comments')
@token_required
def list_comments(): 
   comments = Comment.objects.all()
   return [transform_comment_json(comment) for comment in comments]

@app.get('/comments/<id>')
@token_required
def get_comment(id):
   comment = Comment.objects.get(id=ObjectId(id))
   if not comment:
      return jsonify({'message': 'Comment not found'}), 404
   return transform_comment_json(comment), 200

@app.post('/comments')
@token_required
def create_comment():
   payload = request.get_json()
   comment = Comment(content=payload.get('content'), author=g.email, createdAt=datetime.now, postId=ObjectId(payload.get('postId')), upvoteCount=0, downvoteCount=0)
   if 'replyToCommentId' in payload:
      comment.replyToCommentId = ObjectId(payload.get('replyToCommentId'))
   comment.save()
   return transform_comment_json(comment), 201

@app.put('/comments/<id>')
@token_required
def update_comment(id):
   try:
      comment = Comment.objects.get(id=ObjectId(id), author=g.email)
      if not comment:
         return jsonify({'message': 'Comment not found'}), 404
      payload = request.get_json()
      comment.content = payload.get('content')
      comment.updatedAt = datetime.now
      comment.save()
      return transform_comment_json(comment), 200
   except DoesNotExist:
      return jsonify({'message': 'Comment not found'}), 404
   except Exception as e:
      return jsonify({'message': str(e) }), 500
   
   

@app.delete('/comments/<id>')
@token_required
def delete_comment(id):
   comment = Comment.objects.get(id=ObjectId(id), author=g.email)
   if not comment:
      return jsonify({'message': 'Comment not found'}), 404
   
   comment.delete()
   return jsonify({'message': 'comment deleted'}), 204

if __name__ == "__main__":
   app.run(port=5000)