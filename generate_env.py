import os

env_vars = {
    "DATABASE_URL": "postgresql://user:password@postgres:5432/ragdb",
    "S3_ENDPOINT_URL": "http://minio:9000",
    "S3_ACCESS_KEY": "admin",
    "S3_SECRET_KEY": "password",
    "S3_BUCKET": "documents",
    "MINIO_ROOT_USER": "admin",
    "MINIO_ROOT_PASSWORD": "password",
    "POSTGRES_USER": "user",
    "POSTGRES_PASSWORD": "password",
    "POSTGRES_DB": "ragdb"
}

env_file_path = ".env"

if not os.path.exists(env_file_path):
    with open(env_file_path, "w") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    print("[+] Created .env with default values.")
else:
    print("[!] .env file already exists. No changes made.")
