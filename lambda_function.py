import boto3
import hashlib
import json
import s3
import random, string

def randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

def lambda_handler(event, context):
    auth = event['headers']['authorization']
    req_method = event['requestContext']['http']['method']
    req_path= event['requestContext']['http']['path']
    print(req_method+':'+req_path)
    response = {}
    if req_method == 'POST' and req_path == '/backup':
        repponse = {
            'data': None,
        }
    elif req_method == 'GET' and req_path == '/restore':
        response = {
            'data': [
                {
                  'orderId': 0,
                  'memoId': '20240101-000000',
                  'memoPreview': 'サンプルサンプルサンプルサンプル\nサンプル',
                  'memo': 'サンプルサンプルサンプルサンプル\nサンプル',
                  'backColor': 800,
                },
                {
                  'orderId': 1,
                  'memoId': '20240101-000001',
                  'memoPreview': 'サンプルサンプルサンプルサンプル\nサンプル',
                  'memo': 'サンプルサンプルサンプルサンプル\nサンプル',
                  'backColor': 500,
                },
                {
                  'orderId': 2,
                  'memoId': '20250101-000001',
                  'memoPreview': 'サンプルサンプルサンプルサンプル\nサンプル',
                  'memo': 'サンプルサンプルサンプルサンプル\nサンプル',
                  'backColor': 600,
                },
            ],
        }
    else:
        raise SystemError('No method.')
    
    r = randomname(32)
    print(r)
    a = hashlib.md5(r.encode()).digest()
    b = hashlib.md5(a).hexdigest()
    print(a)
    print(b)
    
    res = s3.s3_get("tag-memo", auth)
    
    print(res)
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
