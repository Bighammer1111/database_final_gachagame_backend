"""Copyright 2024 Instai.co
"""

from datetime import datetime, timedelta
from typing import Union
import re
import hashlib
import binascii
import jwt
from flask.ctx import AppContext
import pymysql
import boto3
from botocore.exceptions import ClientError
from app.instai_dataflow.ses_config.ses_identity import SesIdentity
from app.instai_dataflow.database import (
    get_db_connection,
    get_s3_client,
    AWS_S3_BUCKET_NAME,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION
)


def signup(ctx: AppContext, firstname: str, lastname: str, email: str, password: str,
           password_check: str, role: str) -> dict:
    """signup

    Args:
        ctx (AppContext): context.
        firstname (str): firstname.
        lastname (str): lastname.
        email (str): email.
        password (str): password.
        password_check (str): password, should equal to password.
        role (str): user role
    Returns:
        dict: response payload.
    """
    if not firstname:
        return {"err": True, "err_msg": "firstname needs to have at least one string"}
    if not lastname:
        return {"err": True, "err_msg": "lastname needs to have at least one string"}
    if not password:
        return {"err": True, "err_msg": "password needs to have at least one string"}
    if not email:
        return {"err": True, "err_msg": "email needs to have at least one string"}
    if password != password_check:
        return {"err": True, "err_msg": "password != password_check"}
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return {"err": True, "err_msg": "email format is incorrect"}

    ses_client = boto3.client(
        "ses",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    ses_identity = SesIdentity(ses_client)
    
    status = ses_identity.get_identity_status(email)
    if status != "Success":
        try:
            ses_identity.verify_email_identity(email)
            return {
                "err": True,
                "err_msg": "Verification email sent. Please verify your email before signing up."
            }
        except ClientError as e:
            print(f"Error sending verification email: {e}")
            return {"err": True, "err_msg": "Failed to send verification email"}

    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                                          ctx.app.secret_key.encode('utf-8'), 32000, 16)
    hashed_password_hex = binascii.hexlify(hashed_password).decode('utf-8')
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            select_sql = "SELECT * FROM Users WHERE email=%s"
            cursor.execute(select_sql, (email,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                return {"err": True, "err_msg": "email already exists"}
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            if not role:
                role = 'normal_user'
            sql = "INSERT INTO Users (firstname, lastname, email, password, createtime, role) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (firstname, lastname, email, hashed_password_hex, timestamp, role))
            userid = cursor.lastrowid
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return {"err": True, "err_msg": "signup failed"}
    finally:
        conn.close()
    
    try:
        s3_client = get_s3_client()
        s3_client.put_object(Bucket=AWS_S3_BUCKET_NAME, Key=f'uploads/{userid}/')
    except Exception as e:
        print(f"Error creating S3 folder: {e}")

    return {"err": False, "err_msg": "signup completed"}


def signin(ctx: AppContext, email: str, password: str) -> dict:
  """signin

  Args:
      ctx (AppContext): context.
      username (str): username.
      email (str): email.
      password (str): passwor.

  Returns:
      dict: response payload.
  """
  conn = get_db_connection()
  user = None
  try:
    with conn.cursor() as cursor:
        # 查詢資料庫，根據電子郵件查找用戶
        sql = "SELECT * FROM Users WHERE email=%s"
        cursor.execute(sql, (email,))
        user = cursor.fetchone()
  except pymysql.MySQLError as e:
      print(f"Error: {e}")
  finally:
      conn.close()

  if user is None:
    return {"err": True, "err_msg": "user not found"}
  hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                                          ctx.app.secret_key.encode('utf-8'),
                                          32000, 16)
  hashed_password_hex = binascii.hexlify(hashed_password).decode('utf-8')
  if user['password'] != hashed_password_hex:
    return {"err": True, "err_msg": "incorrect password"}

  userid = user['id']
  role = user['role']
  token = jwt.encode(
      {
          "userid": userid,
          "email": email,
          "role": role,
          "exp": datetime.utcnow() + timedelta(hours=2)
      },
      ctx.app.secret_key,
      algorithm='HS256')

  return {"err": False, "err_msg": "signin success", "token": token, "user_id": userid, "role": role}


def get_user(ctx: AppContext, token: str) -> dict:
  """get all user's info.

  Args:
      ctx (AppContext): context.
      token (str): token.

  Returns:
      dict: response.
  """
  email = verify(ctx, token)
  if email is None:
    return {"err": True, "err_msg": "not verified"}
  conn = get_db_connection()
  users = None
  try:
      with conn.cursor() as cursor:
          selectsql = "select id, firstname, lastname, email, password, role, createtime from Users where role != %s"
          cursor.execute(selectsql, ('admin_user',))
          users = cursor.fetchall()
  except pymysql.MySQLError as e:
      print(f"Error: {e}")
      return {"err": True, "err_msg": "select sql failed"}
  finally:
      conn.close()
  if users is None:
    return {"err": True, "err_msg": "project not found"}

  user_list = []
  for user in users:
      user_list.append({
          "id": user['id'],
          "firstname": user['firstname'],
          "lastname": user['lastname'],
          "email": user['email'],
          "password": user['password'],
          "role": user['role'],
          "createtime": user['createtime']
      })

  return {"err": False, "err_msg": "success", "user_list": user_list}


def modify_user(ctx: AppContext, token: str, role: str, firstname: str, lastname: str, email: str, password: str, userid: int) -> dict:
  """modify user info.

  Args:
      ctx (AppContext): context.
      token (str): token.
      project_id (str): project id.

  Returns:
      dict: response.
  """
  emails = verify(ctx, token)
  if emails is None:
    return {"err": True, "err_msg": "not verified"}
  hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                                          ctx.app.secret_key.encode('utf-8'), 32000, 16)
  hashed_password_hex = binascii.hexlify(hashed_password).decode('utf-8')
  conn = get_db_connection()
  try:
      with conn.cursor() as cursor:
          timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
          updatesql = "update Users set role = %s , firstname = %s, lastname = %s, email = %s, password = %s, LastUpdated = %s where id = %s"
          cursor.execute(updatesql, (role,firstname,lastname,email,hashed_password_hex,timestamp,userid))
          conn.commit()
          return {"err": False, "err_msg": "update user's information success"}
  except pymysql.MySQLError as e:
      print(f"Error: {e}")
      return {"err": True, "err_msg": "update sql failed"}
  finally:
      conn.close()


