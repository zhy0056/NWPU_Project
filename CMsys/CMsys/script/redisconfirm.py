import redis
"""
本文件用于查看redis是否成功存储手机号，并是否会于30s之后过期
"""
conn = redis.Redis(host='127.0.0.1', port=6379)
# conn.set('foo', 'bar')

# result = conn.get('foo')
result = conn.get('15602983197')
# conn.flushall()
print(result)
