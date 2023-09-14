import os
import telebot
import private
import db_writer as db
from faq import faq_database as faq
from telebot import types

bot = telebot.TeleBot(private.token)

global nav
nav = [0, 0, 0, 0]

global current_page
global total_pages

per_page = 5
current_page = 1

@bot.message_handler(commands=['start'])
def welcome (message):
    user = message.from_user.id

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Битрикс24')
    item2 = types.KeyboardButton('Доступы к сервисам')
    item3 = types.KeyboardButton('Телефония')
    markup.add(item1, item2, item3)

    bot.send_message(user, 'Добро пожаловать!', reply_markup=generate_menu())

@bot.message_handler(commands=['admin'])
def admin_panel (message):
    user = message.from_user.id
    if user not in db.admin_list():
        db.new_admin(message=message)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Запросы Битрикс24')
    item2 = types.KeyboardButton('Запросы Доступы к сервисам')
    item3 = types.KeyboardButton('Запросы Телефония')
    markup.add(item1, item2, item3)
    
    bot.send_message(user, 'Выберите раздел.', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def menu (message):
    global nav
    user = message.from_user.id
    for section, subsections in faq.items():
        if section == message.text:
            nav = [section, 0, 0, 0]
            bot.send_message(user, f'Раздел {nav[0]}\nВыберите раздел:', reply_markup=generate_submenu())
            break

    if message.text == 'Запросы Битрикс24' or message.text == 'Запросы Доступы к сервисам' or message.text == 'Запросы Телефония':
        text = message.text.split()[1:]
        nav[0] = ' '.join(text)
        markup = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton('Открытые обращения', callback_data='opened_petition')
        button2 = types.InlineKeyboardButton('Закрытые обращения', callback_data='closed_petition')
        button3 = types.InlineKeyboardButton('Статистика', callback_data='statistic')
        markup.add(button1, button2, button3)
        bot.send_message(user, f'{nav[0]}\nЧто вы хотите сделать?', reply_markup=markup)
        
@bot.callback_query_handler(func = lambda call: True)
def callback_inline(call):
    global nav
    global petition
    global n
    global total_pages
    global current_page

    user = call.from_user.id

    if call.data == 'back' and nav[3] == 1:
        nav[3] = 0
        bot.edit_message_text(chat_id=user, message_id=call.message.id, text=f'Раздел {nav[1]}\nВыберите свой вопрос:', reply_markup=generate_questions())
    elif call.data == 'back' and nav[2] == 1:
        nav[2] = 0
        bot.edit_message_text(chat_id=user, message_id=call.message.id, text=f'Раздел {nav[0]}\nВыберите свой вопрос:', reply_markup=generate_submenu())
    elif call.data == 'help':
        msg = bot.send_message(user, 'Опишите свою проблему')
        bot.register_next_step_handler(msg, start_support)
    elif call.data == 'page_prev':
        current_page = current_page - 1
        text = nav[1].split()[1:]
        text = ' '.join(text)
        bot.edit_message_text(chat_id=user, message_id=call.message.id, text=f'Раздел {text}, страница {current_page} из {total_pages}\nВыберите свой вопрос:', reply_markup=generate_questions())
    elif call.data == 'page_next':
        current_page = current_page + 1
        text = nav[1].split()[1:]
        text = ' '.join(text)
        bot.edit_message_text(chat_id=user, message_id=call.message.id, text=f'Раздел {text}, страница {current_page} из {total_pages}\nВыберите свой вопрос:', reply_markup=generate_questions())
    elif call.data == 'opened_petition':
        petition_list(call, 'В обработке')
    elif call.data == 'closed_petition':
        petition_list(call, 'Завершено')
    elif call.data == 'close_petition':
        db.close_petition(n)
    elif call.data[0] == '#':
        n = int(call.data[1:])
        message = db.one_petition(n)
        msg = f'№{n}. {nav[0]}\n\nДата: {message[5].split()[0]}\nСтатус: {message[4]}\nТэг: @{message[1]}\n\n{message[2]}'
        markup = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton('Перейти к диалогу', url=f'https://t.me/{message[1]}?start=dialog')
        button2 = types.InlineKeyboardButton('Завершить', callback_data='close_petition')
        markup.add(button1, button2)
        if message[3] != ' ':
            bot.send_photo(user, photo=message[3], caption=msg, reply_markup=markup)
        else:
            bot.send_message(user, msg, reply_markup=markup)
    else:  
        entries = faq[nav[0]]

        if nav[2] == 0:
            for entry in entries:
                if entry.split()[0] == call.data:
                    nav[1] = entry
                    total_pages = (len(faq[nav[0]][nav[1]]) + per_page - 1) // per_page
                    current_page = 1
                    text = entry.split()[1:]
                    text = ' '.join(text)
                    bot.edit_message_text(chat_id=user, message_id=call.message.id, text=f'Раздел {text}, страница {current_page} из {total_pages}\nВыберите свой вопрос:', reply_markup=generate_questions())
                    break
        else:
            entries = faq[nav[0]][nav[1]]
            for entry in entries:
                nav[3] = 1

                question = entry['question']

                if question.split()[0] == call.data:
                    file_path = os.path.join('faq', nav[0], nav[1], question)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        question = file.read()
                    bot.edit_message_text(chat_id=user, message_id=call.message.id, text=question, reply_markup=answers_markup())
                    break

    '''match call.data:
        case 'back':
            if nav[3] == 1:
                nav[3] = 0
                bot.edit_message_text(chat_id=user, message_id=call.message.id, text=f'Раздел {nav[1]}\nВыберите свой вопрос:', reply_markup=generate_questions())
            elif nav[2] == 1:
                nav[2] = 0
                bot.edit_message_text(chat_id=user, message_id=call.message.id, text=f'Раздел {nav[0]}\nВыберите свой вопрос:', reply_markup=generate_submenu())
        case 'help':
            msg = bot.send_message(user, 'Опишите свою проблему')
            bot.register_next_step_handler(msg, start_support)
        case 'page_prev':
            current_page = current_page - 1
            text = nav[1].split()[1:]
            text = ' '.join(text)
            bot.edit_message_text(chat_id=user, message_id=call.message.id, text=f'Раздел {text}, страница {current_page} из {total_pages}\nВыберите свой вопрос:', reply_markup=generate_questions())
        case 'page_next':
            current_page = current_page + 1
            text = nav[1].split()[1:]
            text = ' '.join(text)
            bot.edit_message_text(chat_id=user, message_id=call.message.id, text=f'Раздел {text}, страница {current_page} из {total_pages}\nВыберите свой вопрос:', reply_markup=generate_questions())
        case 'opened_petition':
            petition_list(call, 'В обработке')
        case 'closed_petition':
            petition_list(call, 'Завершено')
        case 'close_petition':
            db.close_petition(n)
        case _:
            if call.data[0] == '#':
                n = int(call.data[1:])
                message = db.one_petition(n)
                msg = f'№{n}. {nav[0]}\n\nДата: {message[5].split()[0]}\nСтатус: {message[4]}\nТэг: @{message[1]}\n\n{message[2]}'
                markup = types.InlineKeyboardMarkup(row_width=1)
                button1 = types.InlineKeyboardButton('Перейти к диалогу', url=f'https://t.me/{message[1]}?start=dialog')
                button2 = types.InlineKeyboardButton('Завершить', callback_data='close_petition')
                markup.add(button1, button2)
                if message[3] != ' ':
                    bot.send_photo(user, photo=message[3], caption=msg, reply_markup=markup)
                else:
                    bot.send_message(user, msg, reply_markup=markup)
            else:  
                entries = faq[nav[0]]

                if nav[2] == 0:
                    for entry in entries:
                        if entry.split()[0] == call.data:
                            nav[1] = entry
                            total_pages = (len(faq[nav[0]][nav[1]]) + per_page - 1) // per_page
                            current_page = 1
                            text = entry.split()[1:]
                            text = ' '.join(text)
                            bot.edit_message_text(chat_id=user, message_id=call.message.id, text=f'Раздел {text}, страница {current_page} из {total_pages}\nВыберите свой вопрос:', reply_markup=generate_questions())
                            break
                else:
                    entries = faq[nav[0]][nav[1]]
                    for entry in entries:
                        nav[3] = 1

                        question = entry['question']

                        if question.split()[0] == call.data:
                            file_path = os.path.join('faq', nav[0], nav[1], question)
                            with open(file_path, 'r', encoding='utf-8') as file:
                                question = file.read()
                            bot.edit_message_text(chat_id=user, message_id=call.message.id, text=question, reply_markup=answers_markup())
                            break'''
          
def generate_menu():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
        for section, _ in faq.items():
            button_text = f'{section}'
            markup.add(types.KeyboardButton(button_text))

        return markup

def generate_submenu():
    global nav
    nav[1] = 0
    nav[2] = 0
    nav[3] = 0
    markup = types.InlineKeyboardMarkup()
    
    entries = faq[nav[0]]

    for entry in entries:
        button_text = entry.split()[1:]
        button_text = ' '.join(button_text)
        callback_data = entry.split()[0]
        markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
        
    markup.add(types.InlineKeyboardButton('Другое', callback_data='help'))
    return markup

def generate_questions():
    global current_page
    global total_pages
    global per_page
    markup = types.InlineKeyboardMarkup()
    
    nav[2] = 1

    entries = faq[nav[0]][nav[1]]
    
    start_index = (current_page - 1) * per_page
    end_index = min(current_page * per_page, len(entries))

    for entry in entries[start_index:end_index]:
        question = entry['question']
        button_text = question.split()[1:]
        button_text = ' '.join(button_text)
        callback_data = question.split()[0]
        markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))

    navigation_row = []
    if current_page > 1:
        navigation_row.append(types.InlineKeyboardButton('⬅️', callback_data=f'page_prev'))
        
    if current_page < total_pages:
        navigation_row.append(types.InlineKeyboardButton('➡️', callback_data=f'page_next'))
    
    if navigation_row:
        markup.row(*navigation_row)
    markup.add(types.InlineKeyboardButton('Назад', callback_data='back'))
    
    return markup


def answers_markup():
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Это не помогло', callback_data='help')
    button2 = types.InlineKeyboardButton('Назад', callback_data='back')
    markup.add(button1, button2)
    return markup

def start_support(message):
    global nav
    db.new_petition(message=message, nav=nav)
    bot.send_message(message.from_user.id, 'Обращение получено!\nС вами свяжется специалист.')

    for admin in db.admin_list():
        bot.send_message(admin, f'Появилось новое обращение в отделе {nav[0]}!')

def petition_list(call, status):
    global nav
    global petition
    user = call.from_user.id
    petition = db.read_petition(departament=nav[0], status=status)
    if status == 'В обработке':
        msg = f'{nav[0]}\nВсего открытых обращений: {len(petition)}'
    else:
        msg = f'{nav[0]}\nВсего закрытых обращений: {len(petition)}'

    markup = types.InlineKeyboardMarkup()

    for entry in petition:
        button_text = f'Обращение №{entry[0]}'
        callback_data = f'#{entry[0]}'
        markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))

    bot.edit_message_text(chat_id=user, message_id=call.message.id, text=msg, reply_markup=markup)
bot.infinity_polling()