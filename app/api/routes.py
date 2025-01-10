import json
from flask import request, jsonify, current_app ,send_file
from flask.ctx import AppContext
from . import api_bp
import os
from app.instai_dataflow.database import get_db_connection,get_s3_client, AWS_S3_BUCKET_NAME
from app.instai_dataflow import auth
import pymysql
import time
import random


@api_bp.route("/register_user", methods = ["POST"])
def register_user():
    ctx = current_app.app_context()

    token = request.form.get("access_token")
    ctx = current_app.app_context()

    email = auth.verify(ctx, token)
    if email is None:
        return {"err": True, "err_msg": "not verified"}
    
    user_id = request.form.get("user_id")
    character_name = request.form.get("character_name")
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            insert_sql = "INSERT INTO user_Character (user_id, create_time, character_name, grantee, grantee_state, top_up_state, gem, vip_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_sql,(
                user_id,
                create_time,
                character_name,
                0,
                0,
                0,
                0,
                0,))
            selectsql = "select * from user_Character where create_time = %s"
            cursor.execute(
                selectsql, (create_time)
            )
            character = cursor.fetchone()
            character_id = character["character_id"]
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return {"err": True, "err_msg": "create failed"}
    finally:
        conn.close()
    return {"err": False, "character_id": character_id}

@api_bp.route("/get_user_character", methods = ["POST"])
def get_user_character():
    ctx = current_app.app_context()

    token = request.form.get("access_token")
    ctx = current_app.app_context()

    email = auth.verify(ctx, token)
    if email is None:
        return {"err": True, "err_msg": "not verified"}
    
    user_id = request.form.get("user_id")
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            selectsql = "select user_id,character_id,character_name from user_Character where user_id = %s"
            cursor.execute(
                selectsql, (user_id)
            )
            character = cursor.fetchall()
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return {"err": True, "err_msg": "create failed"}
    finally:
        conn.close()
    return {"err": False, "user's character": character}

@api_bp.route("/get_character_backpack", methods = ["POST"])
def get_character_backpack():
    ctx = current_app.app_context()

    token = request.form.get("access_token")
    ctx = current_app.app_context()

    email = auth.verify(ctx, token)
    if email is None:
        return {"err": True, "err_msg": "not verified"}
    
    character_id = request.form.get("character_id")
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            selectsql = "select card.card_id,card.card_name,card.rarity,card.card_picture_path,skill.skill_name,skill.skill_cost,skill.skill_damage from backpack LEFT JOIN card on card.card_id = backpack.card_id LEFT JOIN skill on card.skill_id = skill.skill_id where character_id = %s"
            cursor.execute(
                selectsql, (character_id)
            )
            obtain_card = cursor.fetchall()
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return {"err": True, "err_msg": "create failed"}
    finally:
        conn.close()
    return {"err": False, "obtain_card": obtain_card}
    
@api_bp.route("/get_character_gacha_history", methods = ["POST"])
def get_character_gacha_history():
    ctx = current_app.app_context()

    token = request.form.get("access_token")
    ctx = current_app.app_context()

    email = auth.verify(ctx, token)
    if email is None:
        return {"err": True, "err_msg": "not verified"}
    
    character_id = request.form.get("character_id")
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            selectsql = "select card.card_id,card.card_name,gacha_history.gacha_time from gacha_history LEFT JOIN card on card.card_id = gacha_history.card_id where character_id = %s"
            cursor.execute(
                selectsql, (character_id)
            )
            gacha_history = cursor.fetchall()
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return {"err": True, "err_msg": "create failed"}
    finally:
        conn.close()
    return {"err": False, "gacha_history": gacha_history}

@api_bp.route("/get_character_list", methods = ["POST"])
def get_character_list():
    ctx = current_app.app_context()

    token = request.form.get("access_token")
    ctx = current_app.app_context()

    email = auth.verify(ctx, token)
    if email is None:
        return {"err": True, "err_msg": "not verified"}
    
    character_id = request.form.get("character_id")
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            selectsql = "select * from user_Character where character_id = %s"
            cursor.execute(
                selectsql, (character_id)
            )
            character = cursor.fetchone()
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return {"err": True, "err_msg": "get character failed"}
    finally:
        conn.close()
    return {"err": False, "character": character}

