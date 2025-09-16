import json
import base64

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  

def parse_str(message_content: str):  
    """
    This function takes a string as input and tries to parse it as a JSON object.
    If the parsing is successful, it returns the parsed JSON object.
    If there is a JSONDecodeError, it returns the string "There was some error parsing the model's output".
   
    """

    message_clean = message_content.strip().strip("```json").strip("```")

    try:
        message_json = json.loads(message_clean)
        return message_json
    except json.JSONDecodeError:
        return "There was some error parsing the model's output"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "There was some error parsing the model's output"