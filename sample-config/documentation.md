# Email-Rule-Enforcer Configuration Documentation

Email-Rule-Enforcer is a software application designed to process Rules against an IMAP mailbox. This is the documentation for the configuration files for this software.  

## Overview of Config file layout
Configuration files are stored in XML format, and can be located anywhere on the local filesystem.  
There may be a single configuration file, or a configuration broken into multiple files.  
Generally, each section will be put into a single file, as laid out in the "sample-config" directory.  
Rule files are special: there can be many Rules files, and they will all be read and processed.  
Each file is explained in sections below.  

## Usage
All config files should be passed in as one or more xml-based config files: a server-connection config, a username & password config (authinfo), a rules config and a general config.  
Each of these files should be passed in via command-line arguments, eg:  
```no-highlight
python3 email-rule-enforcer.py  -c ./config/config-authinfo.xml -c ./config/config-serverinfo.xml  \  
-c ./config/config-rules.xml  -c ./config/config-general.xml
```
A single unified config file may be supplied. Conversely, a single file for each section may be used.  
A sample config of each type is supplied. The sample configs are annotated with acceptable values and default options.  
Ordering of individual sections on the command line is not important (eg authinfo and servinfo can be given in any order), however if multiple xml files contain the same section (with the exception of "config_rules") only the first-passed section will apply.
Rules are speical: multiple Rules config files may be specified (regardless of whether there is a unified all-other-config file supplied).  

## Usage Examples
The following examples are valid examples of command-line exection:
```no-highlight
python3 email-rule-enforcer.py  -c ./config/config-authinfo.xml  \  
-c ./config/config-serverinfo.xml  -c ./config/config-rules.xml  \  
-c ./config/config-general.xml
```
```no-highlight
python3 -c ~/email-parse-config/config-unified.xml
```
```no-highlight
python3 email-rule-enforcer.py  -c ./config/config-authinfo.xml -c ./config/config-serverinfo.xml -c ./config/config-general.xml  \  
-c ./config/config-rules-block-senders.xml  \  
-c ./config/config-rules-match-recipients.xml  \  
-c ./config/config-rules-all-folders.xml  \  
-c ./config/config-rules-delete-everything-ahahaha.xml
```
```no-highlight
python3 -c ~/email-parse-config/config-unified.xml -c ./config/config-extra-rules.xml
```
In the following example, the second "authinfo-2" file is ignored:
```no-highlight
python3 email-rule-enforcer.py  -c ./config/config-authinfo-1.xml  \  
-c ./config/config-serverinfo.xml  -c ./config/config-rules.xml  \  
-c ./config/config-authinfo-2.xml  -c ./config/config-general.xml
```

## Configuration XML Overview
All configuation is structured as an xml as per the following structure:  
```xml
<?xml version="1.0" encoding="UTF-8"?>
<emailenforcer>
	<config_general>
		<!-- Options here -->
	</config_general>
	<config_serverinfo>
		<!-- Options here -->
	</config_serverinfo>
	<config_authinfo>
		<!-- Options here -->
	</config_authinfo>
	<config_rules>
		<!-- Options here -->
	</config_rules>
</emailenforcer>
```
The above structure may be supplied as a single config file, or may be split into multiple config files with each major section split into an individual file (as provided in the sample_config). Each split file should still have a root node of <emailenforcer>.  
There may be multiple config_rules sections.  
Each major section has all options detailed below.  
All config files must be well-formatted valid XML files - if they are not, the software will safely fail without performng any actions.  

### Config Sample
A sample config shows the following:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<emailenforcer>
	<config_general>
		<mailhandling_behaviour>
			<sample_path modifier="something">my_value</mark_as_read_on_move>
		</mailhandling_behaviour>
	</config_general>
</emailenforcer>
```
In this example:
* Each XML node name is represented a path (eg "emailenforcer/config_general/mailhandling_bahaviour/sample_path")
* Modifiers (optional) appear against the node such as "<sample_path modifier="something">"
* Values are the text in between the <>s, as shown by "my_value"
For the purposes of all documentation, the initial path name of <emailenforcer> will be ignored, so the above example path would be referred to as "config_general/mailhandling_bahaviour/sample_path"

## Major Section: General

The general section contains settings to control general program behaviour.

| XML Node Name | Modifiers | ValueType | Default Value | Optional? | Notes |
| ------------- | --------- | --------- | ------------- | --------- | ----- |
|mailhandling_behaviour/|-|(node)|(node)|Yes| |
|mailhandling_behaviour/empty_trash_on_exit|-|Boolean|False|Yes| |
|mailhandling_behaviour/mark_as_read_on_move|-|Boolean|True|Yes| |
|notification_email_on_completion/|-|(node)|(node)|Yes| |
|notification_email_on_completion/recipient_email|-|Text|-|Yes|Can have multiple recipient_emails, one address per config line|
|notification_email_on_completion/subject|-|Text|-|Yes| |
|notification_email_on_completion/body_prefix|-|Text|-|Yes| |
|notification_email_on_completion/attach_log|-|Boolean|Yes|Yes| |
|logging/|-|(node)|(node)|Yes|Log Levels run from 1-5, verbose-quiet: these correspond to DEBUG, INFO, WARNING, ERROR, CRITICAL|
|logging/console_level|-|Integer|2|Yes|Console Log Level|
|logging/console_ultra_debug|-|Text|off|Yes|Pours out a large amount of debug info to the console|
|logging/console_insane_debug|-|Text|off|Yes|Pours out an enourmous amount of debug info to the console|
|logging/test_config_parse_only|-|Boolean|False|Program will parse all config and then ceases prior to IMAP|
|logfile/|-|(node)|(node)|Yes|Controls standard Logfile output|
|logfile/log_folder|-|Text|-|Yes| |Trailing slash can be omitted|
|logfile/log_filename|-|Text|-|Yes| |First bit of log filename|
|logfile/append_date_to_filename|-|Boolean|Yes|Yes| |ISO format, including current time|
|logfile/filename_extension>|-|Text|.log|Yes| |
|logfile/continue_on_log_fail|-|Boolean|No|Yes| |Continue even if log file is not writeable|
|logfile/logfile_level|-|Integer|2|Yes| |1-5 verbose-quiet|
|logfile_debug/|-|(node)|(node)|Yes|Controls debug Logfile output|
|logfile_debug/log_folder|-|Text|-|Yes| |Trailing slash can be omitted|
|logfile_debug/log_filename|-|Text|-|Yes| |First bit of log filename|
|logfile_debug/append_date_to_filename|-|Boolean|Yes|Yes| |ISO format, including current time|
|logfile_debug/filename_extension>|-|Text|.log|Yes| |
|logfile_debug/continue_on_log_fail|-|Boolean|No|Yes| |Continue even if log file is not writeable|
|logfile_debug/logfile_level|-|Integer|2|Yes| |1-5, verbose-quiet|
  

## Major Section: ServerInfo

The general section contains settings to control general program behaviour.

| XML Node Name | Modifiers | ValueType | Default Value | Optional? | Notes |
| ------------- | --------- | --------- | ------------- | --------- | ----- |
  

## Major Section: AuthInfo

The general section contains settings to control general program behaviour.

| XML Node Name | Modifiers | ValueType | Default Value | Optional? | Notes |
| ------------- | --------- | --------- | ------------- | --------- | ----- |
  

## Major Section: Rules
NB All config values here apply to all Rules files

The general section contains settings to control general program behaviour.

| XML Node Name | Modifiers | ValueType | Default Value | Optional? | Notes |
| ------------- | --------- | --------- | ------------- | --------- | ----- |
  

