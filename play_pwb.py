import multiprocessing
import socket
import qrcode
import pywebio_chat
from guizero import App, Text, PushButton, Combo, info, yesno, Picture, CheckBox


p2 = multiprocessing.Process(target=pywebio_chat.wb)

# узнать свой локальный ip
def get_interface_ip(family: socket.AddressFamily) -> str:
    # arbitrary private address
    host = "10.253.155.219"

    with socket.socket(family, socket.SOCK_DGRAM) as s:
        try:
            s.connect((host, 58162))
        except OSError:
            return "127.0.0.1"

        return s.getsockname()[0]  # type: ignore

ipv4 = get_interface_ip(socket.AF_INET)
tm = 300


# Тема
def wr_theme(theme):
    f = open('usr_thm.txt', 'w')
    f.write(theme)
    f.close()

def open_theme():
        f = open('usr_thm.txt', 'r')
        user_theme = f.read()
        f.close()
        return user_theme

# QR
def gen_qr():
    qr = qrcode.QRCode(box_size=5, border=1)
    qr.add_data(f'http://{ipv4}:{pywebio_chat.prt}')
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qr.gif")

# Тема
if open_theme() == 'minty':
    background = (238,247,241)
    txtcolor = 'black'
    ch_options = ['Светлая тема', 'Темная тема']
else:
    background = (3,20,50)
    txtcolor = 'white'
    ch_options = ['Темная тема', 'Светлая тема']

# Интерфейс
def gui():

    # Авто открытие браузера
    '''
    def browser_auto_open():
        global auto_open
        if checkbox.value == 1:
            auto_open = True
        else:
            auto_open = False '''


    # Выбор темы
    def choise_method():
        if choise.value == "Светлая тема":
            app.bg = (238,247,241)
            start_vidget.text_color='black'
            theme = 'minty'
            wr_theme(theme)

        else:
            app.bg = (3,20,50)
            start_vidget.text_color = 'white'
            theme = 'dark'
            wr_theme(theme)



    # закрыть приложение
    def closeapp():
        if play_button.text_color == 'blue':
            quit()
        else:
            cl_app = yesno('Внимание!', 'Остановить сервер и выйти?')
            if cl_app == True:
                play_button.text_color = 'blue'
                play_button.text = 'Start Server'
                p2.terminate()
                p2.join()
                play_button.after(1000, quit)
            else:
                pass


    def counter():
        global tm
        tm -= 1

        if tm % 2 == 0:
            app.title = "DEMO Version"
        else:
            app.title = f"Завершение через {tm} сек"

        if tm <= 0 or tm > 300:
            if play_button.text_color == 'blue':
                about_demo()
                quit()
            else:
                play_button.text_color = 'blue'
                play_button.text = 'Start Server'
                p2.terminate()
                p2.join()
                about_demo()
                quit()

    # START server
    def player():
        if play_button.text_color == 'blue':
            play_button.text_color = (236,74,66)
            play_button.text = 'Stop and quit'
            p2.start()
            #print(p2.ident)
            choise.enabled = False
            lable_002.value =f'Откройте в браузере \n http://{ipv4}:{pywebio_chat.prt} \n или воспользуйтесь QR'
            gen_qr()
            picture.image = 'qr.gif'

        else:
            closeapp()




    # About
    def about_demo():
        info("info", "Created by aleksan149 \nhttps://github.com/aleksan149 \n2023 "
                     '\n За полной версией обращайтесь к автору в телеграмм @Aleksan149'
                     "\n\nInComServer - служебный чат \n- Запустите сервер "
                     "\n- Откройте адрес или qr код в браузере на любых устройствах \n- Общайтесь!"
                     "\n\n* Устройства пользователей и сервер должны быть подключены к одной локальной сети!")

    def about():
        info("info", "Created by aleksan149 \nhttps://github.com/aleksan149 \n2023 "
                     "\n\nInComServer - служебный чат \n- Запустите сервер "
                     "\n- Откройте адрес или qr код в браузере на любых устройствах \n- Общайтесь!"
                     "\n\n* Устройства пользователей и сервер должны быть подключены к одной локальной сети!")

    #GUI

    app = App(title="Internal Communication", height=500, width=300, bg=background)




    # Кнопка инфо
    info_butoon = PushButton(app, image='i.png', command=about_demo, align="bottom", padx=0, pady=0)


    lable_00 = Text(app, height=1) # Пустые лейблы для отступа

    lable_00.repeat(1000, counter)

    start_vidget = Text(app, text="InComServer", size=30, color=txtcolor)

    lable_001 = Text(app, height=1) # Пустые лейблы для отступа

    lable_01 = Text(app, text="Оформление:", color='white', enabled=False, height=1)

    choise = Combo(app, options=ch_options, height=1, width=15, command=choise_method)
    choise.text_color = "black"
    #choise.bg = 'white'


    lable_02 = Text(app, height=1)  # Пустые лейблы для отступа
    #checkbox = CheckBox(app, text="Автоматически открыть чат в браузере", command=browser_auto_open)
    #checkbox.text_color = txtcolor

    lable_002 = Text(app, color='white', text='Запустите сервер \nи откройте выданный адрес \n'
                                              'в браузере', size=15, enabled=False, height=3)

    #lable_03 = Text(app, height=1) # Пустые лейблы для отступа

    picture = Picture(app, image='bgnd.gif')

    lable_04 = Text(app, align='bottom', height=1) # Пустые лейблы для отступа

    play_button = PushButton(app, text="Start Server", padx=20, pady=10, align='bottom', command=player)
    play_button.text_color = 'blue'

    lable_05 = Text(app, height=1, align='bottom') # Пустые лейблы для отступа



    app.when_closed = closeapp
    app.display()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    p1 = multiprocessing.Process(target=gui)
    p1.start()
    #print(p1.ident)
    p1.join()








