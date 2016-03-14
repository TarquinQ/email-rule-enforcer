# Email-Rule-Enforcer
##Overview
Email Rule Enforcer will connect to a remote email mailbox and proceed to implement a series of rules against that mailbox.
By default, this means an IMAP4 mail server & maibox, connecting to the INBOX folder, and operating on all emails in that folder.
This aims to be a simple implementation, but one still able to handle lots of rules and handle errors gracefully.

##Approach
The fundamental idea is to connect to a mailbox, connect to an initial folder, get a list of emails in that folder, and process each email acording to rules defined in a config file.
The script is designed to be run against a mailbox perdioidcally, via cron or similar, and designed 

##Usage Notes
Please note, this script will download the full contents of each message in order to parse the subject & body - this does not use IMAP4 server-side searching, but a complete client-side regex implementation.
Each "run" is completely independent, and will not cache results locally.
Written in pure python, and designed to be usable via unix command line.

##Usage
This should take in several config files: a server config, a username & password config (authinfo), a general config and a rules config.
These files should be passed in via named command-line arguments:
--config-authinfo=./config/config-authinfo.xml
--config-serverinfo=./config/config-serverinfo.xml
--config-general=./config/config-general.xml
--config-rules=./config/config-rules.xml
An example config of each type is supplied.

##Use Case
Use cases include:
* Situations where there are no (usable) server-side rules
* Situations where a lot of different rules are required
* Situations where a lot of email is received regularly.

##Project Status
The project is currently under very-draft initial development.

##Contributions
Contributions will be accepted, although I'd like to get the initial code written & committed first.
