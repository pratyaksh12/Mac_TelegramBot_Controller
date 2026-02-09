import telebot;
from dotenv import load_dotenv;
import datetime;
import subprocess
import os;

# load env file
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


if(API_TOKEN):
    bot = telebot.TeleBot(API_TOKEN)
else:
    raise Exception("Telegram api is not provided")

if(CHAT_ID):
    authorisation_id = int(CHAT_ID)
else:
    raise Exception("Chat ID was not set")


# manage security popups 
def show_macos_popup(message_text):
    escaped_message = message_text.replace('"', '\\"')
    applescript_command = f'display dialog "{escaped_message}" with title "Alert" buttons {{"OK"}} default button "OK"'
    try:
        subprocess.run(["osascript", "-e", applescript_command], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"AppleScript error: {e.stderr.decode()}", flush=True)
        return False
    except Exception as e:
        print(f"Unexpected error in show_macos_popup: {e}", flush=True)
        return False

    
    
# testing for a healthy ping
@bot.message_handler(commands=['ping'])
def handle_ping(message):
    if(message.chat.id == authorisation_id):
        bot.reply_to(message, "pong!")
        
# screenshot for the active screen        
@bot.message_handler(commands=['ss', 'screenshot', 'screen'])
def handle_screenShot(message):
    # veryfication
    if(message.chat.id != authorisation_id):
        return 
    
    # create a temporary image path
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y")
    path = f"/tmp/screenshot_{timestamp}.png"    
    print(f"Taking screenshot to {path}...")
    
    try:
        # run subprocess
        subprocess.run(["screencapture", "-x", "-D", "1", path], check=True)
        
        # send picture to chat
        with open(path, "rb") as photo:
            bot.send_photo(message.chat.id, photo, caption=f"Screenshot at {timestamp}")
        
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        bot.reply_to(message, f"Error: {e}")
            
    finally:  # delete file once sent
        if(os.path.exists(path)):    
            os.remove(path)
        
        
if __name__ == "__main__":
    print("Bot is starting...")
    bot.infinity_polling()
    
