# secure_client.py
import requests
import argparse
import socket
import sys
import os
from urllib3.exceptions import InsecureRequestWarning
from dotenv import load_dotenv

# Loads environment variables
load_dotenv()

# Suppress only the single InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Get API key from environment variable (more secure than hardcoding)
API_KEY = os.environ.get("ECHO_API_KEY")
if not API_KEY:
    print("Error: Please set the ECHO_API_KEY environment variable")
    sys.exit(1)

LOCAL_IP = str(socket.gethostbyname(socket.gethostname()))

SERVER_URL = f"https://{LOCAL_IP}:5000/echo"  # Public-facing server


def send_message(message):
    headers = {"X-API-Key": API_KEY}
    try:
        # verify=False is only for development with self-signed certs
        # In production, use proper certificates and set verify=True
        response = requests.post(
            SERVER_URL,
            json={"message": message},
            headers=headers,
            verify=False,  # Change to True for production
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("response")
        else:
            return f"Error: Server returned status code {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Connection error: {e}"


# Rest of client code remains the same...


def interactive_mode():
    predefined_messages = [
        "Hello, server!",
        "How are you doing?",
        "Testing 1-2-3",
        "This is a test message",
        "Goodbye!",
    ]

    while True:
        print("\nSelect a message to send:")
        for i, msg in enumerate(predefined_messages, 1):
            print(f"{i}. {msg}")
        print("0. Exit")

        choice = input("\nEnter your choice (0-5): ")

        if choice == "0":
            print("Exiting...")
            break

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(predefined_messages):
                message = predefined_messages[idx]
                print(f"Sending: '{message}'")
                response = send_message(message)
                print(f"Received: '{response}'")
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send messages to echo server")
    parser.add_argument("-m", "--message", help="Message to send")

    args = parser.parse_args()

    if args.message:
        response = send_message(args.message)
        print(f"Received: '{response}'")
    else:
        interactive_mode()
