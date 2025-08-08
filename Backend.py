from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# OpenAI API settings
API_KEY = "-----"  # Replace with your actual API key
API_URL = "-----" # Replace with your URL

# Global variables
temperature = 0.5
number_of_tokens = 100  # Default value
num_outputs = 1
payload = {}

def get_openai_response(user_input, temperature, max_tokens, num_outputs):
    """
    Makes a request to the OpenAI API with the given parameters.
    """
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        "model": "gpt-4",  # Adjust as necessary
        "messages": [{"role": "user", "content": user_input}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "n": num_outputs
    }

    print("Payload being sent to OpenAI:", payload)  # Log the payload

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            # Extract and return responses as a list
            choices = response.json().get('choices', [])
            return [choice['message']['content'] for choice in choices]
        else:
            print(f"OpenAI API Error: {response.status_code}, {response.text}")
            return {"error": f"OpenAI API Error: {response.status_code}", "details": response.text}
    except Exception as e:
        print(f"Exception during OpenAI API call: {str(e)}")
        return {"error": "Exception occurred during OpenAI API call", "details": str(e)}

@app.route('/')
def index():
    return render_template('ChatPage.html')  # Serve the main HTML page

@app.route('/ParamPage')
def green():
    return render_template('ParamPage.html')

@app.route('/Temperature')
def param1():
    return render_template('Temperature.html')

@app.route('/Outputs')
def param2():
    return render_template('Outputs.html')

@app.route('/Tokens')
def param3():
    return render_template('Tokens.html')

@app.route('/send-message', methods=['POST'])
def send_message():
    """
    Handles messages from the frontend, makes an OpenAI API call, and returns the response.
    """
    global temperature, number_of_tokens, num_outputs

    data = request.get_json()
    user_message = data.get('message', '')

    # Validate the input
    if not user_message.strip():
        return jsonify({"error": "Message cannot be empty"}), 400

    print(f"Received message: {user_message}")
    print(f"Current settings: Temperature={temperature}, Max Tokens={number_of_tokens}, Outputs={num_outputs}")

    # Call OpenAI API with the current settings
    responses = get_openai_response(user_message, temperature, number_of_tokens, num_outputs)

    # Check if an error occurred in the OpenAI response
    if isinstance(responses, dict) and "error" in responses:
        return jsonify({"error": responses["error"], "details": responses.get("details", "")}), 500

    # Return the list of responses and payload details to the frontend
    return jsonify({
        "responses": responses,
        "payload": {
            "messages": [{"role": "user", "content": user_message}],
            "temperature": temperature,
            "max_tokens": number_of_tokens,
            "n": num_outputs
        }
    })

# Route to receive and update the slider value
@app.route('/slider-valueP1-1', methods=['POST'])
def slider_value():
    global temperature, num_outputs  # Use only the required global variables

    data = request.get_json()
    slider_value = data.get('value')  # Extract the slider value

    # Update the global temperature with the slider's value
    temperature = float(slider_value)
    print("Updated temperature:", temperature)  # Log the updated temperature

    return jsonify({"status": "success", "value": slider_value})

@app.route('/slider-valueP2-2', methods=['POST'])
def num_outputs_handler():
    global num_outputs  # Access the global num_outputs variable

    data = request.get_json()
    slider_value = data.get('value')  # Extract the slider value from the request
    try:
        num_outputs = int(slider_value)  # Update the global variable
        print("Updated number of outputs:", num_outputs)  # Log the new value
        return jsonify({"status": "success", "value": num_outputs})
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid value provided"}), 400



@app.route('/update-integer', methods=['POST'])
def update_integer():
    global number_of_tokens  # Access the global number_of_tokens variable

    data = request.get_json()
    new_value = data.get('value')  # Extract the value from the JSON payload

    try:
        number_of_tokens = int(new_value)  # Update the global variable
        print("Updated number_of_tokens:", number_of_tokens)  # Log for debugging
        return jsonify({"status": "success", "number_of_tokens": number_of_tokens})
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid integer value"}), 400

@app.route('/get-number-of-tokens', methods=['GET'])
def get_number_of_tokens():
    global number_of_tokens  # Fetch the global variable
    return jsonify({"number_of_tokens": number_of_tokens})

@app.route('/get-temperature', methods=['GET'])
def get_temperature():
    global temperature  # Fetch the global temperature variable
    return jsonify({"temperature": temperature})

@app.route('/get-num_outputs', methods=['GET'])
def get_num_outputs():
    global num_outputs  # Fetch the global temperature variable
    return jsonify({"num_outputs": num_outputs})


if __name__ == '__main__':
    app.run(debug=True)
