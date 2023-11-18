echo "Building docker images..."

echo "Removing old images..."
docker image rm python-validator:latest
docker image rm typescript-validator:latest
docker image rm javascript-validator:latest

echo "Building new images..."
docker build --tag python-validator -f CodingChallengerBot\DockerFiles\python.dockerfile .
docker build --tag typescript-validator -f CodingChallengerBot\DockerFiles\typescript.dockerfile .
docker build --tag javascript-validator -f CodingChallengerBot\DockerFiles\javascript.dockerfile .