import boto3
import uuid

def upload_file(file, bucket_name, key):
    s3_client = boto3.resource('s3')
    try: 
        s3_client.Bucket(bucket_name).put_object(Key=key, Body=file)
    except Exception:
        raise Exception("An error occurred while uploading the file.")
    
def get_unique_filename(original_file_name):
    return f"{uuid.uuid4()}-{original_file_name}"

def generate_presigned_url(bucket_name, key):
    s3_client = boto3.client('s3')
    return s3_client.generate_presigned_url(
        ClientMethod='get_object', 
        Params={'Bucket': bucket_name, 'Key': key}, 
        ExpiresIn=3600
    )
    