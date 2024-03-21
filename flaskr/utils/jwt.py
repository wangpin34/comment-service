from datetime import datetime, timedelta, timezone

import jwt


def gen_jwt(user_id, secret):
   payload = {
      'user_id': user_id,
      'exp': datetime.now(timezone.utc) + timedelta(days=1)
   }
   jwt_token = jwt.encode(payload, secret, algorithm='HS256')
   return jwt_token

def verify_jwt(jwt_token, secret):
   jwt.decode(jwt_token, secret, algorithms=['HS256'])