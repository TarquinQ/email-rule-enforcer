from modules.models.GlobalCounters import GlobalCounters
from modules.models.GlobalTimeRecorders import GlobalTimeRecorders


def create_default_rule_counters():
    ret_counters = GlobalCounters()
    ret_counters.new_counter('folders_processed')
    ret_counters.new_counter('emails_seen')
    ret_counters.new_counter('emails_matched')
    ret_counters.new_counter('rules_in_set')
    ret_counters.new_counter('rules_checked')
    ret_counters.new_counter('actions_taken')
    return ret_counters


def create_default_timers():
    ret_timers = GlobalTimeRecorders()
    ret_timers.new_counter('overall', start=True)
    ret_timers.new_counter('mainfolder', start=False)
    ret_timers.new_counter('allfolders', start=False)
    return ret_timers


# 2. Rule counts: Keep a count of the following items:
# * Count Each Raw Email Seen - Main Rules
# * Count Each Raw Email Seen - AllFolders Rule
# * Count Each Email Matched (only once per email)
# * Count Total Rules Processed/Checked
# * Count Hitcount per-Rule
# * Count Actions Taken (main rules)
# * Count Actions Taken (AllFolders)
# * Start Time - Global
# * End Time - Global
# * Start Time MainRules + timedelta
# * End Time MainRules + timedelta
# * Start Time AllFolderRules + timedelta
# * End Time AllFolderRules + timedelta

# config.globalstate.counters()
# GlobalState():
#    Counters():
#    Timers():
