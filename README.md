# App
This repo is created for the course Release Engineering for Machine Learning Applications. It contains the app-image which can interface with any model URL which is specified during the launch of the dockerfile using REST API's.

Important for passing enivornment variables: https://stackoverflow.com/questions/49770999/docker-env-for-python-variables
In essence just run the following command:
`docker run -e MODEL_URL=https://corncobs.com ... <image-name> ...`

