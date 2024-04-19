import requests

def generate_text(model_name, prompt, seed, temperature=0):
    API_URL = "https://ollama.saipriya.org/api/generate"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,  # assuming we want the non-streaming response
        "options": {
            "seed": seed,
            "temperature": 0
        }
    }

    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        # Parse the JSON response and return the text completion
        return response.json().get("response")
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

if __name__ == "__main__":
    model = "llama3:8b"  # Replace with your model's name
    seed = 42  # Replace with your desired seed for reproducibility
    prompt = """ Respond to this question with ONLY one of with these choice and nothing else in json: 
    (addContact : name | removeContact : name | scheduleMeeting : *create the title, use 24hr format, standard datetime, and leave anything as " " if it is not easily discernable.* 
    [attendees, title, date, time] | editMeeting : name | moveMeeting : meetingName | removeMeeting : name) based the question, try to figure out what its asking. 
    It will be after the word QUESTION>. 
    QUESTION>schedule a meeting with sam on tuesday at 6 pm"""
    
    completion = generate_text(model, prompt, seed)
    if completion:
        print(f"Model response: {completion}")
