"""Copyright 2024 Instai.co
"""
import os
import datetime
import enum
import pymysql
import flask_sqlalchemy
import boto3
from dotenv import load_dotenv
db = flask_sqlalchemy.SQLAlchemy()
import time


# 加載環境變數
env_path = os.path.join(os.path.dirname(__file__), './.env')
load_dotenv(env_path)
AWS_RDS_HOST = os.getenv('AWS_RDS_HOST')
RDS_PORT = int(os.getenv('RDS_PORT', 3306))
AWS_RDS_USERNAME = os.getenv('AWS_RDS_USERNAME')
AWS_RDS_PASSWORD = os.getenv('AWS_RDS_PASSWORD')
RDS_DATABASE = os.getenv('RDS_DATABASE')
AWS_REGION = os.getenv('AWS_REGION')
AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
ADMINEMAIL = os.getenv('REACT_APP_EMAIL')
ADMINPASSWORD = os.getenv('REACT_APP_PASSWORD')
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 連接到 S3
def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )


# 連接到 RDS 資料庫
def get_db_connection():
    ca_path = os.path.join(BASE_DIR, 'us-east-1-bundle.pem')
    return pymysql.connect(
        host=AWS_RDS_HOST,
        port=RDS_PORT,
        user=AWS_RDS_USERNAME,
        password=AWS_RDS_PASSWORD,
        database=RDS_DATABASE,
        ssl={'ca': ca_path},
        cursorclass=pymysql.cursors.DictCursor
    )

def start_style_transform_ec2():
    ec2_client = boto3.client('ec2',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

    # 要启动的实例 ID 列表
    instance_id = 'i-0e039003969e12dd3'  # 替换为你要启动的实例ID


    ec2_client.start_instances(InstanceIds=[instance_id])

    
    
    ssm_client = boto3.client('ssm')
    command_script = '''
        cd /home/ubuntu/style_transform_api

        docker-compose up -d

        while ! docker ps | grep -q style_transform_api; do
            echo "等待容器启动中..."
            sleep 2
        done

        echo "Docker 容器已启动"
        '''
    
    while True:
        time.sleep(5)
        response = ec2_client.describe_instance_status(InstanceIds=[instance_id])
        instance_status = response['InstanceStatuses']
        print(instance_status)
        system_status = instance_status[0]['SystemStatus']['Status']
        instance_status_check = instance_status[0]['InstanceStatus']['Status']
        print('waiting for runing')
        if system_status == 'ok' and instance_status_check == 'ok':
            print('server have been runing')
            break


    
    response = ssm_client.send_command(
    InstanceIds=[instance_id],  # EC2 实例ID
    DocumentName="AWS-RunShellScript",  # 如果是 Windows 实例，使用 "AWS-RunPowerShellScript"
    Parameters={
        'commands': [command_script]  # 要执行的命令
    }
    )

    # 获取命令ID
    command_id = response['Command']['CommandId']
    print(f'Command ID: {command_id}')
    # 等待命令执行完成
    time.sleep(10)

    # 检查命令执行状态，直到命令完成
    status = 'Pending'
    while status not in ['Success', 'Failed', 'Cancelled', 'TimedOut']:
        time.sleep(5)
        output = ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=instance_id
        )
        status = output['Status']
        print(f"Command Status: {status}")
    # 获取命令执行的输出
    response_after = ssm_client.get_command_invocation(
        CommandId=command_id,
        InstanceId=instance_id
    )

    return response_after
