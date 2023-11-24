import subprocess
import os
import random
import shutil
import string
import threading
import shutil
import time
import signal
import socketio

reciveLoop = True


def validateCode(user_code: str, validate_code: str, lang):
    if lang == "python":
        return validate_python(user_code, validate_code)
    elif lang == "javascript":
        return validate_javascript(user_code, validate_code)
    elif lang == "typescript":
        return validate_typescript(user_code, validate_code)


def validate_python(user_code: str, validate_code: str):
    if not os.path.isdir("run"):
        os.mkdir("run")

    fileID = generateRandomId()
    os.mkdir(f"run/{fileID}")

    with open(f"run/{fileID}/solution.py", "w", encoding="utf-8") as file:
        file.write(user_code)
    with open(f"run/{fileID}/test.py", "w", encoding="utf-8") as file:
        if "import codewars_test as test" not in validate_code:
            validate_code = "import codewars_test as test\n" + validate_code
        file.write(validate_code)

    result = manageThread(fileID, "python")

    shutil.rmtree(f"run/{fileID}")
    return result


def validate_javascript(user_code: str, validate_code: str):
    if not os.path.isdir("run"):
        os.mkdir("run")

    fileID = generateRandomId()
    os.mkdir(f"run/{fileID}")

    data = ""
    with open(f"CodingChallengerBot/DockerFiles/test.js", "r", encoding="utf-8") as file:
        data = file.read()

    with open(f"run/{fileID}/test.js", "w", encoding="utf-8") as file:
        file.write(data + "\n")
        file.write(user_code + "\n")
        file.write(validate_code)

    result = manageThread(fileID, "javascript")

    shutil.rmtree(f"run/{fileID}")
    return result


def validate_typescript(user_code: str, validate_code: str):
    if not os.path.isdir("run"):
        os.mkdir("run")

    fileID = generateRandomId()
    os.mkdir(f"run/{fileID}")

    data = ""
    with open(f"CodingChallengerBot/DockerFiles/test.ts", "r", encoding="utf-8") as file:
        data = file.read()

    with open(f"run/{fileID}/solution.ts", "w", encoding="utf-8") as file:
        file.write(user_code)

    with open(f"run/{fileID}/test.ts", "w", encoding="utf-8") as file:
        file.write(data + "\n")
        file.write(validate_code)

    result = manageThread(fileID, "typescript")

    shutil.rmtree(f"run/{fileID}")
    return result


def generateRandomId(length=6):
    characters = string.ascii_lowercase + string.digits
    random_id = "".join(random.choice(characters) for _ in range(length))
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
        subprocess.run(f"docker kill {fileID}", stdout=subprocess.DEVNULL)
    return result


def runDocker(fileID, lang):
    subprocess.run(
        f"docker create --network none --cpus 1 -m 300m --name {fileID} {lang}-validator:latest",
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        f"docker cp run/{fileID}/. {fileID}:/workspace", stdout=subprocess.DEVNULL
    )
    subprocess.run(f"docker start {fileID}", stdout=subprocess.DEVNULL)
    subprocess.run(f"docker wait {fileID}", stdout=subprocess.DEVNULL)
    result = subprocess.run(
        f"docker logs {fileID}", stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    subprocess.run(f"docker rm -f {fileID}", stdout=subprocess.DEVNULL)
    if result.stdout.decode() != "":
        return result.stdout.decode()
    return "<SYSTEM::>" + result.stderr.decode()


io = socketio.SimpleClient()
io.connect("http://localhost:8989", transports=["websocket"])


def handle_interrupt(signum, frame):
    global reciveLoop
    print("Code Validator Terminating...")
    reciveLoop = False
    exit(0)
signal.signal(signal.SIGINT, handle_interrupt)
signal.signal(signal.SIGTERM, handle_interrupt)


while reciveLoop:
    event = io.receive()
    if event[0] == "run_code":
        json = event[1]
        result = validateCode(json["user_code"], json["validate_code"], json["lang"])
        io.emit("submit_result", [result, json["sid"]])