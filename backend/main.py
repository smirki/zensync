from flask import Flask, request, jsonify, render_template
import requests
import json

app = Flask(__name__)

# Simulated database
contacts = []
events = []

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

    model = "llama3:8b"  # Adjust model name as necessary
    seed = 42
    prompt = (f"Respond to this question with ONLY one of these choices in VALID JSON format and nothing else: "
              f"(\"addContact\" : {{\"name\" : person's name, info : really good summary of the person if given such as hobbies or things to remember them by, else leave blank. }} }}| removeContact : name | scheduleMeeting : {{attendees : [], title : *really good summary of request*, date : *like today, tomorrow etc*, startime : 24hrtime, endtime: 24hrtime}} | "
              f"removeMeeting : [title, date, time] | editMeeting : name | moveMeeting : meetingName | showSchedule : date | "
              f"getEventDetails : [date, time] | setReminder : [event, date, time] | removeReminder : [event, date] | "
              f"listUpcomingEvents : duration | queryFreeTime : date | syncCalendars : ) based on the question, try to figure out what it's asking. Check again to make sure it is only outputting valid JSON. "
              f"QUESTION>{command}")

    completion = generate_text(model, prompt, seed)
    if completion:
        if not process_response(completion):
            return jsonify({"error": "Failed to process response"}), 400

    return jsonify({"contacts": contacts, "events": events})

def process_response(completion):
    try:
        response = json.loads(completion)
        if 'addContact' in response:
            # Extract the contact details
            contact_info = response['addContact']
            # Check if the contact already exists
            existing_contact = next((contact for contact in contacts if contact['name'] == contact_info['name']), None)
            if existing_contact:
                # Update existing contact with new info if provided
                existing_contact.update(contact_info)
            else:
                # Add new contact if not already present
                contacts.append(contact_info)
        elif 'addContacts' in response:
            contacts.extend(response['addContacts'])
        elif 'removeContact' in response:
            contacts.remove(response['removeContact'])
        elif 'scheduleMeeting' in response:
            event = {
                "attendees": response['scheduleMeeting']['attendees'],
                "title": response['scheduleMeeting']['title'],
                "date": response['scheduleMeeting']['date'],
                "starttime": response['scheduleMeeting']['starttime'],
                "endtime": response['scheduleMeeting']['endtime']
            }
            events.append(event)
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
        return True
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error processing response: {str(e)}")
        return False

@app.route('/')
def home():
    return render_template('index2.html')

if __name__ == '__main__':
    app.run(debug=True)
