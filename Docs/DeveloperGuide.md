# HomeWise Backend Development Guide

## Source Code Overview

		git repository contains:
			.ebextensions
				django.config
				db-migrate.config
			.elasticbeanstalk
				config.yml
			Agent
				...
			HomeWiseDjango
				...
				settings.py
				local_settings.py
			.gitignore
			manage.py
			requirements.txt

`.ebextensions/django.config`
	[Option settings](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/ebextensions-optionsettings.html) to set `DJANGO_SETTING_MODULE` environment variable during deployment, as well as path to application - the wsgi file.

`.ebextensions/db-migrate.config`
	[Container commands](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/customize-containers-ec2.html#linux-container-commands) to run database migration during deployment.

`.elasticbeanstalk/config.yml`
	Elastic Beanstalk configuration file, for use with [awsebcli](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html) and created with `eb init`.

`HomeWiseDjango/settings.py`
	Django settings file for *production*.
		HTTPS/SSL Enabled
		DEBUG set to *False*
		ALLOWED_HOSTS include production domains
		DATABASES uses PostgreSQL on AWS
		TIME_ZONE synced with AWS Region
		SECRET_KEY set in environment variables

`HomeWiseDjango/local_settings.py`
	Django settings file for *development*.
		HTTPS/SSL Disabled
		DEBUG set to *True*
		ALLOWED_HOSTS only has localhost
		DATABASES uses sqlite
		TIME_ZONE set to UTC
		SECRET_KEY hardcoded in file

`requirements.txt`
	Contains python package dependencies.

## Setup Local Development Environment

1. Clone git repository
2. Install python packages: `pip install -r requirements.txt`
	1. It is recommended to use `virtualenv` for this project. More information on virtual environments: [https://virtualenv.pypa.io/en/stable/](https://virtualenv.pypa.io/en/stable/)
3. Set `DJANGO_SETTINGS_MODULE` environment module
	1. **Unix Bash**
		1. `export DJANGO_SETTINGS_MODULE=HomeWiseDjango.local_settings`
	2. **Windows**
		2. `set DJANGO_SETTINGS_MODULE=HomeWiseDjango.local_settings`
4. Run database migration
	1. `python manage.py migrate`
5. Run server
	1. `django-admin runserver`

## Elastic Beanstalk Deployment

This backend is currently deployed to Amazon Web Services (AWS) via the [Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/) tool. The preferred method of deploying to the service is a combination of application versioning with git the [AWS Command Line Interface](https://aws.amazon.com/cli/) for deployment.

### Setting up AWS CLI

[AWS Command Line Interface](https://aws.amazon.com/cli/) can be installed on your local machine. Once installed, run `aws configure` to authenticate with the AWS account to which the application will be deployed. This command requires an *AWS Access Key ID* and *AWS Secret Access Key* which are generated via the **My Security Credentials** tab in the top-right corner of the AWS website.

### Connecting to Elastic Beanstalk with awsebcli

Elastic Beanstalk has its own CLI package, [awsebcli](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html), which is installed in a similar manner. Once installed, it will use the AWS credentials provided in the previous step. The tool is accessed via the command `eb`.

`eb` commands will use the configuration specified in `.elasticbeanstalk/config.yml`

`eb status` lists the status of the current environment

### Deploying to the Elastic Beanstalk environment

The `eb` tool deploys new code by tracking versions of the application. For this reason, you must first commit your changes with `git commit` before deploying code.

`eb deploy` will deploy the latest commit, as well as output the events of the Elastic Beanstalk instance.

### Accessing the EC2 instance

Every Elastic Beanstalk application creates at least one EC2 instance to run the application code. Since an EC2 instance is just a server, it is possible to access this instance via ssh and run commands remotely.

To connect to the EC2 instance associated with this application run `eb ssh`

The command will check for the appropriate ssh private key which must be in the appropriate ssh keys folder depending on your local machine. To see the private key associated with this EC2 instance you can login to the AWS management console, navigate to EC2, and view generated private keys.
