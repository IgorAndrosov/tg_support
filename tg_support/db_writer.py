import sqlite3
import telebot
import private
import datetime
from telebot import types

bot = telebot.TeleBot(private.token)

conn = sqlite3.connect('db/db.db', check_same_thread=False)
cursor = conn.cursor()

def new_petition(message, nav):
    current_datetime = datetime.datetime.now()
    current_datetime = current_datetime.strftime('%d.%m.%y %H:%M:%S')
    photo_id = ' '
    message_text = ' '
    if message.text:
        message_text = message.text
    if message.photo:
        photo_id = message.photo[0].file_id
    cursor.execute('insert into petition (username, message, photo_id, start_time, departament) values(?,?,?,?,?)', (message.from_user.username, message_text, photo_id, current_datetime,nav[0],))
    conn.commit()

def read_petition(departament, status):
    cursor.execute(f"select * from petition where departament = ? and status = ?", (departament, status))
    result = cursor.fetchall()
    conn.commit()
    return result

def one_petition(numer):
    cursor.execute(f'select * from petition where id = {numer}')
    result = cursor.fetchone()
    conn.commit()

    return result

def close_petition(numer):
    current_datetime = datetime.datetime.now()
    current_datetime = current_datetime.strftime('%d.%m.%y %H:%M:%S')
    status = 'Завершено'
    cursor.execute('update petition set status = ?, end_time = ? where id = ?', (status, current_datetime, numer))
    conn.commit()

def admin_list():
    cursor.execute('select user_id from admins')
    result = cursor.fetchall()
    conn.commit()
    if not result:
        result = [1]
        return result
    else:
        return result[0]

def new_admin(message):
    cursor.execute('insert into admins (user_id, user_name) values (?,?)', (message.from_user.id, message.from_user.first_name))
    conn.commit()