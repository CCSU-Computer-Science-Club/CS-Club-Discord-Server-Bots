import subprocess
import os
import random
import shutil
import string
import threading

def validateCode(user_code, validate_code, lang):
    if (lang == "python"):
        return validate_python(user_code, validate_code)
    elif (lang == "javascript"):
        return validate_javascript(user_code, validate_code)
    elif (lang == "typescript"):
        return validate_typescript(user_code, validate_code)


def validate_python(user_code, validate_code):

    if (not os.path.isdir('run')):
         os.mkdir("run")

    fileID = generateRandomId()
    os.mkdir(f"run/{fileID}")

    with open(f'run/{fileID}/solution.py', 'w') as file:
        file.write(user_code)
    with open(f'run/{fileID}/test.py', 'w') as file:
        file.write(validate_code)

    result = manageThread(fileID, "python")

    shutil.rmtree(f"run/{fileID}")
    return result

def validate_javascript(user_code, validate_code):

    if (not os.path.isdir('run')):
         os.mkdir("run")

    fileID = generateRandomId()
    os.mkdir(f"run/{fileID}")

    data = ""
    with open(f'test.js', 'r') as file:
        data = file.read()

    with open(f'run/{fileID}/test.js', 'w') as file:
        file.write(data + "\n")
        file.write(user_code + "\n")
        file.write(validate_code)


    result = manageThread(fileID, "javascript")


    shutil.rmtree(f"run/{fileID}")
    return result

def validate_typescript(user_code, validate_code):

    if (not os.path.isdir('run')):
         os.mkdir("run")

    fileID = generateRandomId()
    os.mkdir(f"run/{fileID}")

    data = ""
    with open(f'test.ts', 'r') as file:
        data = file.read()

    with open(f'run/{fileID}/solution.ts', 'w') as file:
        file.write(user_code)

    with open(f'run/{fileID}/test.ts', 'w') as file:
        file.write(data + "\n")
        file.write(validate_code)

    result = manageThread(fileID, "typescript")

    shutil.rmtree(f"run/{fileID}")
    return result


def generateRandomId(length=6):
    characters = string.ascii_lowercase + string.digits
    random_id = ''.join(random.choice(characters) for _ in range(length))
    return random_id

def manageThread(fileID, lang):
        result = None
        def target():
            nonlocal result
            result = runDocker(fileID, lang)
            return
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout=5)

        if thread.is_alive():
            result = "<SYSTEM::>Execution took too long"
            subprocess.run(f"docker kill {fileID}", stdout = subprocess.DEVNULL)
        return result

def runDocker(fileID, lang, timeout=2000):
    subprocess.run(f"docker create --cpus 1 -m 300m --name {fileID} {lang}-validator:latest", stdout = subprocess.DEVNULL)
    subprocess.run(f"docker cp run/{fileID}/. {fileID}:/workspace", stdout = subprocess.DEVNULL)
    subprocess.run(f"docker start {fileID}", stdout = subprocess.DEVNULL)
    subprocess.run(f"docker wait {fileID}", stdout = subprocess.DEVNULL)
    result = subprocess.run(f"docker logs {fileID}", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(f"docker rm -f {fileID}", stdout = subprocess.DEVNULL)
    if result.stdout.decode() != "":
        return result.stdout.decode()
    return "<SYSTEM::>" + result.stderr.decode()