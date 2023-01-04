import asyncio
import multiprocessing

from pywebio import start_server, config
from pywebio.input import *
from pywebio.output import *
from pywebio.session import defer_call, info as session_info, run_async, run_js


chat_msgs = []
online_users = set()
MAX_MESSAGES_COUNT = 100
prt = 8080

mode_list = ['📱', '💻', '🖥'] # Режим чата

# Тема
def open_theme():
    f = open('usr_thm.txt', 'r')
    user_theme = f.read()
    f.close()
    return user_theme

# Чат
def wb():
    # Проверка занятого имени
    def check_user(n):
        for i in mode_list:
            if f'{i} {n}' in online_users or n == '📢':
                return "Такой ник уже занят!"
        else:
            return None

    # Проверка сообщения
    def check_message(m):
        if m["cmd"] == "Отправить" and m['msg'] == '':
            return ('msg', "Введите текст сообщения!")
        elif m["cmd"] == "Громче":
            m['msg'] = 'Сделай громче'
        elif m["cmd"] == "Тише":
            m['msg'] = 'Сделай тише'
        elif m["cmd"] == "Меня":
            m['msg'] = 'МЕНЯ'
        elif m["cmd"] == "Остальных":
            m['msg'] = 'остальных'
        elif m["cmd"] == "👍":
            m['msg'] = '👍'
        elif m["cmd"] == "👍":
            m['msg'] = '👎'

        else:
            return None





    @config(theme=open_theme())
    async def main():

            global chat_msgs

            put_markdown("##  🖥 InCom чат\nArtist version") # logo
            msg_box = output()
            #put_scrollable(msg_box, height=200, keep_bottom=True) # Поле с сообщениями

            # форма входа в чат
            nickname = await input_group("Войти в чат", [
                        input(placeholder="Ваше имя", name="msg", required=True, validate=check_user),
                        actions(name="cmd", buttons=[
                            {'label':"Войти", 'value': 'submit', 'color': 'success'},
                            {'label': "Отмена", 'type': 'reset', 'color': 'secondary'}])
                        ])

            # выбор режима чата
            confirm = await actions('Выбрать способ общения', buttons=[
                {'label':'Ввод текста', 'value': 'Ввод текста', 'color': 'dark'},
                {'label': 'Горячие клавиши', 'value': 'Горячие клавиши', 'color': 'dark'},
                {'label': 'Текст + клавиши', 'value': 'Текст + клавиши', 'color': 'dark'}
                 ], help_text='')


            toast(f'Режим "{confirm}"')
            if confirm == 'Ввод текста':
                mode = '🖥'
            elif confirm == 'Горячие клавиши':
                mode = '📱'
            else:
                mode = '💻'

            put_scrollable(msg_box, height=200, keep_bottom=True)

            nickname = f'{mode} ' + nickname['msg']
            online_users.add(nickname)
            chat_msgs.append(('📢', f'`{nickname}` присоединился к чату!'))
            msg_box.append(put_markdown(f'📢 `{nickname}` присоединился к чату'))

            refresh_task = run_async(refresh_msg(nickname, msg_box))

            while True:

                if '🖥' in nickname:
                    data = await input_group("💭 Новое сообщение", [
                        input(placeholder="Текст сообщения ...", name="msg"),
                        actions(name="cmd", buttons=[
                            {'label':"Отправить", 'value': 'Отправить', 'color': 'success'},
                            {'label': "Выйти из чата", 'type': 'cancel', 'color': 'secondary'}])
                        ], validate=check_message)


                elif '📱' in nickname:
                    data = await input_group("💭 Новое сообщение", [
                        actions(name="cmd", buttons=[
                            {'label': "ГРОМЧЕ!", 'value': 'Громче', 'color': 'success'},
                            {'label': "", 'value': '', 'color': 'dark', 'disabled': 'True'},
                            {'label': "ТИШЕ!", 'value': 'Тише', 'color': 'success'},
                            {'label': "", 'value': '', 'color': 'dark', 'disabled': 'True'},
                            {'label': " МЕНЯ ", 'value': 'Меня', 'color': 'dark'},
                            {'label': "", 'value': '', 'color': 'dark', 'disabled': 'True'},
                            {'label': "ОСТАЛЬНЫХ", 'value': 'Остальных', 'color': 'dark'},
                            {'label': "", 'value': '', 'color': 'dark', 'disabled': 'True'},
                            {'label': "👍", 'value': '👍', 'color': 'dark'},
                            {'label': "", 'value': '', 'color': 'dark', 'disabled': 'True'},
                            {'label': "Выйти из чата", 'type': 'cancel', 'color': 'danger'}])
                    ], validate=check_message)

                else:
                    data = await input_group("💭 Новое сообщение", [
                        input(placeholder="Текст сообщения ...", name="msg", datalist=[
                            'Громче', 'Тише', 'Меня', 'Остальных', '👍', '👎']),
                        actions(name="cmd", buttons=[
                            {'label': "Отправить", 'value': 'Отправить', 'color': 'success'},
                            {'label': "Выйти из чата", 'type': 'cancel', 'color': 'secondary'}])
                    ], validate=check_message)

                if data is None:
                    out = await actions('Выйти из чата?', buttons=[
                        {'label': "Выйти", 'value': 'Да', 'color': 'danger'},
                        {'label': "Остаться", 'value': 'Нет', 'color': 'secondary'}])
                    if out == 'Да':
                        break
                    else:
                        continue

                msg_box.append(put_markdown(f"`{nickname}`: {data['msg']}"))
                chat_msgs.append((nickname, data['msg']))

            refresh_task.close()

            online_users.remove(nickname)
            toast("Вы вышли из чата!")
            msg_box.append(put_markdown(f'📢 Пользователь `{nickname}` покинул чат!'))
            chat_msgs.append(('📢', f'Пользователь `{nickname}` покинул чат!'))

            put_buttons([dict(label='Перезайти', value='Перезайти', color='success')], onclick=lambda btn:run_js('window.location.reload()'))


    async def refresh_msg(nickname, msg_box):
            global chat_msgs
            last_idx = len(chat_msgs)

            while True:
                await asyncio.sleep(1)

                for m in chat_msgs[last_idx:]:
                    if m[0] != nickname: # if not a message from current user
                        msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))

                # remove expired
                if len(chat_msgs) > MAX_MESSAGES_COUNT:
                    chat_msgs = chat_msgs[len(chat_msgs) // 2:]

                last_idx = len(chat_msgs)


    start_server(main, debug=True, port=prt, cdn=False, auto_open_webbrowser=False)

