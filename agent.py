import os
import dotenv
import base64
import openai

dotenv.load_dotenv()

AGENT_API = os.getenv("AGENT_API")

if(AGENT_API):
    client = openai.Client(api_key=AGENT_API)
    


def encode_image(path):
    print("converting to base64...")
    with open(path, "rb") as image:
        return base64.b64encode(image.read()).decode("utf-8")
    

def handle_image_response(path):
    base_64_img = encode_image(path)
    print("conversion successful.")
    print("Sending message to agent")
    if not AGENT_API:
        print("Error: AGENT_API key not found. Please set it in .env file.")
        return "Error: API Key missing"
        
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano", # Updated to a valid model name
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "What is the answer for the question in the image? keep answer within 50 words and concise"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base_64_img}"
                            }
                        }
                    ]
                }
            ]
        )
        print("response recieved successfully")
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return f"Error: {e}"




    
    
    