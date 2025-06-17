import os
import subprocess

def get_files_info(working_directory, directory=None):
    try:
        if directory is None:
            target_path = os.path.abspath(working_directory)
        else:
            target_path = os.path.abspath(os.path.join(working_directory, directory))
        work_dir_path = os.path.abspath(working_directory)
        # 1. Guardrail check: is target_path inside work_dir_path?
        if not target_path.startswith(work_dir_path):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        # 2. Is the target path a directory?
        if not os.path.isdir(target_path):
            return f'Error: "{directory}" is not a directory'
        # 3. List directory contents
        files_info = ""
        for filename in os.listdir(target_path):
            file_path = os.path.join(target_path, filename)
            file_size = os.path.getsize(file_path)
            file_is_dir = os.path.isdir(file_path)
            files_info += (f"- {filename}: file_size={file_size} bytes, is_dir={file_is_dir}\n")
        if not files_info:
            files_info = "No files found in the directory."
        return files_info
    except Exception as e:
        return f'Error: {str(e)}'

def get_file_content(working_directory, file_path):
    MAX_FILE_SIZE = 10001
    try:
        target_path = os.path.abspath(os.path.join(working_directory, file_path))
        work_dir_path = os.path.abspath(working_directory)
        # 1. Guardrail check: is target_path inside work_dir_path?
        if not target_path.startswith(work_dir_path):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        # 2. Is the target path a file?
        if not os.path.isfile(target_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        # 3. Read file content
        with open(target_path, 'r', encoding='utf-8') as file:
            content = file.read(MAX_FILE_SIZE)
            if len(content) > 10000:
                content = content[:10000] + '[...File "{file_path}" truncated at 10000 characters]'
        return content
    except Exception as e:
        return f'Error: {str(e)}'
    
def write_file(working_directory, file_path, content):
    try:
        target_path = os.path.abspath(os.path.join(working_directory, file_path))
        work_dir_path = os.path.abspath(working_directory)
        # 1. Guardrail check: is target_path inside work_dir_path?
        if not target_path.startswith(work_dir_path):
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        # 2. Write file content
        os.path.exists(os.path.dirname(target_path)) or os.makedirs(os.path.dirname(target_path))
        with open(target_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f'Error: {str(e)}'
    
def run_python_file(working_directory, file_path):
    try:
        target_path = os.path.abspath(os.path.join(working_directory, file_path))
        work_dir_path = os.path.abspath(working_directory)
        # 1. Guardrail check: is target_path inside work_dir_path?
        if not target_path.startswith(work_dir_path):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        # 2. Is the target path a file?
        if not os.path.isfile(target_path):
            return f'Error: File "{file_path}" not found.'
        # 3. If the file doesn't end with ".py", return an error string:
        if not target_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file.'
        # 4. Run the Python file with a timeout of 30 seconds
        result = subprocess.run(['python', target_path], timeout=30, cwd=work_dir_path, capture_output=True, text=True)
        statement = f'STDOUT: {result.stdout} \nSTDERR: {result.stderr}'
        if result.returncode != 0:
            statement += f'\nProcess exited with code {result.returncode}'
        if not result.stdout and not result.stderr:
            statement = 'No output produced.'
        return statement
    except Exception as e:
        return f"Error: executing Python file: {e}"