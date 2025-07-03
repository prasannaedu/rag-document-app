import boto3
from botocore.client import Config

s3_client = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="admin",
    aws_secret_access_key="password123",
    config=Config(signature_version="s3v4")
)

try:
    s3_client.head_bucket(Bucket="documents")
    print("Bucket 'documents' exists!")
except s3_client.exceptions.ClientError as e:
    if e.response["Error"]["Code"] == "404":
        print("Bucket 'documents' does not exist. Creating it...")
        s3_client.create_bucket(Bucket="documents")
        print("Created bucket 'documents'!")
    else:
        print(f"Error: {e}")
