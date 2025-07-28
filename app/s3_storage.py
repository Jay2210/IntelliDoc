import json
import boto3
from botocore.exceptions import ClientError
from app.config import settings

_s3 = boto3.resource(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)
_bucket = _s3.Bucket(settings.S3_BUCKET)

def save_json(key: str, obj: dict) -> None:
    _bucket.put_object(Key=key, Body=json.dumps(obj).encode("utf-8"))

def load_json(key: str) -> dict:
    try:
        resp = _bucket.Object(key).get()
        return json.loads(resp["Body"].read())
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return {}
        raise

def list_keys(prefix: str) -> list:
    return [o.key for o in _bucket.objects.filter(Prefix=prefix)]
