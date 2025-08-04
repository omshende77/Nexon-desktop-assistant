from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)


# System instructions

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""


# Load or create chat log
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)


# Google search
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    answer = f"The search results for '{query}' are:\n[start]\n"
    for r in results:
        answer += f"Title: {r.title}\nDescription: {r.description}\n\n"
    answer += "[end]"
    # print(answer)
    return answer

# Clean output
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "hi"},
    {"role": "assistant", "content": "hello how can i help you"}
]


# Real-time date/time info (only added if needed)

def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")  # Full month name
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data += "Use this real-time information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data


# Main chatbot logic
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
    # Append user input to messages
    messages.append({"role": "user", "content": f"{prompt}"})
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    try:
        # Generate response
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "").strip()
        messages.append({"role": "assistant", "content": Answer})

        # Save chat log
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        # Remove temporary system messages
        SystemChatBot.pop()
        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred. Please try again."

# Run the chatbot
if __name__ == "__main__":
    print("Chatbot initialized.")
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
