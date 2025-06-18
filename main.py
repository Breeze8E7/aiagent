import os
import sys
from functions.funcs_for_agent import *
from dotenv import load_dotenv
from google import genai
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Retrieves the content of a file in the specified directory, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path (relative to the working directory) to the file with the content the user wants to retrieve.",
            ),
        },
    ),
)
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file in the specified directory, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path (relative to the working directory) to the file with the content the user wants to write to.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
    )
)
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a python file, constrained within the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path (relative to the working directory) of the python file to run.",
            ),
        },
    )
)
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)
system_prompt = """
You are a helpful AI coding agent.
When a user asks a question or makes a request, make a function call plan. You can perform the following operations:
- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files
All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""
verbose = False
continue_conversation = True
if "--verbose" in sys.argv:
    verbose = True
    sys.argv.remove("--verbose")
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
if len(sys.argv) < 2:
    print("Usage: python script.py '<your prompt here>'")
    sys.exit(1)
user_prompt = sys.argv[1]
messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]
while continue_conversation:
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
    )
    for part in response.candidates[0].content.parts:
        if isinstance(part, types.Part) and part.function_call:
            function_call_result = call_function(part.function_call, verbose)
            messages.append(response.candidates[0].content)
            messages.append(function_call_result)
            if function_call_result.parts[0].function_response.response:
                if verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")
            else:
                raise Exception("Function call did not return expected response structure")
        else:
            print(part.text)
            if verbose == True:
                print(f"User prompt: {user_prompt}")
                prompt_token_count = response.usage_metadata.prompt_token_count
                print(f"Prompt tokens: {prompt_token_count}")
                candidates_token_count = response.usage_metadata.candidates_token_count 
                print(f"Response tokens: {candidates_token_count}")
            continue_conversation = False