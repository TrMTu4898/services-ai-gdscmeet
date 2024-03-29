# AIGDSCMeet - AI GDSCMeet Service

## Introduction

AIGDSCMeet is a project that utilizes technologies such as FastAPI, Socket.IO, Gunicorn, PyTorch, CUDA, and Transformers to process and extract information from audio in meetings using GPU acceleration.

## System Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [NVIDIA Docker Toolkit](https://github.com/NVIDIA/nvidia-docker)
- [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

## Installation

1. Clone the project from GitHub:

    ```bash
    git clone https://github.com/TrMTu4898/services-ai-gdscmeet.git
    cd services-ai-gdscmeet
    ```

2. Run Docker Compose:

    ```bash
    docker-compose up --build
    ```

3. Access the application at [ws://127.0.0.1:5000/](ws://127.0.0.1:5000/)

## Project Structure

- `APIAI/main.py`: Contains the main source code for the FastAPI, Gunicorn, Uvicorn for AI function.
- `AIGDSCMeet/main.py`: Container the main source code for SocketIO, FastAPI, Uvicorn connect to the client at the gateway [ws://127.0.0.1:5000/].
- `APIAI/Dockerfile`: Dockerfile to build the Docker image for the api alication.
- `AIGDSCMeet/Dockerfile`: Dockerfile to build the Docker image for socketIO application.
- `docker-compose.yml`: Docker Compose configuration file.
- `APIAI/requirements.txt`: List of Python dependencies for APIAI.
- `AIGDSCMeet/requirements.txt`: List of Python dependencies for AIDSCMeet.

## Usage

1. After installation and running, access [ws://127.0.0.1:5000/](ws://127.0.0.1:5000/) in your web browser.
2. [Instructions for use](https://github.com/TrMTu4898/speech-to-text-client.git)
3. Perform actions on the interface to interact with the application.

## For example
-   ```
    //Initialize socket connection
    const socket = io.connect('ws://127.0.0.1:5000/', {
        auth: user_info
    });

    //Connect to the server
    socket.on('connect', () => {
        console.log('Connected to the server!');
    });

    //Disconnect from the server
    socket.on('disconnect', () => {
        console.log('Disconnected from the server!');
    });

    //Send data to the server
    socket.emit('speech_to_text_result', interimResults)


    //Receive results from the server
    socket.on('speechToKeywords', (result) => {
        console.log('Speech to Keywords Result:', result);
    });
    ```
    
## Notes

- Ensure your computer has a GPU compatible with CUDA for optimal performance of the project.

- To optimize GPU performance, make sure to install the NVIDIA Docker Toolkit and CUDA Toolkit correctly.

- If you encounter issues, check the logs of the containers for detailed information.

