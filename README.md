# Email-Rule-Enforcer
##Overview
Email Rule Enforcer will connect to a remote email mailbox and proceed to implement a series of rules against that mailbox.
By default, this means an IMAP4 mail server & maibox, connecting to the INBOX folder, and operating on all emails in that folder.
This aims to be a simple implementation, but one still able to handle a lot of rules, and handle errors gracefully.

##Approach
The fundamental idea is to connect to a mailbox, connect to an initial folder, get a list of emails in that folder, and process each email acording to rules defined in a config file.
The script is designed to be run against a mailbox perdioidcally, via cron or similar, and designed to follow a set of specificed rules.

##Usage Notes
Please note, this script will download the full contents of each message in order to parse the subject & body - this does not use IMAP4 server-side searching, but a complete client-side regex implementation. This is good, since it has maximum flexibility, and bad if you have a large mailbox and slow connection. Each "run" is completely independent, and does not cache results locally.
Written in pure python, and designed to be usable via unix command line.

##Usage
This should take in one or more xml-based config files: a server config, a username & password config (authinfo), a general config and a rules config.
Each of these files should be passed in via named command-line arguments:
-c ./config/config-authinfo.xml
-c ./config/config-serverinfo.xml
-c ./config/config-general.xml
-c ./config/config-rules.xml
A sample config of each type is supplied, annotated with default options.

##Use Case
Use cases include:
* Situations where there are no (usable) server-side rules
* Situations where a lot of different rules are required
* Situations where a lot of email is received regularly and needs to be dealt with

##Project Status
The project is currently under very-draft initial development.
Not only does it not curently work, there is a very large amount of change underway & yet to come.

##Contributions
Contributions will be accepted, although I'd like to get the initial code written & committed first.
