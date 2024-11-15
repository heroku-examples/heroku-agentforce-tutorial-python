Creating Agentforce Custom Actions with Heroku - Python
========================================================

This tutorial explains how to deploy a Heroku application written in Python that can be used to build an Agentforce custom action, extending the capabilities of any Agentforce agent with the power of Heroku's fully managed, elastic compute services.

> **_IN A HURRY?_** This application has already been deployed publicly and is available at [https://...](https://...) so that you can skip straight to [configuring Heroku based actions in your Salesforce organization](xxx) to try it out first.

App Authentication
------------------

Regardless how you access this app, you will need to complete or configure basic authentication. We have included this as a reminder that best practice is to consider authentication for APIs, especially those involved in AI interactions such as this. For APIs in general it is typical to use JWT based authentication. For the basic authentication setup here the default user name is `heroku` and the password is `agent`.

> **WARNING**: Carefully review your app authentication needs and requirements before deploying to production

Deploying to Heroku
-------------------

You can deploy this application to your Heroku account using the button below or manually using our CLI.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

To proceed with a CLI deployment install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) and login with your Heroku account (or [signup](https://signup.heroku.com/)). Then execute the following CLI commands:

```
git clone https://github.com/heroku-examples/heroku-agentforce-tutorial-python
cd heroku-agentforce-tutoral-python
heroku create myagentaction
git push heroku main
```

Once this has been deployed take note of the web URL then refer to the instructins in [configuring Heroku based actions in your Salesforce organization](xxx)

Running and Testing Locally
---------------------------

Although you cannot integrate this app with Agentforce until you deplo it, you can still develop and test your actions inputs and outputs locally, using the built in [Swagger UI](https://swagger.io/tools/swagger-ui/). Once you are happy with your changes refer to the deployment and configuraiton steps above.

```
git clone https://github.com/heroku-examples/heroku-agentforce-tutorial-python
cd heroku-agentforce-tutoral-python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Once the application is running navigate to the URL below, click the **Try it Out** button andcomplete the basic authentication as covered above.

```
http://127.0.0.1:5000
```