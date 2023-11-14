echo "Building docker containers"
docker build --tag python-validator -f python.dockerfile .
docker build --tag typescript-validator -f typescript.dockerfile .
docker build --tag javascript-validator -f javascript.dockerfile .
pause