def delete_user(ctx: AppContext, token: str, userid: int) -> dict:
  """Delete project.

  Args:
      ctx (AppContext): context.
      token (str): token.
      project_id (str): project id.

  Returns:
      dict: response.
  """
  email = verify(ctx, token)
  if email is None:
    return {"err": True, "err_msg": "not verified"}

  conn = get_db_connection()
  try:
      with conn.cursor() as cursor:
          #delete user's all projects
          delsql = "delete from  Projects where user_id = %s"
          cursor.execute(delsql, (userid,))
          #delete user's all requirements
          delreqsql = "delete from  Requirements where uploader = %s"
          cursor.execute(delreqsql, (userid,))
          #delete user's all images
          delimsql = "delete from  Images where uploader = %s"
          cursor.execute(delimsql, (userid,))

          #delete user
          delpsql = "delete from  Users where id = %s"
          cursor.execute(delpsql, (userid,))
      conn.commit()
  except pymysql.MySQLError as e:
      print(f"Error: {e}")
      return {"err": True, "err_msg": "user deletion failed"}
  finally:
      conn.close()
  # 删除指定路徑資料夾及其内容
  folder_path = 'uploads/' + str(userid) + '/'
  s3 = get_s3_client()
  paginator = s3.get_paginator('list_objects_v2')
  pages = paginator.paginate(Bucket=AWS_S3_BUCKET_NAME, Prefix=folder_path)

  delete_us = dict(Objects=[])
  for page in pages:
      for obj in page.get('Contents', []):
          delete_us['Objects'].append(dict(Key=obj['Key']))

  if delete_us['Objects']:
      s3.delete_objects(Bucket=AWS_S3_BUCKET_NAME, Delete=delete_us)

  return {"err": False, "err_msg": "delete User success"}


def verify(ctx: AppContext, token: str) -> Union[str, None]:
  """Verify the token.

  Args:
      ctx (AppContext): context.
      token (str): token.

  Returns:
      Union[str, None]: email.
  """
  email = None
  try:
    email = jwt.decode(token, ctx.app.secret_key, algorithms=['HS256'])['email']
  except Exception as e:
    pass
  return email