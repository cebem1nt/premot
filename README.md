# Premot
Lets you controll your pc remotely trough a telegram bot, also with a terminal emulator embeded into a telegram message. Why would you use this and not ssh? No clue.
Same program as [remot](https://github.com/cebem1nt/remot), but in python because tgbot c++ doesn't work well with poor internet :(

## Installation
Aquire a telegram bot api key and your internal telegram id. put them into `keys.py`

Now the installation part:

```sh
python -m venv env
source sourceme
pip install -r requirements.txt
```

There it is, you can run the bot with:
```
python premot.py
```

## Usage
This bot provides the following commands:
```
# Executes any shell command
/exec "some command here" -> /exec ls -a
# Sends requested file from pc to you
/file "filepath"
# Starts a terminal session with given shell (your default one if none)
/shell "optional shell here" -> /shell bash  ; /shell
# Ends terminal session
/end
```

Yeah and now you can do neofetch in telegram