@api_bp.route("/get_card_pool", methods = ["POST"])
def get_card_pool():
    ctx = current_app.app_context()

    token = request.form.get("access_token")
    ctx = current_app.app_context()

    email = auth.verify(ctx, token)
    if email is None:
        return {"err": True, "err_msg": "not verified"}
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            selectsql = "SELECT card_pool.*,c.card_name,c.card_picture_path FROM card_pool LEFT JOIN card c ON card_pool.card_id = c.card_id"
            cursor.execute(
                selectsql
            )
            card_pool = cursor.fetchall()
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        
        return {"err": True, "err_msg": "get card_pool failed11111"}
    finally:
        conn.close()

    return {"err": False, "card_pool": card_pool}


@api_bp.route("/top_up", methods = ["POST"])
def top_up():
    ctx = current_app.app_context()

    token = request.form.get("access_token")
    ctx = current_app.app_context()

    email = auth.verify(ctx, token)
    if email is None:
        return {"err": True, "err_msg": "not verified"}

    top_up_gem = int(request.form.get("top_up_gem"))
    character_id = request.form.get("character_id")
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            search_sql = "SELECT top_up_state FROM user_Character WHERE character_id = %s"
            cursor.execute(search_sql,(
                character_id,))
            top_up_state = cursor.fetchone()
            if top_up_state["top_up_state"] == 0:
                top_up_gem = top_up_gem*2
                selectsql = "UPDATE user_Character SET top_up_state = 1 WHERE character_id = %s;"
                cursor.execute(
                    selectsql,(character_id)
                )
            selectsql = "UPDATE user_Character SET gem = gem + %s WHERE character_id = %s;"
            cursor.execute(
                selectsql,(top_up_gem,character_id)
            )
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return {"err": True, "err_msg": "top up failed"}
    finally:
        conn.close()
    return {"err": False, "top_up_gem": top_up_gem}

@api_bp.route("/gacha_once", methods = ["POST"])
def gacha_once():
    ctx = current_app.app_context()

    token = request.form.get("access_token")
    ctx = current_app.app_context()

    email = auth.verify(ctx, token)
    if email is None:
        return {"err": True, "err_msg": "not verified"}
    
    card_pool_id = request.form.get("card_pool_id")
    character_id = request.form.get("character_id")
    gacha_result = gacha(card_pool_id,character_id)
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            update_sql = "UPDATE user_Character SET gem = gem - 160 WHERE character_id = %s;"
            cursor.execute(
                update_sql,(character_id)
            )
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return {"err": True, "err_msg": "gacha failed"}
    finally:
        conn.close()
    return gacha_result

@api_bp.route("/gacha_ten_times", methods = ["POST"])
def gacha_ten_times():
    ctx = current_app.app_context()

    token = request.form.get("access_token")
    ctx = current_app.app_context()

    email = auth.verify(ctx, token)
    if email is None:
        return {"err": True, "err_msg": "not verified"}
    
    card_pool_id = request.form.get("card_pool_id")
    character_id = request.form.get("character_id")

    total_gacha_result = gacha_ten_times(card_pool_id,character_id)
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            update_sql = "UPDATE user_Character SET gem = gem - 1600 WHERE character_id = %s;"
            cursor.execute(
                update_sql,(character_id)
            )
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return {"err": True, "err_msg": "get card_pool failed"}
    finally:
        conn.close()
    
    return total_gacha_result
    
    
