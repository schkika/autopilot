import boto3
from django.http import HttpResponseRedirect, JsonResponse
AWS_REGION = "eu-central-1"

def get_bucket_list():
    # Create an S3 client
    s3 = boto3.client('s3')

    try:
        # Retrieve the list of buckets
        response = s3.list_buckets()

        if 'Buckets' in response:
            buckets = dict([[bucket['Name'], dict([[folder, get_files_in_folder(bucket['Name'], folder)] for folder in  get_bucket_folders(bucket['Name'])])] for bucket in response['Buckets']])
            return buckets
        else:
            return []

    except Exception as e:
        print(f"Error retrieving bucket list: {str(e)}")
        return []
    

def create_empty_folder(bucket_name, folder_path):
    # Create an S3 client
    s3 = boto3.client('s3')

    try:
        # Upload an empty object to simulate creating the folder
        folder_key = f"{folder_path}/"
        response = s3.put_object(Bucket=bucket_name, Key=folder_key)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False

    except Exception as e:
        print(f"Error creating empty folder '{folder_path}' in bucket '{bucket_name}': {str(e)}")
        return False
    

def get_bucket_folders(bucket_name):
    # Create an S3 client
    s3 = boto3.client('s3')

    try:
        # Retrieve the list of objects in the bucket
        response = s3.list_objects_v2(Bucket=bucket_name, Delimiter='/')

        if 'CommonPrefixes' in response:
            folders = [prefix['Prefix'].rstrip('/') for prefix in response['CommonPrefixes']]
            return folders
        else:
            return []

    except Exception as e:
        print(f"Error retrieving bucket folders for bucket '{bucket_name}': {str(e)}")
        return []


def get_folders_in_folder(bucket_name, folder_path):
    # Create an S3 client
    s3 = boto3.client('s3')

    try:
        # Retrieve the list of objects in the folder
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path, Delimiter='/')

        if 'CommonPrefixes' in response:
            folders = [prefix['Prefix'].replace(folder_path, '').rstrip('/') for prefix in response['CommonPrefixes']]
            return folders
        else:
            return []

    except Exception as e:
        print(f"Error retrieving folders in folder '{folder_path}' in bucket '{bucket_name}': {str(e)}")
        return []


def create_s3_bucket(bucket_name):
    s3 = boto3.client('s3', region_name=AWS_REGION)
    location = {'LocationConstraint': AWS_REGION}
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)


def upload_file_to_s3_bucket(bucket_name, folder_name, file_name, file_content):
    s3 = boto3.client('s3')
    key = folder_name + '/' + file_name
    s3.put_object(Body=file_content, Bucket=bucket_name, Key=key)


def upload_file_to_s3(bucket_name, file_name, file_content):
    s3 = boto3.client('s3')
    key = file_name
    s3.put_object(Body=file_content, Bucket=bucket_name, Key=key)


def read_file_from_s3_bucket(bucket_name, folder_name, file_name):
    s3 = boto3.client('s3')
    key = folder_name + '/' + file_name
    response = s3.get_object(Bucket=bucket_name, Key=key)
    file_content = response['Body'].read().decode('utf-8')
    return file_content


def get_file_from_aws(bucket_name, file_name):
    s3 = boto3.client('s3')
    key = file_name
    response = s3.get_object(Bucket=bucket_name, Key=key)
    file_content = response['Body'].read().decode('utf-8')
    return file_content


def get_pdf_from_aws(bucket_name, file_name):
    s3 = boto3.client('s3')
    key = file_name
    response = s3.get_object(Bucket=bucket_name, Key=key)
    file_content = response['Body'].read()
    return file_content


def get_png_from_aws(bucket_name, file_name):
    s3 = boto3.client('s3')
    key = file_name
    response = s3.get_object(Bucket=bucket_name, Key=key)
    file_content = response['Body'].read()
    return file_content


def get_files_in_folder(bucket_name, folder_name):
    s3 = boto3.client('s3')
    prefix = folder_name + '/'
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    files = []
    if 'Contents' in response:
        for obj in response['Contents']:
            file_key = obj['Key']
            if file_key.endswith('/'):  # Skip folders
                continue
            file_name = file_key.split('/')[-1]  # Extract only the file name
            files.append(file_name)
    return files


import boto3

def read_files_in_folder(bucket_name, folder_path):
    # Create an S3 client
    s3 = boto3.client('s3')

    try:
        # List objects in the folder
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)

        if 'Contents' in response:
            files = [obj['Key'] for obj in response['Contents']]
            return files
        else:
            return []

    except Exception as e:
        print(f"Error reading files in folder '{folder_path}' in bucket '{bucket_name}': {str(e)}")
        return []



def delete_bucket(bucket_name):
    s3_res = boto3.resource('s3')
    s3_res.Bucket(bucket_name).delete()


def delete_objects_in_bucket(bucket_name):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name)
    if 'Contents' in response:
        objects = [{'Key': obj['Key']} for obj in response['Contents']]
        s3.delete_objects(Bucket=bucket_name, Delete={'Objects': objects})


def upload_pdf_to_folder(bucket_name, file_path, s3_key):
    import boto3

    # Create a Boto3 S3 client
    s3 = boto3.client('s3')
    bucket_name = bucket_name
    file_path = file_path
    s3_key = s3_key

    try:
        # Upload the file to S3
        s3.upload_file(file_path, bucket_name, s3_key)
        print("File uploaded successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def delete_object(bucket_name, s3_key):
    s3 = boto3.client('s3')
    try:
        response = s3.delete_object(Bucket=bucket_name, Key=s3_key)
        print("Object deleted successfully.")
    except Exception as e:
        print("Error:", e)