# pathlib is used for handling file and directory paths easily
# subprocess is used to run system shell commands from python
# tuple from typing is used to specify function return types as tuples
# Imports decorator to define langchain tools
import pathlib
import subprocess
from typing import Tuple
from langchain_core.tools import tool

# define the project root directory inside the current working directory
PROJECT_ROOT = pathlib.Path.cwd() / "generated_project"

# this is the function which is used to check whether the given path current in safe to use or is it trying to escape the directory
def safe_path_for_project(path: str) -> pathlib.Path:
    """Ensures that the path stays inside the project root (security check)."""

    # it resolves the absolute path of the target file
    # meaning that it interpret the .. or . in path to show its actual directory
    p = (PROJECT_ROOT / path).resolve()

    # prevents writing files outside the project root directory
    # it actually raise valueerror is the below condition is meet
    # p.parents means it show every possible parents of the current path
    # this is the example
    # PosixPath('/Users/rishabh/generated_project/data/logs'),
    # PosixPath('/Users/rishabh/generated_project/data'),
    # PosixPath('/Users/rishabh/generated_project'),
    # PosixPath('/Users/rishabh'),
    # PosixPath('/Users'),
    # PosixPath('/')
    if PROJECT_ROOT.resolve() not in p.parents and PROJECT_ROOT.resolve() != p:
        # raises error if file is outside the root
        raise ValueError("Attempt to write outside project root")

    # return the safe resolved path
    return p

# this function is used to write content in the given file
@tool
def write_file(path: str, content: str) -> str:
    """Writes content to a file within the project root."""

    # ensures file path is safe
    p = safe_path_for_project(path)

    # creates directories if they don't exist
    p.parent.mkdir(parents=True, exist_ok=True)

    # Opens file in write mode with UTF-8 encoding
    with open(p, "w", encoding="utf-8") as f:
        # writes the provided content to the file
        f.write(content)

    # returns a message confirming file creation
    return f"WROTE:{p}"

# this function is used to read the content from the file of give path and return empty string if the path does not exist
@tool
def read_file(path: str) -> str:
    """Reads content from a file within the project root."""

    # ensure the file path is safe
    p = safe_path_for_project(path)

    # checks if the file exists
    if not p.exists():
        # returns empty string if file not found 
        return ""

    # Opens file in the read mode
    with open(p, "r", encoding="utf-8") as f:
        # return the file content
        return f.read()

# this function is used to get the current working directory which was PROJECT ROOT directory
@tool
def get_current_directory() -> str:
    """Returns the current working directory (project root)."""

    # Converts project root path to string and returns it
    return str(PROJECT_ROOT)

# p.glob("**/*") List everything inside the folder, no matter how deeply nested.
# if the output is :
#     /home/rishabh/project/data/info.csv
#     /home/rishabh/project/data/reports/report1.pdf
# f.relative_to(PROJECT_ROOT):
#   makes paths neat and relative to your project root:
#         data/info.csv
#         data/reports/report1.pdf
# *	Match everything (any file or folder name) in the current directory only
# **	Match everything recursively — including all subdirectories
# **/*	Match all files/folders inside this folder and its subfolders
# this function is used to list all the files in the directory which are related to PROJECT_ROOT
@tool
def list_files(directory: str = ".") -> str:
    """Lists all the files in a given directory inside the project root."""

    # Ensures directory path is safe
    p = safe_path_for_project(directory)

    # checks if the path is actually a directory
    if not p.is_dir():
        # returns error if not a directory
        return f"ERROR: {p} is not a directory"

    # lists all files paths (relative to project root) in the directory and subdirectories
    files = [str(f.relative_to(PROJECT_ROOT)) for f in p.glob("**/*") if f.is_file()]

    # Returns file list or a message if empty
    return "\n".join(files) if files else "No files found."

# capture_output=True → captures both stdout and stderr
# this function is used to first check the current working direcotry and if that is done then it run the given shell command in the directory
@tool
def run_cmd(cmd: str, cwd: str = None, timeout: int = 30) -> Tuple[int, str, str]:
    """Runs a shell command in a directory and returns code, output, and error."""

    # sets working directory safely
    cwd_dir = safe_path_for_project(cwd) if cwd else PROJECT_ROOT

    # Executes shell command with timeout, capturing stdout and stderr
    res = subprocess.run(cmd, shell=True, cwd=str(cwd_dir), capture_output=True, text=True, timeout=timeout)

    # returns exit code, standard output, and error output
    return res.returncode, res.stdout, res.stderr

# this function is used to make the directory of the PROJECT_ROOT and return it
def init_project_root():
    """Creates the project root folder if it doesn't exist."""

    # Creates the root directory safely
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)

    # Returns the root directory path as string
    return str(PROJECT_ROOT)