def gacha(card_pool_id,character_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            selectsql = "SELECT * FROM user_Character WHERE character_id = %s"
            cursor.execute(
                selectsql, (character_id)
            )
            character = cursor.fetchone()
            if character["gem"] < 160:
                return {"err": True, "gacha_result": "gem is not enough"}
            selectsql = "SELECT * FROM card_pool LEFT JOIN card ON card_pool.card_id = card.card_id WHERE card_pool_id = %s"
            cursor.execute(
                selectsql,(card_pool_id)
            )
            card_pool = cursor.fetchone()
            low_rarity_probability = card_pool["low_rarity_probability"]
            medium_rarity_probability = card_pool["medium_rarity_probability"]
            if character["grantee"] >= 79:
                if character["grantee_state"] == 0:
                    random_process = random.uniform(1, 0)
                    if random_process < 0.5:
                        selectsql = "SELECT card.card_id,card.card_name,card.rarity,card.card_picture_path FROM standard_pool LEFT JOIN card ON standard_pool.card_id = card.card_id WHERE card.rarity = %s"
                        cursor.execute(
                            selectsql,(3)
                        )
                        result_all = cursor.fetchall()
                        result = random.choice(result_all)
                        selectsql = "UPDATE user_Character SET grantee = 0 WHERE character_id = %s"
                        cursor.execute(
                            selectsql,(character_id)
                        )
                        selectsql = "UPDATE user_Character SET grantee_state = 1 WHERE character_id = %s"
                        cursor.execute(
                            selectsql,(character_id)
                        )
                        selectsql = "SELECT * FROM user_Character WHERE character_id = %s"
                        cursor.execute(
                            selectsql, (character_id)
                        )
                        character = cursor.fetchone()
                        insert_sql = "INSERT INTO gacha_history (gacha_time, character_id, card_id) VALUES (%s, %s, %s)"
                        cursor.execute(insert_sql,(
                            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            character_id,
                            result["card_id"],))
                        search_sql = "SELECT * FROM backpack WHERE character_id = %s and card_id = %s"
                        cursor.execute(search_sql,(
                            character_id,
                            result["card_id"],))
                        if cursor.fetchone() == None:
                            insert_sql = "INSERT INTO backpack (character_id, card_id) VALUES (%s, %s)"
                            cursor.execute(insert_sql,(
                                character_id,
                                result["card_id"],))
                        conn.commit()
                        return {"err": False, "gacha_result": result, "grantee":character["grantee"], "grantee_state":character["grantee_state"]}
                    else:
                        selectsql = "SELECT card.card_id,card.card_name,card.rarity,card.card_picture_path FROM card_pool LEFT JOIN card ON card_pool.card_id = card.card_id WHERE card_pool_id = %s"
                        cursor.execute(
                                selectsql,(card_pool_id)
                            )
                        result = cursor.fetchone()
                        selectsql = "UPDATE user_Character SET grantee = 0 WHERE character_id = %s"
                        cursor.execute(
                            selectsql,(character_id)
                        )
                        selectsql = "UPDATE user_Character SET grantee_state = 0 WHERE character_id = %s"
                        cursor.execute(
                            selectsql,(character_id)
                        )
                        selectsql = "SELECT * FROM user_Character WHERE character_id = %s"
                        cursor.execute(
                            selectsql, (character_id)
                        )
                        character = cursor.fetchone()
                        insert_sql = "INSERT INTO gacha_history (gacha_time, character_id, card_id) VALUES (%s, %s, %s)"
                        cursor.execute(insert_sql,(
                            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            character_id,
                            result["card_id"],))
                        search_sql = "SELECT * FROM backpack WHERE character_id = %s and card_id = %s"
                        cursor.execute(search_sql,(
                            character_id,
                            result["card_id"],))
                        if cursor.fetchone() == None:
                            insert_sql = "INSERT INTO backpack (character_id, card_id) VALUES (%s, %s)"
                            cursor.execute(insert_sql,(
                                character_id,
                                result["card_id"],))
                        conn.commit()
                        return {"err": False, "gacha_result": result, "grantee":character["grantee"], "grantee_state":character["grantee_state"]}
                    
                else:
                    selectsql = "SELECT card.card_id,card.card_name,card.rarity,card.card_picture_path FROM card_pool LEFT JOIN card ON card_pool.card_id = card.card_id WHERE card_pool_id = %s"
                    cursor.execute(
                        selectsql,(card_pool_id)
                    )
                    result = cursor.fetchone()
                    selectsql = "UPDATE user_Character SET grantee = 0 WHERE character_id = %s"
                    cursor.execute(
                        selectsql,(character_id)
                    )
                    selectsql = "UPDATE user_Character SET grantee_state = 0 WHERE character_id = %s"
                    cursor.execute(
                        selectsql,(character_id)
                    )
                    selectsql = "SELECT * FROM user_Character WHERE character_id = %s"
                    cursor.execute(
                        selectsql, (character_id)
                    )
                    character = cursor.fetchone()
                    insert_sql = "INSERT INTO gacha_history (gacha_time, character_id, card_id) VALUES (%s, %s, %s)"
                    cursor.execute(insert_sql,(
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        character_id,
                        result["card_id"],))
                    search_sql = "SELECT * FROM backpack WHERE character_id = %s and card_id = %s"
                    cursor.execute(search_sql,(
                        character_id,
                        result["card_id"],))
                    if cursor.fetchone() == None:
                        insert_sql = "INSERT INTO backpack (character_id, card_id) VALUES (%s, %s)"
                        cursor.execute(insert_sql,(
                            character_id,
                            result["card_id"],))
                    conn.commit()
                    return {"err": False, "gacha_result": result, "grantee":character["grantee"], "grantee_state":character["grantee_state"]}

            else:
                random_process = random.uniform(1, 0)
                if random_process >= 0 and random_process <= low_rarity_probability:
                    selectsql = "SELECT card.card_id,card.card_name,card.rarity,card.card_picture_path FROM standard_pool LEFT JOIN card ON standard_pool.card_id = card.card_id WHERE card.rarity = %s"
                    cursor.execute(
                        selectsql,(1)
                    )
                    result_all = cursor.fetchall()
                    result = random.choice(result_all)
                    insert_sql = "INSERT INTO gacha_history (gacha_time, character_id, card_id) VALUES (%s, %s, %s)"
                    cursor.execute(insert_sql,(
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        character_id,
                        result["card_id"],))
                    search_sql = "SELECT * FROM backpack WHERE character_id = %s and card_id = %s"
                    cursor.execute(search_sql,(
                        character_id,
                        result["card_id"],))
                    if cursor.fetchone() == None:
                        insert_sql = "INSERT INTO backpack (character_id, card_id) VALUES (%s, %s)"
                        cursor.execute(insert_sql,(
                            character_id,
                            result["card_id"],))
                elif random_process >= low_rarity_probability and random_process <= low_rarity_probability+medium_rarity_probability:
                    selectsql = "SELECT card.card_id,card.card_name,card.rarity,card.card_picture_path FROM standard_pool LEFT JOIN card ON standard_pool.card_id = card.card_id WHERE card.rarity = %s"
                    cursor.execute(
                        selectsql,(2)
                    )
                    result_all = cursor.fetchall()
                    result = random.choice(result_all)
                    insert_sql = "INSERT INTO gacha_history (gacha_time, character_id, card_id) VALUES (%s, %s, %s)"
                    cursor.execute(insert_sql,(
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        character_id,
                        result["card_id"],))
                    search_sql = "SELECT * FROM backpack WHERE character_id = %s and card_id = %s"
                    cursor.execute(search_sql,(
                        character_id,
                        result["card_id"],))
                    if cursor.fetchone() == None:
                        insert_sql = "INSERT INTO backpack (character_id, card_id) VALUES (%s, %s)"
                        cursor.execute(insert_sql,(
                            character_id,
                            result["card_id"],))
                else:
                    if character["grantee_state"] == 0:
                        random_process = random.uniform(1, 0)
                        if random_process < 0.5:
                            selectsql = "SELECT card.card_id,card.card_name,card.rarity,card.card_picture_path FROM standard_pool LEFT JOIN card ON standard_pool.card_id = card.card_id WHERE card.rarity = %s"
                            cursor.execute(
                                selectsql,(3)
                            )
                            result_all = cursor.fetchall()
                            result = random.choice(result_all)
                            selectsql = "UPDATE user_Character SET grantee = 0 WHERE character_id = %s"
                            cursor.execute(
                                selectsql,(character_id)
                            )
                            selectsql = "UPDATE user_Character SET grantee_state = 1 WHERE character_id = %s"
                            cursor.execute(
                                selectsql,(character_id)
                            )
                            selectsql = "SELECT * FROM user_Character WHERE character_id = %s"
                            cursor.execute(
                                selectsql, (character_id)
                            )
                            character = cursor.fetchone()
                            insert_sql = "INSERT INTO gacha_history (gacha_time, character_id, card_id) VALUES (%s, %s, %s)"
                            cursor.execute(insert_sql,(
                                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                character_id,
                                result["card_id"],))
                            search_sql = "SELECT * FROM backpack WHERE character_id = %s and card_id = %s"
                            cursor.execute(search_sql,(
                                character_id,
                                result["card_id"],))
                            if cursor.fetchone() == None:
                                insert_sql = "INSERT INTO backpack (character_id, card_id) VALUES (%s, %s)"
                                cursor.execute(insert_sql,(
                                    character_id,
                                result["card_id"],))
                            conn.commit()
                            
                            return {"err": False, "gacha_result": result, "grantee":character["grantee"], "grantee_state":character["grantee_state"]}
                        else:
                            selectsql = "SELECT card.card_id,card.card_name,card.rarity,card.card_picture_path FROM card_pool LEFT JOIN card ON card_pool.card_id = card.card_id WHERE card_pool_id = %s"
                            cursor.execute(
                                selectsql,(card_pool_id)
                            )
                            result = cursor.fetchone()
                            selectsql = "UPDATE user_Character SET grantee = 0 WHERE character_id = %s"
                            cursor.execute(
                                selectsql,(character_id)
                            )
                            selectsql = "UPDATE user_Character SET grantee_state = 0 WHERE character_id = %s"
                            cursor.execute(
                                selectsql,(character_id)
                            )
                            selectsql = "SELECT * FROM user_Character WHERE character_id = %s"
                            cursor.execute(
                                selectsql, (character_id)
                            )
                            character = cursor.fetchone()
                            insert_sql = "INSERT INTO gacha_history (gacha_time, character_id, card_id) VALUES (%s, %s, %s)"
                            cursor.execute(insert_sql,(
                                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                character_id,
                                result["card_id"],))
                            search_sql = "SELECT * FROM backpack WHERE character_id = %s and card_id = %s"
                            cursor.execute(search_sql,(
                                character_id,
                                result["card_id"],))
                            if cursor.fetchone() == None:
                                insert_sql = "INSERT INTO backpack (character_id, card_id) VALUES (%s, %s)"
                                cursor.execute(insert_sql,(
                                    character_id,
                                    result["card_id"],))
                            conn.commit()
                            return {"err": False, "gacha_result": result, "grantee":character["grantee"], "grantee_state":character["grantee_state"]}
                        
                    else:
                        selectsql = "SELECT card.card_id,card.card_name,card.rarity,card.card_picture_path FROM card_pool LEFT JOIN card ON card_pool.card_id = card.card_id WHERE card_pool_id = %s"
                        cursor.execute(
                            selectsql,(card_pool_id)
                        )
                        result = cursor.fetchone()
                        selectsql = "UPDATE user_Character SET grantee = 0 WHERE character_id = %s"
                        cursor.execute(
                            selectsql,(character_id)
                        )
                        selectsql = "UPDATE user_Character SET grantee_state = 0 WHERE character_id = %s"
                        cursor.execute(
                            selectsql,(character_id)
                        )
                        selectsql = "SELECT * FROM user_Character WHERE character_id = %s"
                        cursor.execute(
                            selectsql, (character_id)
                        )
                        character = cursor.fetchone()
                        insert_sql = "INSERT INTO gacha_history (gacha_time, character_id, card_id) VALUES (%s, %s, %s)"
                        cursor.execute(insert_sql,(
                            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            character_id,
                            result["card_id"],))
                        search_sql = "SELECT * FROM backpack WHERE character_id = %s and card_id = %s"
                        cursor.execute(search_sql,(
                            character_id,
                            result["card_id"],))
                        if cursor.fetchone() == None:
                            insert_sql = "INSERT INTO backpack (character_id, card_id) VALUES (%s, %s)"
                            cursor.execute(insert_sql,(
                                character_id,
                                result["card_id"],))
                        conn.commit()
                        return {"err": False, "gacha_result": result, "grantee":character["grantee"], "grantee_state":character["grantee_state"]}
                
                selectsql = "UPDATE user_Character SET grantee = grantee + 1 WHERE character_id = %s;"
                cursor.execute(
                    selectsql,(character_id)
                )
                selectsql = "SELECT * FROM user_Character WHERE character_id = %s"
                cursor.execute(
                    selectsql, (character_id)
                )
                character = cursor.fetchone()
            
                
        
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return {"err": True, "err_msg": "get character failed"}
    finally:
        conn.close()
    
    return {"err": False, "gacha_result": result, "grantee":character["grantee"], "grantee_state":character["grantee_state"]}

def gacha_ten_times(card_pool_id,character_id):
    conn = get_db_connection()
    total_gacha_result = []
    try:
        for i in range(0,10):
            with conn.cursor() as cursor:
                selectsql = "SELECT * FROM user_Character WHERE character_id = %s"
                cursor.execute(
                    selectsql, (character_id)
                )
                character = cursor.fetchone()
                selectsql = "SELECT * FROM card_pool LEFT JOIN card ON card_pool.card_id = card.card_id WHERE card_pool_id = %s"
                cursor.execute(
                    selectsql,(card_pool_id)
                )
                card_pool = cursor.fetchone()
                low_rarity_probability = card_pool["low_rarity_probability"]
                medium_rarity_probability = card_pool["medium_rarity_probability"]
                if character["grantee"] >= 79:
                    if character["grantee_state"] == 0:
                        random_process = random.uniform(1, 0)
                        if random_process < 0.5:
                            selectsql = "SELECT card.card_id,card.card_name,card.rarity,card.card_picture_path FROM standard_pool LEFT JOIN card ON standard_pool.card_id = card.card_id WHERE card.rarity = %s"
                            cursor.execute(
                                selectsql,(3)
                            )
                            result_all = cursor.fetchall()
                            result = random.choice(result_all)
                            selectsql = "UPDATE user_Character SET grantee = 0 WHERE character_id = %s"
                            cursor.execute(
                                selectsql,(character_id)
                            )
                            selectsql = "UPDATE user_Character SET grantee_state = 1 WHERE character_id = %s"
                            cursor.execute(
                                selectsql,(character_id)
                            )
                            character = cursor.fetchone()
                            total_gacha_result.append(result)
                            conn.commit()
                            continue
                        else:
                            selectsql = "SELECT card.card_id,card.card_name,card.rarity,card.card_picture_path FROM card_pool LEFT JOIN card ON card_pool.card_id = card.card_id WHERE card_pool_id = %s"
                            cursor.execute(
                                    selectsql,(card_pool_id)
                                )
                            result = cursor.fetchone()
                            selectsql = "UPDATE user_Character SET grantee = 0 WHERE character_id = %s"
                            cursor.execute(
                                selectsql,(character_id)
                            )
                            selectsql = "UPDATE user_Character SET grantee_state = 0 WHERE character_id = %s"
                            cursor.execute(
                                selectsql,(character_id)
                            )
                            character = cursor.fetchone()
                            total_gacha_result.append(result)
                            conn.commit()
                            continue
                        
                    else:
                        selectsql = "SELECT card.card_id,card.card_name,card.rarity,card.card_picture_path FROM card_pool LEFT JOIN card ON card_pool.card_id = card.card_id WHERE card_pool_id = %s"
                        cursor.execute(
                            selectsql,(card_pool_id)
                        )
                        result = cursor.fetchone()
                        selectsql = "UPDATE user_Character SET grantee = 0 WHERE character_id = %s"
                        cursor.execute(
                            selectsql,(character_id)
                        )
                        selectsql = "UPDATE user_Character SET grantee_state = 0 WHERE character_id = %s"
                        cursor.execute(
                            selectsql,(character_id)
                        )
                        character = cursor.fetchone()
                        total_gacha_result.append(result)
                        conn.commit()
                        continue

                else:
                    random_process = random.uniform(1, 0)
                    if random_process >= 0 and random_process <= low_rarity_probability:
                        selectsql = "SELECT card.card_id,card.card_name,card.rarity,card.card_picture_path FROM standard_pool LEFT JOIN card ON standard_pool.card_id = card.card_id WHERE card.rarity = %s"
                        cursor.execute(
                            selectsql,(1)
                        )
                        result_all = cursor.fetchall()
                        result = random.choice(result_all)
                    elif random_process >= low_rarity_probability and random_process <= low_rarity_probability+medium_rarity_probability:
                        selectsql = "SELECT card.card_id,card.card_name,card.rarity,card.card_picture_path FROM standard_pool LEFT JOIN card ON standard_pool.card_id = card.card_id WHERE card.rarity = %s"
                        cursor.execute(
                            selectsql,(2)
                        )
                        result_all = cursor.fetchall()
                        result = random.choice(result_all)
                    else:
                        if character["grantee_state"] == 0:
                            random_process = random.uniform(1, 0)
                            if random_process < 0.5:
                                selectsql = "SELECT card.card_id,card.card_name,card.rarity,card.card_picture_path FROM standard_pool LEFT JOIN card ON standard_pool.card_id = card.card_id WHERE card.rarity = %s"
                                cursor.execute(
                                    selectsql,(3)
                                )
                                result_all = cursor.fetchall()
                                result = random.choice(result_all)
                                selectsql = "UPDATE user_Character SET grantee = 0 WHERE character_id = %s"
                                cursor.execute(
                                    selectsql,(character_id)
                                )
                                selectsql = "UPDATE user_Character SET grantee_state = 1 WHERE character_id = %s"
                                cursor.execute(
                                    selectsql,(character_id)
                                )
                                character = cursor.fetchone()
                                total_gacha_result.append(result)
                                conn.commit()
                                continue
                            else:
                                selectsql = "SELECT card.card_id,card.card_name,card.rarity,card.card_picture_path FROM card_pool LEFT JOIN card ON card_pool.card_id = card.card_id WHERE card_pool_id = %s"
                                cursor.execute(
                                    selectsql,(card_pool_id)
                                )
                                result = cursor.fetchone()
                                selectsql = "UPDATE user_Character SET grantee = 0 WHERE character_id = %s"
                                cursor.execute(
                                    selectsql,(character_id)
                                )
                                selectsql = "UPDATE user_Character SET grantee_state = 0 WHERE character_id = %s"
                                cursor.execute(
                                    selectsql,(character_id)
                                )
                                character = cursor.fetchone()
                                total_gacha_result.append(result)
                                conn.commit()
                                continue
                            
                        else:
                            selectsql = "SELECT card.card_id,card.card_name,card.rarity,card.card_picture_path FROM card_pool LEFT JOIN card ON card_pool.card_id = card.card_id WHERE card_pool_id = %s"
                            cursor.execute(
                                selectsql,(card_pool_id)
                            )
                            result = cursor.fetchone()
                            selectsql = "UPDATE user_Character SET grantee = 0 WHERE character_id = %s"
                            cursor.execute(
                                selectsql,(character_id)
                            )
                            selectsql = "UPDATE user_Character SET grantee_state = 0 WHERE character_id = %s"
                            cursor.execute(
                                selectsql,(character_id)
                            )
                            character = cursor.fetchone()
                            total_gacha_result.append(result)
                            conn.commit()
                            continue
                    
                    selectsql = "UPDATE user_Character SET grantee = grantee + 1 WHERE character_id = %s;"
                    cursor.execute(
                        selectsql,(character_id)
                    )
                
                selectsql = "SELECT * FROM user_Character WHERE character_id = %s"
                cursor.execute(
                    selectsql, (character_id)
                )
                character = cursor.fetchone()
                total_gacha_result.append(result)

        with conn.cursor() as cursor:
            for i in range(0,10):
                print(i)
                insert_sql = "INSERT INTO gacha_history (gacha_time, character_id, card_id) VALUES (%s, %s, %s)"
                cursor.execute(insert_sql,(
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    character_id,
                    total_gacha_result[i]["card_id"],))
                print(i)
                search_sql = "SELECT * FROM backpack WHERE character_id = %s and card_id = %s"
                cursor.execute(search_sql,(
                    character_id,
                    total_gacha_result[i]["card_id"],))
                search_result = cursor.fetchone()
                print(i)
                if search_result == None:
                    insert_sql = "INSERT INTO backpack (character_id, card_id) VALUES (%s, %s)"
                    cursor.execute(insert_sql,(
                        character_id,
                        total_gacha_result[i]["card_id"],))

            
        
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return {"err": True, "err_msg": "get character failed"}
    finally:
        conn.close()

    return {"err": False, "gacha_result": total_gacha_result, "grantee":character["grantee"], "grantee_state":character["grantee_state"]}