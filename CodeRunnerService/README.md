# CodeRunnerService

The CodeRunnerService contains 2 separate sections, the first is the codeRunnerAPI which manages incoming requests and assigns the request to a worker to be executed. The second section is that worker that receives an incoming request through a websocket and executes it in a docker container.

### codeRunnerAPI.py

The main focuses of the codeRunnerAPI are the websocket event handlers

The code below defines the socket event listeners:

```python
@socketio.on('connect')
def socket_connect():
    connected_workers[request.sid] = False
```

When a connection is made to the websocket server on the ``connect`` event the socket ID of the connection is added to a dictionary where the key is the socket ID and the value is the boolean status of the worker that defines whether the worker is currently working or not.

```python
@socketio.on('disconnect')
def socket_connect():
    connected_workers.pop(request.sid)
```

When a connection is disconnected or lost the socket ID is removed from the connected workers dictionary

```python
@socketio.on('submit_result')
def submit_result(data):
    connected_workers[request.sid] = False
```

The submit_result event is fired when the codeValidatorService returns the result of running the code

```python
@socketio.on("enqueue_code")
def enqueue_code(data):
    data["sid"] = request.sid
    pending_tasks.append(data)
```

The enqueue_code event is fired when the discord bot adds code to be ran to the queue in the codeRunnerAPI

### codeValidatorService.py

#### reciveLoop

We will walk through the codeValidator service step by step starting with the event handling loop

```python
while reciveLoop:
    event = io.receive()
    if event[0] == "run_code":
        json = event[1]
        result = validateCode(json["user_code"], json["validate_code"], json["lang"])
        io.emit("submit_result", [result, json["sid"]])
```

This while loop will wait for an incoming event named "run_code" using ``io.receive()``. Once this happens the arguments are sent to the ``validateCode`` function to be ran. Once the result is returned the service will sent the response back to the ``codeRunnerAPI`` using the ``io.emit("submit_result", [result, json["sid"]])`` function.

#### validateCode

The ``validateCode`` function shown below simply calls the function corresponding to the input ``lang`` argument:

```python
def validateCode(user_code: str, validate_code: str, lang):
    if lang == "python":
        return validate_python(user_code, validate_code)
    elif lang == "javascript":
        return validate_javascript(user_code, validate_code)
    elif lang == "typescript":
        return validate_typescript(user_code, validate_code)
```

Based on that ``lang`` argument the function will call one of 3 ``validate`` functions. For simplicity only validate_python will be shown here in the documentation, the other functions will be extremely similar to this one.

#### validate_python

```python
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
```

We start by creating a folder called `run` if it does not already exist. This folder acts as a temporary place to store the user and validation code. The function then adds the import for the testing module if it does not already exist. The function then calls the  ``manageThread`` function and finally cleans up and returns the result.

#### manageThread

```python
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
```

The ``manageThread`` function as shown above starts by creating a thread using the local scope function named ``target``. ``manageThread`` will then join this thread which will wait 5 seconds before automatically terminating the thread if the execution of the code takes too long.

#### runDocker

The ``runDocker`` function that is called in the local scope ``target`` function is what starts and manages the docker containers.

```python
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
```

The function starts by creating a docker container from the image that corresponds to the supplied language. Then the temporary files that were stored in the `run` directory are copied to the container's file system. The container is then started and the output of the user supplied code is stored by using the ``logs`` docker command. The result is then returned.
