#!/usr/bin/env python3
import sys
import importlib
import subprocess
import os
import re
import shutil

ITM_DIR = os.path.dirname(os.path.realpath(__file__))

def install_python() -> None:
    print("Please install Python 3.10 or Python 3.11 before continuing.")
    sys.exit(1)

def install_venv() -> None:
    print("Please install venv. On Ubuntu/Debian, try 'sudo apt install python3-venv'.")
    sys.exit(1)

def handle_creation_error(path: str) -> None:
    print("Could not create %s. Check permissions." % str(path))
    sys.exit(1)

def handle_git_missing() -> None:
    print("Please install git and ensure it's in your PATH.")
    sys.exit(1)

def handle_download_problem(repo_name: str) -> None:
    print("Failure attempting to clone %s project. Check connectivity and access permissions."
          % repo_name)
    sys.exit(1)

def install_repo(git_path: str, ldir: str | None = None) -> str:
    """ Will clone `git_path` into `ldir`. If `ldir` isn't passsed, will
        use .deprepos/(project_name) """
    m = re.search(r".*/(.*)\.git", git_path)
    assert m is not None, f"Invalid git path: {git_path}"
    project_name = m.group(1)

    if ldir is None:
        ldir = os.path.join(".deprepos", project_name)
    if os.path.exists(ldir):
        print("Dependency repo already installed: " + ldir)
        return ldir
    lp = subprocess.run(["git", "clone", git_path, ldir], check=False)
    if lp.returncode != 0:
        handle_download_problem(ldir)
    return ldir

def install_server(git_path: str) -> None:
    ldir = install_repo(git_path)
    lbuilder = venv.EnvBuilder(with_pip=True, upgrade_deps=True)
    try:
        lbuilder.create(os.path.join(ldir, "venv"))
    except PermissionError:
        print(f"Could not create virtual environment in {ldir}. Check to see if a program is "
              + "already running from this directory, or files are read-only.")
        sys.exit(1)
    lctxt = lbuilder.ensure_directories(os.path.join(ldir, "venv"))
    _ = subprocess.run([lctxt.env_exe, "-m", "pip", "install", "-r",
                                      os.path.join(ldir, "requirements.txt")], check=True)


def run_cmd_or_die(argv: list[str], capture_output: bool = False, err_msg: str | None = None) -> str:
    """ Just a wrapper around some common subprocess.run() stuff """
    p: subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]
    if capture_output:
        p = subprocess.run(argv, check=False, capture_output=True, text=True)
    else:
        p = subprocess.run(argv, check=False)
    if 0 != p.returncode:
        if err_msg is not None:
            print(err_msg)
        sys.exit(1)

    if capture_output:
        assert type(p.stdout) is str
        return p.stdout
    return ''

os.chdir(ITM_DIR)

try:
    if sys.version_info.major < 3 or sys.version_info.minor < 10 \
                                  or sys.version_info.minor > 11:
        install_python()
except:
    install_python()

try:
    importlib.import_module("venv")
except:
    install_venv()

import venv
builder = venv.EnvBuilder(with_pip=True, upgrade_deps=True)
try:
    builder.create("venv")
except PermissionError:
    print("Could not create virtual environment in venv. Check to see if a program is "
          + "already running from this directory, or files are read-only.")
    sys.exit(1)
except shutil.SameFileError as err:
    print("Error occurred: ")
    print(str(err))
    print("If you are in an activated environment in this directory, deactivate. Otherwise, if "
          + "there is a sim link to Python at the venv location referenced by the above error, "
          + "delete and rerun.")
    sys.exit(1)
    
ctxt = builder.ensure_directories("venv")
subprocess.run([ctxt.env_exe, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

try:
    os.makedirs(".deprepos")
except FileExistsError:
    pass
except:
    handle_creation_error(".deprepos")



try:
    p = subprocess.run(["git", "--version"], check=False)
    if p.returncode != 0:
        handle_git_missing()
except:
    handle_git_missing()

print("Installing TA3 client")
#install_repo("git@github.com:NextCenturyCorporation/itm-evaluation-client.git")
install_repo("https://github.com/NextCenturyCorporation/itm-evaluation-client.git")

subprocess.run([ctxt.env_exe, "-m", "pip", "install", "-e",
                              os.path.join(".deprepos", "itm-evaluation-client")], check=True)

