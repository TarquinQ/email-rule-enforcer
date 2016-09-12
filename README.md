# Email-Rule-Enforcer
##Overview
Email Rule Enforcer will connect to a remote email mailbox and proceed to implement a series of rules against emails in that mailbox.  
By default, this means an IMAP mail server & maibox, connecting to the INBOX folder, and operating on all emails in that folder.  
This aims to be a simple implementation, whilst still able to handle a lot of rules.  

##Approach
The fundamental idea is to connect to a mailbox, connect to an initial folder, get a list of emails in that folder, and process each email 
acording to rules defined in a config file. There are two sets of rules: one set which applies to a main folder (usually Inbox), and another set which applies to all folders.  
The script is designed to be run against a mailbox perdioidcally, via cron or similar, and designed to follow the sets of specificed rules.

##Usage Notes
This software does not use IMAP4 server-side searching, instead using a complete client-side regex implementation. This is has maximum flexibility, but may not be suitable if you have a large mailbox and/or slow connection. Each "run" is completely independent, and does not cache results locally.  
In order to improve speed and reduce bandwidth, this software will only download the headers of each message, unless a "body" field search appears in the ruleset. Also, efforts have been made to reduce the number of IMAP commands issued during message retrival, which should also assist to reduce bandwidth (and time).   

## System Requirements
Requires Python 3.4 -- written in python3, and uses SSL and other extensions added in v3.4. Version requirement is enforced at runtime.  
The core is written in pure python (ie core libraries only, no external or package requirements), and designed to be usable via unix command line.  
If the 'colorlog' python pip package is installed & accessible, then the console output becomes coloured -- however this is completely optional.  
This is written and tested on a Linux system, however it should be fully portable to all other systems that can run Python (including Windows).  

##Usage
This should take in one or more xml-based config files: a server-connection config, a username & password config (authinfo), a rules config and a general config.  
Each of these files should be passed in via command-line arguments, eg:  
-c ./config/config-authinfo.xml  
-c ./config/config-serverinfo.xml  
-c ./config/config-rules.xml  
-c ./config/config-general.xml  
A sample config of each type is supplied; each config option is annotated with purpose, values and default options.  
Alternately, a unified config file may be supplied, to simply all config into a single file.
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
* Match emails in Main (Inbox) folder to Rules; Perform Actions as required
* Match emails in All Folder to secondary Rules; Perform Actions as required
* Produce logs to Console, main & debug logfiles

### Remainder of Project Implementation
* Improved Logging
* More Testing
* More Documentation
Currently tested against Office 365 and Gmail. It should also work against any standard IMAPv4 server implementation (since it uses Python's native IMAP Libraries).

##Contributions
Contributions will be accepted, although I'd like to get the initial code written & committed first.

