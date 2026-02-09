import telebot;
from dotenv import load_dotenv;
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

@bot.message_handler(commands=['start'])
def handle_start(message):
    if(message.chat.id != authorisation_id):
        print(f"Unauthorized access attempt from CHAT ID: {message.chat.id}")
        return 
    
    user_first_name = message.from_user.first_name
    bot.reply_to(message, f"Hello {user_first_name} control is online. your chat id is {message.chat.id}")
    print(f"authorize access for {user_first_name} - {message.chat.id}")
    
    
    
@bot.message_handler(commands=['ping'])
def handle_ping(message):
    if(message.chat.id == authorisation_id):
        bot.reply_to(message, "pong!")
        
        
if __name__ == "__main__":
    print("Bot is starting...")
    bot.infinity_polling()
    
