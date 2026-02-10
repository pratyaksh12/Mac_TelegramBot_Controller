import telebot;
from dotenv import load_dotenv;
import datetime;
import subprocess
import os;
import ffmpeg

# load env file
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
FFMPEG_PATH = "/opt/homebrew/bin/ffmpeg" 


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
        
# screenshot for the active screen        
def take_screenshot_and_send(message):
        
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
        return False
            
    finally:  # delete file once sent
        if(os.path.exists(path)):    
            os.remove(path)
            
    return True


# function to take a screen recording for a set duration of time
def take_screenrecording_and_send(chat_id, duration) -> bool:
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y")
    output_dir = "/tmp/screenrecordings"
    raw_path = f"{output_dir}/{timestamp}.mov"
    final_path = f"{output_dir}/{timestamp}.mp4"
    screencapture_cmd = ["screencapture", "-V", str(duration), "-x", "-k", raw_path]
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        bot.send_message(chat_id, "starting recording")
        print("executing screencapture command", flush=True)
        subprocess.run(screencapture_cmd, check=True, capture_output=True)
        
        if(not os.path.exists(raw_path) or os.path.getsize(raw_path) == 0):
            print("error capturing the video file doesn't exist or size is 0.")
            return False
        
        print("recording capture successful. Converting to mp4 usinf ffmpeg")
        ffmpeg_cmd = [
            FFMPEG_PATH, "-i", raw_path, 
            "-c:v", "libx264", 
            "-preset", "ultrafast", 
            "-pix_fmt", "yuv420p", 
            "-crf", "23", 
            "-movflags", "+faststart", 
            final_path
        ]
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)

        if not os.path.exists(final_path) or os.path.getsize(final_path) == 0:
            print("error: MP4 file doesn't exist or is empty after conversion")
            return False
        
        print(f"conversion to mp4 successful sending to telegram")
        
        with open(final_path, "rb") as video:
            bot.send_video(chat_id, video, caption=f"screen recording taken on {timestamp}. duration: {duration}")
            
    except subprocess.SubprocessError as err:
        print("subprocess error", err)
        return False
    finally:
        os.remove(raw_path)
        os.remove(final_path)
        
    return True
        
    
       
@bot.message_handler(commands=['ss', 'screenshot', 'screen'])
def handle_screenshot(message):
    if(message.chat.id != authorisation_id):
        bot.reply_to(message, "you are not authorised by the admin")
        return
    if not take_screenshot_and_send(message):
        bot.reply_to(message, "error taking a screenshot")
        
        
        
@bot.message_handler(commands=['screenrec', 'screenrecord', 'sr'])
def handle_screenrecording(message):
    
    # authorise
    if(message.chat.id != authorisation_id):
        bot.reply_to(message, "Not authorised by admin")
    
    # check for 2 arguments
    args = message.text.split()    
    if(len(args) < 2):
        bot.reply_to(message, f"Usage: /{message} <duration>\n Example: /{message} 15")
    
    # send to related function
    try:
        duration = int(args[1])
        if not (5 <= duration <= 300):
            bot.reply_to(message, "duration has to be between 5 and 300 seconds (5 min).")
            
        if not (take_screenrecording_and_send(message.chat.id, duration)):
            bot.reply_to(message, "recording failed")
            
    # check for duration as a number
    except ValueError:
        bot.reply_to(message, "duration has to be a number between 5 and 300")
    except Exception:
        bot.reply_to(message, "error during recording please refre to console")
                    
        
        
        
        
if __name__ == "__main__":
    print("Bot is starting...")
    bot.infinity_polling()
    
