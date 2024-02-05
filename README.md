# Building a real-time chat application using Python, Django, and Redis.

The application should allow users to send and receive messages in real-time, using a technology such as WebSockets.
The application should be built using Python, Django and should include proper routing, error handling and form validation
The application should use Redis to implement real-time functionality, so all part about messages should be stored both in Redis (for fast response), not in a database (in case someone refresh page or add to the conversation, you will need to retrieve all messages for that conversation).
Use a database (PostgresSQL/MySQL) to manage users, and maybe conversation ids.
The application should include proper logging and monitoring.

#### Considerations:

* API URL structure is up to you.
* Initial data for sign up: name, last name, email.
* Validation rules for signup data are up to you.
* Json structure is up to you.
* It will be a big plus if you deploy the services somewhere in the cloud (heroku, gcloud, aws, azure, etc). It's ok if you just do it locally, but use docker.
* Use github (or other git repo). It's a big plus to include github actions.
* Do tests and integrations tests.
* Programming language: Python.

_BONUS: If you can implement API throttling for messages in real time, that's a big one. Throttling rules are up to you (1 API call per second allowed or 10 API calls per minute, etc).
Log every API call received, log format is up to you.
Place a README.md file with instructions in the github repo so test can be performed and checked._

## Django Chat Application

The application was developed Django 4.2 (python 3.8.15 env), using [Django-Channels](https://channels.readthedocs.io/en/latest/). It uses Redis as a DB to provide real time messages to the queue, and also saves all messages to a Postgres DB for persistance.
It has a simple django form web interface for user registration and login/logout, and room selection

#### To run local server

Dependencies: having `docker` and `docker-compose` installed locally.

From the root folder of the application, run the following command: `ENVIRON=local docker-compose -f ./docker/docker-compose.yml up --build`

_**To create a chat room, you will have to go to the Django-admin console (`127.0.0.1:8000/admin`) and create a new Room object.**_

#### Resgister and log in

To register a new user, you can click on the **Sign Up** button on the top right corner of the web, fill with username, password and confirm password (beware, this has Django password check). This will create a new user and log in, and redirect to the Room selection web.

_**START CHATTING**_

#### To run unit tests

From the project root folder of the application, run `python manage.py test` to run all unit tests.

#### Message throttling

- I applied a custom message throttling service to fulfill project's necessities.
- You can configure the message rate using the following Django config setting `WEBSOCKET_THROTTLE="10/second`.
- You can use any combination you like with `["year", "month", "day", "hour", "minute", "second"]` time parameters.
- You can also set `WEBSOCKET_THROTTLE=unlimited` to deactivate throttling at all.
- If wrong config format is submitted, throttling will defailt to "10/second" config.


#### Final note
This repo include Github actions to run linter and unit testing for CI.
Deployment was not achieved yet because of configuration issues with the Daphne ASGI web server.
