
# **Spotificity (AWS CDK App)**

## **What is this? Why build it?**

Once upon a time, I used to stay updated with the latest music releases from some of my favorite artists. Engaging in discussions and debates about new music with my close friends was a great pastime. Nowadays, my focus on studying and coding, has made it difficult for me to keep up.

To address this, I have started to create a CRUD app that periodically queries Spotify using their API to obtain a list of the latest releases from select artists and send me an email with any updates every Sunday. 

***"But Spotify already offers notifications for when an artist drops, what gives?"*** The reason I prefer receiving a notification every Sunday is that it allows me to plan around digesting the new music, as opposed to having to jump right on the notification when Spotify sends it.

Since this application needs to be stateful, it presents an excellent opportunity for me to learn the inner workings of AWS cloud technologies by using the **AWS Cloud Development Kit (CDK)**.

## **To-Do Checklist**

As of this initial commit, the app features a simple CLI interface that provides specific menu options to trigger Lambda functions. These functions perform CRUD actions on the table holding my list of artists along with their respective Spotify IDs.

Currently, I can view the artists in the table, add new artists to the list, or remove existing artists. Additionally, there is a Lambda function that manages the initial authentication required to interact with Spotify's API.

My ever changing todo list is:

- [x] ~~Create Lambda function that fetches artist's last single (with metadata), last album (with metadata), and last 3 songs they were featured on. (It turns out Spotify does not have an easy way to pull tracks artist is only featured on)~~
- [x] ~~Activate DynamoDB stream that triggers `GetLatestMusic` Lambda when new artist is added to table. (Decided against step function)~~
- [x] ~~Implement AWS SNS functionality.~~
- [x] ~~Implement EventBridge Rule that will trigger a Step Function every so often (TBD) to check for new music. This will then publish updates to the SNS topic.~~
- [x] ~~All client side Lambda invocations use API Gateway instead of boto3.~~
- [] Continue to brainstorm how I can better layout my new music email.
- [] Research if Apple has an API for the iTunes store so I can include a link to purchase any of the new music.
- [] Introduce better logging. Combing over my CloudWatch logs right now is... interesting.
- [] Optimize CLI to reduce latency between actions. More in-memory caching? Asynchronous functions for concurrency?
- [] Create simple in-browser frontend where I can view and interact with my table.

## **Development**

Some notes on development for me.

- Activate virtual environment inside project directory: `source .venv/bin/activate`
- Install the required dependencies: `pip install -r requirements.txt`
- Create CloudFormation template: `cdk synth`
- Compare deployed stack with current local state: `cdk diff`
- Deploy this stack to my default AWS account/region: `cdk deploy`

### Unit Testing

1. Activate virtual environment: `source .venv/bin/activate`
2. Install the required test dependencies: `pip install -r requirements-dev.txt`
3. Make sure there is an `__init__.py` file located in the root of the `cdk/` directory.
4. Run `python -m pytest` within `cdk/` or within `cli/`. Don't run in root folder.
