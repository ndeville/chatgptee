"""
Replicate the ChatGPT desktop app experience in the terminal.
More lightweight.
More keybord controls / ability to define custom keybindings.
Define default model.

v2:
+ add more models, ie run different models in parallel to compare answers.
"""


from datetime import datetime
import os
ts_db = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
ts_time = f"{datetime.now().strftime('%H:%M:%S')}"
print(f"\n---------- {ts_time} starting {os.path.basename(__file__)}")
import time
start_time = time.time()

from dotenv import load_dotenv
load_dotenv()

import openai
import os
import time
from typing_extensions import override
from openai import AssistantEventHandler

# Set up OpenAI API key (use environment variable for security)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Replace with your Assistant ID
ASSISTANT_ID = os.getenv("NIC_KAL_GPT")

# Create a new OpenAI client
client = openai.OpenAI()

# Create a new thread
thread = client.beta.threads.create()

class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print("\nChatGPT:", end=" ", flush=True)
    
    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)
    
    @override
    def on_tool_call_created(self, tool_call):
        print(f"\nChatGPT: {tool_call.type}\n", flush=True)
    
    @override
    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print("\n\nOutput:", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == "exit":
        break

    # Send user message
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_input
    )
    
    # Stream Assistant response
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()
    
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