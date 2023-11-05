import datetime
import jwt

salt = '200056zhanghaiyang2018303029'


def create_token(payload, timeout=20):
    headers = {
        'typ': 'jwt',
        'alg': 'HS256'
    }
    # 构造payload
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=timeout)
    token = jwt.encode(payload=payload, key=salt, algorithm='HS256', headers=headers)  # .decode(utf-8)

    return token
