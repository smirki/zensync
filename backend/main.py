from flask import Flask, request, jsonify, render_template
import requests
import json
from datetime import date
today = date.today()
import calendar
dow = calendar.day_name[today.weekday()] 

app = Flask(__name__)

# Simulated database
contacts = []
events = []
messages = []

def generate_text(model_name, prompt, seed, temperature=0):
    API_URL = "https://ollama.saipriya.org/api/generate"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "seed": seed,
            "temperature": temperature
        }
    }
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        print(response.json().get("response"))
        return response.json().get("response")
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

@app.route('/ai', methods=['POST'])
def ai_endpoint():
    data = request.get_json()
    command = data.get('command')
    messages.append({"text": command, "from": "user"})

    model = "llama3:8b"  # Adjust model name as necessary
    seed = 42
    prompt = (f"All dates should be MM-DD-YYYY. Respond to this question with just json. ONLY one of these choices in VALID JSON format and nothing else: "
              f"(\"addContact\" : {{\"name\" : person's name, email : email, socials : socials, info : really good summary of the person if given such as hobbies or things to remember them by, else leave blank. }} }}| removeContact : name | scheduleMeeting : {{attendees : [], title : *really good summary of request*, date : *Today is :{dow},{today}. calculate the date the user is requesting*, startime : 24hrtime, endtime: 24hrtime}} | "
              f"removeMeeting : [title, date, time] | editMeeting : name | moveMeeting : meetingName | showSchedule : date | "
              f"getEventDetails : [date, time] | setReminder : [event, date, time] | removeReminder : [event, date] | findUsers : {{topics: related to the users they want to find}} looking for a user to hang out with |"
              f"listUpcomingEvents : duration | queryFreeTime : date | syncCalendars : ) based on the question, try to figure out what it's asking. Answer in JSON only after QUESTION>"
              f"QUESTION>{command}")

    completion = generate_text(model, prompt, seed)
    user_response = generate_text(model, f"You are an ai    chatbot for an ai calendar that responds to a user, user said this: and this was the response: {completion} , respond to the user in the simplest words, like an ai chatbot that knows what is going on. Dont ask any followup questions.", seed)  # Initialize an empty list for messages
    if completion:
        # Process the response and also capture any messages if needed
        process_success = process_response(completion)
        if not process_success:
            messages.append({"text": "Failed to process response", "from": "server"})  # Append error message
            return jsonify({"error": "Failed to process response", "messages": messages}), 400
        else:
            messages.append({"text": user_response, "from": "server"})  # Append success message

    # Return the contacts, events, and messages in the response
    return jsonify({"contacts": contacts, "events": events, "messages": messages})

def remove_contact(contact_name):
    global contacts
    # Filter out the contact with the given name
    contacts = [contact for contact in contacts if contact['name'] != contact_name]
    print(f"Updated contacts list after removal: {contacts}")

def remove_contact_prompt(remv_contact):
    contacts_info = ". ".join([f"{contact['name']}" for contact in contacts])
    prompt = f"Given the following contacts: {contacts_info}. Answer ONLY with the exact name from the list that matches with {remv_contact} and capitalization to remove, nothing else."
    model_name = "llama3:8b"  # Adjust model name as necessary
    seed = 42
    temperature = 0
    completion = generate_text(model_name, prompt, seed, temperature)

    if completion:
        # Assuming the model returns the best match's name
        best_match_name = completion.strip()
        # Check if the returned name is in the contacts list
        best_match = next((contact for contact in contacts if contact['name'] == best_match_name), None)
        if best_match:
            print("Contacts before removal:", contacts)
            print("Removing contact:", best_match)
            remove_contact(best_match_name)
            print("Contacts after removal:", contacts)
            return jsonify({"success": f"Removed contact named {best_match_name}"})
        else:
            return jsonify({"error": "No matching contact found"})
    else:
        return jsonify({"error": "Failed to generate response from the model"})


def find_best_matches(topics):
    # Gather all contact information in a detailed prompt
    contacts_info = ". ".join([f"{contact['name']} is known for {contact.get('info', 'No additional info')}" for contact in contacts])
    # Create a detailed prompt for the LLM
    prompt = f"Given the following contacts: {contacts_info}. Find the best match for someone interested in {' and '.join(topics)}."
    
    # Generate text from the LLM
    model_name = "llama3:8b"  # Adjust model name as necessary
    seed = 42
    temperature = 0.5
    completion = generate_text(model_name, prompt, seed, temperature)
    
    if completion:
        # Assuming the model returns the best match's name
        best_match_name = completion.strip()
        # Find and return the contact with that name
        best_match = next((contact for contact in contacts if contact['name'] == best_match_name), None)
        if best_match:
            print(best_match)
            return jsonify(best_match)
        else:
            return jsonify({"error": "No matching contact found"})
    else:
        return jsonify({"error": "Failed to generate response from the model"})

def process_response(completion):
    try:
        response = json.loads(completion)
        if 'addContact' in response:
            new_contact_info = response['addContact']
            # Make sure 'info' is treated as a list even if a single string is passed
            if isinstance(new_contact_info.get('info'), str):
                new_contact_info['info'] = [new_contact_info['info']]
                
            existing_contact = next((contact for contact in contacts if contact['name'] == new_contact_info['name']), None)
            if existing_contact:
                # Ensure the contact has an 'info' key initialized as a list if it doesn't exist
                if 'info' not in existing_contact:
                    existing_contact['info'] = []
                # Extend the existing list with new info items, checking for duplicates
                existing_contact['info'].extend(x for x in new_contact_info.get('info', []) if x not in existing_contact['info'])
            else:
                # Create a new contact with 'info' initialized as a list
                new_contact = {'name': new_contact_info['name'], 'info': new_contact_info.get('info', [])}
                contacts.append(new_contact)
        elif 'removeContact' in response:
            contact_name = response['removeContact']
            remove_contact_prompt(contact_name)
        # Additional command handling goes here...
        elif 'scheduleMeeting' in response:
            event = {
                "attendees": response['scheduleMeeting']['attendees'],
                "title": response['scheduleMeeting']['title'],
                "date": response['scheduleMeeting']['date'],
                "starttime": response['scheduleMeeting']['starttime'],
                "endtime": response['scheduleMeeting']['endtime']
            }
            events.append(event)
            print(events)
        elif 'removeMeeting' in response:
            events[:] = [event for event in events if event['title'] != response['removeMeeting'][0]]
        elif 'showSchedule' in response:
            # Implement logic to display schedule for the given date
            return jsonify([event for event in events if event['date'] == response['showSchedule']])
        elif 'getEventDetails' in response:
            # Implement logic to get details of the specific event
            return jsonify(next((event for event in events if event['date'] == response['getEventDetails'][0] and event['time'] == response['getEventDetails'][1]), None))
        elif 'setReminder' in response:
            # Logic to set a reminder for an event
            # Details might include adding to a reminders list or setting up a notification system
            pass
        elif 'listUpcomingEvents' in response:
            # Implement logic to list upcoming events for the given duration
            pass
        elif 'queryFreeTime' in response:
            # Implement logic to find free time on a given date
            pass
        elif 'syncCalendars' in response:
            # Implement logic to synchronize calendars
            pass
        elif 'findUsers' in response:
            topics = response['findUsers']['topics']
            return find_best_matches(topics)
        return True
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error processing response: {str(e)}")
        return False

@app.route('/')
def home():
    return render_template('index3.html')

if __name__ == '__main__':
    app.run(debug=True)
