"""
Replicate the ChatGPT desktop app experience in the terminal.
More lightweight.
More keybord controls / ability to define custom keybindings.
Define default model.

2025-02-15
- added clipboard copy of both input and output
- added logging in Markdown files

v2:
+ add more models, ie run different models in parallel to compare answers.
"""

from datetime import datetime
import os
ts_db = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
ts_time = f"{datetime.now().strftime('%H:%M:%S')}"
print(f"\n---------- {ts_time} starting {os.path.basename(__file__)}")
ts_chat = f"{datetime.now().strftime('%y%m%d-%H%M')}"

import time
start_time = time.time()

from dotenv import load_dotenv
load_dotenv()

import openai
import os
import time
from typing_extensions import override
from openai import AssistantEventHandler

# GLOBAL

# Add chat log directory configuration
CHAT_LOG_DIR = "/Users/nic/Dropbox/Notes/chat"
chat_file = os.path.join(CHAT_LOG_DIR, f"chat_{ts_chat}.md")
start_file = os.path.join(CHAT_LOG_DIR, "_start.md")

# Add assistant selection

ASSISTANTS = {
    '1': {'id': os.getenv("NIC_KAL_GPT"), 'name': 'Kal GPT'},
    '2': {'id': os.getenv("NIC_KAL_REF"), 'name': 'Kal Ref'},
    '3': {'id': os.getenv("NIC_KAL_EMAIL"), 'name': 'Kal Email'},
    '4': {'id': os.getenv("NIC_KAL_EMAIL_FU"), 'name': 'Kal Email Fu'},
    '5': {'id': os.getenv("NIC_KAL_EMAIL_SEQUENCE"), 'name': 'Kal Email Sequence'},
    '6': {'id': os.getenv("NIC_KAL_COLD_CALL_QUESTIONS"), 'name': 'Kal Cold Call Questions'},
    '7': {'id': os.getenv("NIC_KAL_DEMO"), 'name': 'Kal Demo'},
    # '7': {'id': os.getenv("NIC_LINKEDIN_PROFILE"), 'name': 'LinkedIn Profile'},
    # '8': {'id': os.getenv("NIC_TEST"), 'name': 'Test'},
}

def select_assistant():
    print("\nChoose Your Assistant:\n")
    for key, assistant in ASSISTANTS.items():
        print(f"{key}: {assistant['name']}")
    
    while True:
        max_choice = len(ASSISTANTS)
        choice = input(f"\nSelect assistant (1-{max_choice}): ").strip()
        if choice in ASSISTANTS:
            return ASSISTANTS[choice]['id'], ASSISTANTS[choice]['name']
        print("Invalid selection. Please try again.")

# FUNCTIONS

def copy_to_clipboard(text: str):
    import subprocess
    process = subprocess.Popen("pbcopy", universal_newlines=True, stdin=subprocess.PIPE)
    process.communicate(text)
    return process.returncode == 0


# MAIN

# Create chat directory if it doesn't exist
os.makedirs(CHAT_LOG_DIR, exist_ok=True)

# Select assistant
ASSISTANT_ID, assistant_name = select_assistant()

# Initialize chat log file with timestamp and assistant name
with open(chat_file, "w") as f:
    f.write(f"# Chat Session - {ts_db}\nAssistant: {assistant_name}")

# Set up OpenAI API key (use environment variable for security)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create a new OpenAI client
client = openai.OpenAI()

# Create a new thread
thread = client.beta.threads.create()

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == "exit":
        break
    
    # If input is empty, read from _start.md
    if not user_input.strip():
        try:
            with open(start_file, 'r') as f:
                user_input = f.read().strip()
            if not user_input:
                print("Warning: _start.md is empty")
                continue
        except FileNotFoundError:
            print(f"Warning: {start_file} not found")
            continue

    # Log user message
    with open(chat_file, "a") as f:
        f.write(f"\n\n### User ({ts_time}):\n{user_input}\n")

    # Copy user input to clipboard
    copy_to_clipboard(user_input)

    # Send user message
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_input
    )
    
    # Collect assistant response for clipboard
    full_response = []
    
    class EventHandler(AssistantEventHandler):
        @override
        def on_text_created(self, text) -> None:
            print("\nChatGPT:", end=" ", flush=True)
            # Log assistant response start
            with open(chat_file, "a") as f:
                f.write(f"\n### Assistant ({ts_time}):\n")
        
        @override
        def on_text_delta(self, delta, snapshot):
            print(delta.value, end="", flush=True)
            full_response.append(delta.value)
            # Append each delta to the log file
            with open(chat_file, "a") as f:
                f.write(delta.value)
        
        @override
        def on_tool_call_created(self, tool_call):
            print(f"\nChatGPT: {tool_call.type}\n", flush=True)
        
        @override
        def on_tool_call_delta(self, delta, snapshot):
            if delta.type == 'code_interpreter':
                if delta.code_interpreter.input:
                    print(delta.code_interpreter.input, end="", flush=True)
                    full_response.append(delta.code_interpreter.input)
                if delta.code_interpreter.outputs:
                    print("\n\nOutput:", flush=True)
                    for output in delta.code_interpreter.outputs:
                        if output.type == "logs":
                            print(f"\n{output.logs}", flush=True)
                            full_response.append(output.logs)
    
    # Stream Assistant response
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()
    
    # Copy assistant response to clipboard
    copy_to_clipboard(''.join(full_response))
    
    print("")  # Print newline at the end of response





########################################################################################################

if __name__ == '__main__':
    print('\n\n-------------------------------')
    run_time = round((time.time() - start_time), 3)
    if run_time < 1:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time*1000)}ms at {datetime.now().strftime("%H:%M:%S")}.\n')
    elif run_time < 60:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time)}s at {datetime.now().strftime("%H:%M:%S")}.\n')
    elif run_time < 3600:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time/60)}mns at {datetime.now().strftime("%H:%M:%S")}.\n')
    else:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time/3600, 2)}hrs at {datetime.now().strftime("%H:%M:%S")}.\n')