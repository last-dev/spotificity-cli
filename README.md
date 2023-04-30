
# **Spotificity AWS CDK App**

## **What is this? Why build it?**

Once upon a time, I used to stay updated with the latest music releases from some of my favorite artists. Engaging in discussions and debates about new music with my close friends was a great pastime. Nowadays, my focus on studying and coding, particularly in the pursuit of building artifacts to present during interviews, has made it difficult for me to keep up.

To address this, I have started to create a CRUD app that periodically queries Spotify using their API to obtain a list of the latest releases from selected artists and send me a text with any updates weekly.

Since this application needs to be stateful, it presents an excellent opportunity for me to learn the inner workings of AWS cloud technologies by using the **AWS Cloud Development Kit (CDK)**.

## **To-Do Checklist**

As of this initial commit, the app features a simple CLI interface that provides specific menu options to trigger Lambda functions. These functions perform CRUD actions on the table holding my list of artists along with their respective Spotify IDs.

Currently, I can view the artists in the table, add new artists to the list, or remove existing artists. Additionally, there is a Lambda function that manages the initial authentication required to interact with Spotify's API.

My ever changing todo list is:

- [x] Start adding unit tests for current stage of application.
- [] Add table attributes to each artist that has their last 3 singles, last 3 songs they were featured on, and last album
- [] Create Lambda function that will query Spotify for new releases from current list. This function will publish updates to AWS SNS topic and update table.
- [] Implement Cloudwatch Event that will trigger that Lambda every so often (TBD).
- [] Create simple in-browser frontend where I can view and interact with my table.

## ***Development***

Some notes on development for me.

- Activate virtual environment inside project directory: `source .venv/bin/activate`
- Install the required dependencies: `pip install -r requirements.txt`
- Create CloudFormation template: `cdk synth`
- Compare deployed stack with current local state: `cdk diff`
- Deploy this stack to my default AWS account/region: `cdk deploy`

### Unit Testing

1. Activate virtual environment: `source .venv/bin/activate`
2. Install the required test dependencies: `pip install -r requirements-dev.txt`
3. Run `python -m pytest` within `cdk/` or within `cli/`. Don't run in root folder.
