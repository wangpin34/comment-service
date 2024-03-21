from datetime import datetime, timedelta, timezone

import jwt


def gen_jwt(user, secret):
   payload = {
      'user_id': str(user.id),
      'username': user.username,
      'email': user.email,
      'exp': datetime.now(timezone.utc) + timedelta(days=1)
   }
   jwt_token = jwt.encode(payload, secret, algorithm='HS256')
   return jwt_token

def verify_jwt(jwt_token, secret):
   return jwt.decode(jwt_token, secret, algorithms=['HS256'])