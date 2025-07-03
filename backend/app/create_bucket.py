import boto3

s3_client = boto3.client(
    "s3",
    endpoint_url="http://minio:9000",
    aws_access_key_id="admin",
    aws_secret_access_key="password"
)

try:
    s3_client.create_bucket(Bucket="documents")
    print("Bucket 'documents' created successfully.")
except s3_client.exceptions.BucketAlreadyExists:
    print("Bucket 'documents' already exists.")
except Exception as e:
    print(f"Error creating bucket: {str(e)}")


