# Email-Rule-Enforcer
##Overview
Email Rule Enforcer will connect to a remote email mailbox and proceed to implement a series of rules against emails in that mailbox.  
By default, this means an IMAP mail server & maibox, connecting to the INBOX folder, and operating on all emails in that folder.  
This aims to be a simple implementation, but albeit able to handle a lot of rules.  

##Approach
The fundamental idea is to connect to a mailbox, connect to an initial folder, get a list of emails in that folder, and process each email 
acording to rules defined in a config file.  
The script is designed to be run against a mailbox perdioidcally, via cron or similar, and designed to follow a set of specificed rules.

##Usage Notes
In order to reduce bandwidth, this software will only download the headers of each message, unless a "body" serach appears in the ruleset.  
This software oes not use IMAP4 server-side searching, instead using a complete client-side regex implementation. This is good, since it has maximum flexibility, but maybe bad if you have a large mailbox and slow connection.  
Each "run" is completely independent, and does not cache results locally.  
Written in pure python (ie core libraries only, no pip requirements), and designed to be usable via unix command line.  

## System Requirements
Requires Python 3.4 -- written in python3, and uses SSL extensions added in v3.4. This minumum version requirement is enforced at runtime.  
Written in pure python (cpython corelib), with no external or package dependencies.  
This is written and tested on a Linux system, however it should be fully portable to all other systems that can run Python.  

##Usage
This should take in one or more xml-based config files: a server-connection config, a username & password config (authinfo), a rules config and a general config.  
Each of these files should be passed in via command-line arguments, eg:  
-c ./config/config-authinfo.xml  
-c ./config/config-serverinfo.xml  
-c ./config/config-rules.xml  
-c ./config/config-general.xml  
A sample config of each type is supplied; each config option is annotated with purpose, acceptable values and default options.  
A single unified config file may be supplied. Conversely, a single file for each section may be used.  
Additionally, multiple Rules config files may be specified (regardless of whether there is a unified all-other-config file supplied).  

##Use Cases
Use cases include:
* Situations where there are no (usable) server-side rule implementations
* Situations where a lot of different rules are required (ie exceeds server-side capacity)
* Situations where editing of server-side rules is difficult (eg Shared Mailboxes in Exchange/Office 365)
* Situations where a large amount of email is received regularly and needs to be dealt with
* Situations where extended logging of rules is needed

##Project Status
The project is almost usable.  
More testing is required, but it can currently parse configs and rules, connect to an IMAP server, get all emails in a folder, match emails and perform actions (and produce a lot of logs!).  
There is still a decent amount of change underway and more yet to come, but progress is quite steady and not far from completion.
### Working:
* Read in config files
* Connect to IMAP Server
* Match emails to Rules
* Perform Actions
* Produce logs to Console, main & debug logfiles

### Remainder of Project Implementation
* More Logging
* More Testing
Currently tested against Office 365 and Gmail, and it should work against any standard IMAPv4 server implementation 
(since it uses Python's native IMAP Libraries).

##Contributions
Contributions will be accepted, although I'd like to get the initial code written & committed first.

