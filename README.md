# App
This repo is created for the course Release Engineering for Machine Learning Applications. It contains the app-image which can interface with any model URL which is specified during the launch of the dockerfile using REST API's.

Important for passing enivornment variables: https://stackoverflow.com/questions/49770999/docker-env-for-python-variables
In essence just run the following command:
`docker run -e MODEL_URL=https://corncobs.com ... <image-name> ...`

Make sure to map the container's port 8080 to host port 8080 so you can access the website using `https://localhost:8080`.
So full command is:
`docker run -e MODEL_URL=https://corncobs.com -p 8080:8080: ... <image-name> ...`