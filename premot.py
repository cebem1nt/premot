import telebot, subprocess, os, pty, shlex
import threading, re

from select import select

from keys import API_KEY, ADMIN_ID
from telebot.types import Message

DOWNLOADS = os.path.expanduser("~/downloads") 
bot = telebot.TeleBot(API_KEY)

class Shell:
    is_active = False

    def init_shell(self, msg: Message, shell=None):
        self.child, self.master = pty.fork()
        self.is_active = True
        self.msg = msg

        if shell:
            self.shell = shell
        else:
            os.environ.get("SHELL", "sh")

        if self.child == 0:
            os.environ["TERM"] = "dumb"
            os.environ.pop("VIRTUAL_ENV", None)
            os.environ.pop("VIRTUAL_ENV_PROMPT", None)
            os.environ.pop("PS1", None)

            os.execlp(self.shell, self.shell)

    def exec(self, cli: str):
        cli += '\n'
        os.write(self.master, cli.encode())
    
    def peek(self):
        readable, _, _ = select([self.master], [], [])

        if self.master in readable:
            data = os.read(self.master, 4096)
            return data

    def __render(self):
        while True:
            try:
                content = terminal(self.peek())
                bot.edit_message_text(content, self.msg.chat.id, self.msg.id, parse_mode="Markdown")
            except:
                return

    def render(self):
        th = threading.Thread(target=self.__render, daemon=True)
        th.start()

    def end(self):
        os.close(self.master)
        os.kill(self.child, 9)
        os.waitpid(self.child, 0)
        self.is_active = False

sh = Shell()

def remove_ansii(content: str):
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub('', content)

def getargs(text: str):
    args = text.split(" ", 1)
    
    if len(args) > 1:
        return args[1]
    else:
        return None

def terminal(text: bytes):
    return "```terminal\n" + remove_ansii(text.decode()) + "\n```"

def is_admin(msg: Message):
    if msg.from_user.id != int(ADMIN_ID):
        bot.reply_to(msg, "Who the fuck are you?")
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

    bot_msg = bot.send_message(msg.chat.id, "```terminal\n Initializing terminal... \n```", "Markdown")
    opt_shell = getargs(msg.text)

    sh.init_shell(bot_msg, opt_shell)
    sh.render()

@bot.message_handler(commands=["end"])
def end(msg: Message):
    if not is_admin(msg):
        return

    sh.end()
    bot.send_message(msg.chat.id, "Ending terminal")

@bot.message_handler(content_types=["document"])
def handle_document(msg: Message):
    if not is_admin(msg):
        return

    __handle_document(msg)

@bot.message_handler(func=lambda _: True)
def handle_any(msg: Message):
    if not is_admin(msg):
        return

    if msg.document:
        __handle_document(msg)
    elif sh.is_active:
        bot.delete_message(msg.chat.id, msg.id)
        sh.exec(msg.text)
    else:
        bot.reply_to(msg, "I dont undestand ya")
        
if __name__ == "__main__":
    bot.infinity_polling()