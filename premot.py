import telebot, subprocess, os, pty, shlex

from keys import API_KEY, ADMIN_ID
from telebot.types import Message

DOWNLOADS = os.path.expanduser("~/downloads") 

class Shell:
    def __init__(self):
        pass

    def exec(self, cli: str):
        pass

    def get_output(self):
        pass

bot = telebot.TeleBot(API_KEY)
sh = Shell()

def getargs(text: str):
    return text.split(" ", 1)[1]

def is_admin(msg: Message):
    if msg.from_user.id != int(ADMIN_ID):
        bot.send_message(id, "Access denied.")
        return False

    return True

def __handle_document(msg: Message):
    bot.reply_to(msg, "Alright, seems like a file, hold on a second")
    file_id = msg.document.file_id
    file_name = msg.document.file_name or file_id

    file_info = bot.get_file(file_id)
    raw = bot.download_file(file_info.file_path)

    with open(os.path.join(DOWNLOADS, file_name), "wb") as f:
        f.write(raw)

    bot.reply_to(msg, "File saved")


@bot.message_handler(commands=["exec"])
def exec(msg: Message):
    if not is_admin(msg):
        return

    cli = shlex.split(getargs(msg.text))

    proc = subprocess.run(cli, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        stdin=subprocess.PIPE,
    )

    bot.send_message(msg.chat.id, proc.stdout + proc.stderr)

@bot.message_handler(commands=["file"])
def file(msg: Message):
    if not is_admin(msg):
        return

    path = os.path.expanduser(getargs(msg.text))

    if os.path.exists(path):
        bot.reply_to(msg, "Sending requested file...")
        with open(path, "rb") as f:
            bot.send_document(msg.chat.id, f, caption="Here you go")
    else:
        bot.reply_to(msg, "No such file")

@bot.message_handler(commands=["shell"])
def shell(msg: Message):
    if not is_admin(msg):
        return

    msg = bot.send_message(msg.chat.id, "Initializing terminal...")

@bot.message_handler(commands=["end"])
def end(msg: Message):
    if not is_admin(msg):
        return

@bot.message_handler(content_types=["document"])
def handle_document(msg: Message):
    __handle_document(msg)

@bot.message_handler(func=lambda _: True)
def handle_any(msg: Message):
    if msg.document:
        __handle_document(msg)
    elif sh.is_active:
        sh.exec(msg.text)
        sh.get_output()

        
if __name__ == "__main__":
    bot.infinity_polling()