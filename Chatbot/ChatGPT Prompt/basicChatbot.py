# A basic python scritpt for a chatbot that can handle greeting, farewells and common questions about the weather. 

# Define  fuctions ot handle different interactions

import random

def handle_greeting():
    """Function to handle greetings."""
    responces = ["Hello there!", "Hi!", "Greetings", "How can I help you today?"]
    return random.choice(responces)

def handle_farewell():
    """Function to handle farwell."""
    responces= ["Goodbye!", "See you later!", "Have a greate day!", "Bye!"]
    return random.choice(responces)

def handle_weather_questions():
    """Function to handle weather-related questions."""
    responces = ["It's sunny today!", "Expect some rain later today", "It's quite chilly. Wear a warm coat!"]
    return random.choice(responces)

def handle_unknown():
    """Function to handle unrecognized inputs"""
    responces = ["I'm not sure how to answer that.", "Can you rephrase that?", "I'm here to help, ask me somthing else"]
    return random.choice(responces)

def chatbot_responces(user_input):
    """Function to determine the type of user input and respond appropriately."""
    user_input = user_input.lower()

    if any(greet in user_input for greet in ["hi", "hello", "greetings"]):
        return handle_greeting()
    elif any(farewell in user_input for farewell in ["bye", "goodbye", "see you"]):
        return handle_farewell()
    elif "weather" in user_input:
        return handle_weather_questions()
    else:
        return handle_unknown()

# This code is currently designed to be imported and tested an interactive Python enironment or used in a scritp. 

# Uncomment the following lines to test the chatbot directly:
"""
if __name__ == "__main__":
    running = True
    print("Chatbot: Hi! I'm your chatbot. You can start chatting with me now.")
    while running:
        user_input = input("You: ")
        if user_input.lower() in ["quite", "exit"]:
            running = False
            print("Chatbot: " + handle_farewell())
        else:
            print("Chatbot: " + chatbot_responces(user_input))


"""