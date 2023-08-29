# powerplant-coding-challenge
#### As implemented by Steve Gilissen

## Setup
### Create a virtualenv
```shell
virtualenv powerplant_challenge
```
### Activate the virtualenv
Linux/Unix/Mac
```shell
source powerplant_challenge/bin/activate
```
... or for Windows:
```shell
.\powerplant_challenge\Scripts\activate
```

### Install required packages using pip
```shell
pip install -r requirements.txt
```

## Running the project
```shell
python app.py
```
The Flask dev server will start:
```shell
[2023-08-29 19:58:17,759][INFO]: Starting application...
 * Serving Flask app 'app'
 * Debug mode: on
[2023-08-29 19:58:17,761][INFO]: WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8888
```
You can then do a POST to 127.0.0.1:8888 with the JSON payload