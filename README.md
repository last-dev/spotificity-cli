
# **Spotificity (AWS CDK App)**

## **What is this? Why build it?**

Once upon a time, I used to stay updated with the latest music releases from some of my favorite artists. Engaging in discussions and debates about new music with my close friends was a great pastime. Nowadays, my focus on studying and coding, has made it difficult for me to keep up.

To address this, I've created a CRUD app that periodically queries Spotify's API to obtain a list of the latest releases from select artists and send me an email with any updates every Sunday. 

>***"But Spotify already offers notifications for when an artist drops, what gives?"*** 

The reason I prefer receiving a notification every Sunday is that it allows me to plan around digesting the new music, as opposed to having to jump right on the notification when Spotify sends it.

Since this application needs to be stateful, it presents an excellent opportunity for me to learn the inner workings of AWS cloud technologies by using the **AWS Cloud Development Kit (CDK)**.

## **To-Do Checklist**

As of this initial commit, the app features a simple CLI interface that provides specific menu options to trigger Lambda functions. These functions perform CRUD actions on the table holding my list of artists along with their respective Spotify IDs.

Currently, I can view the artists in the table, add new artists to the list, or remove existing artists. Additionally, there is a Lambda function that manages the initial authentication required to interact with Spotify's API.

Current todo list is:

- [] Continue to brainstorm how I can better layout my new music email.
- [] Research if Apple has an API for the iTunes store so I can include a link to purchase any of the new music.
- [] Optimize CLI to reduce latency between actions. More in-memory caching? Asynchronous functions for concurrency?
- [] Create simple in-browser frontend where I can view and interact with my table.

## **Development**

Some notes on development for me.

- Activate virtual environment inside project directory: `source .venv/bin/activate`
- Install the required dependencies: `pip install -r requirements.txt`
- Deploy to my default AWS account/region:
   1. Change to `cdk/` directory
   2. `cdk deploy [stack_name]` or `cdk deploy --all`
- Run local CLI app:
   1. Change into the `cli/` directory
   2. `python spotificity.py`
