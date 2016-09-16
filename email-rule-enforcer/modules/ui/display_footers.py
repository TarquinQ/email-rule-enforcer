def get_completion_footer(config, global_timers, mainfolder_counters, allfolders_counters):
    ret_str = '''
*********************************************************************
**
** Rules Enforcement Completed.
**
** IMAP Server:    {0}
** IMAP Mailbox:   {1}
**
** Start Time:                {2}
** Completion Time:           {3}
** Total Elapsed Time (sec):  {4}
**
*********************************************************************
**'''.format(
        config['imap_server_name'],
        config['imap_username'],
        global_timers.get_start_datetime('overall'),
        global_timers.get_stop_datetime('overall'),
        global_timers.get_elapsed_seconds('overall')
    )

    ret_str += '''
** Process Details for Main Folder:
**
** Start Time:                {0}
** Completion Time:           {1}
** Total Elapsed Time (sec):  {2}
**
** Total Rules in Set:   {3}
** Total Folders Processed: {4}
** Total Emails Checked:    {5}
** Total Emails Matched:    {6}
** Total Rules Checked:     {7}
** Total Actions Taken:     {8}
**
*********************************************************************
**'''.format(
        global_timers.get_start_datetime('mainfolder'),
        global_timers.get_stop_datetime('mainfolder'),
        global_timers.get_elapsed_seconds('mainfolder'),
        mainfolder_counters.get('rules_in_set'),
        mainfolder_counters.get('folders_processed'),
        mainfolder_counters.get('emails_seen'),
        mainfolder_counters.get('emails_matched'),
        mainfolder_counters.get('rules_checked'),
        mainfolder_counters.get('actions_taken')
    )

    ret_str += '''
** Process Details for All Folders:
**
** Start Time:                {0}
** Completion Time:           {1}
** Total Elapsed Time (sec):  {2}
**
** Total Rules in Set:      {3}
** Total Folders Processed: {4}
** Total Emails Checked:    {5}
** Total Emails Matched:    {6}
** Total Rules Checked:     {7}
** Total Actions Taken:     {8}
**
*********************************************************************
**'''.format(
        global_timers.get_start_datetime('allfolders'),
        global_timers.get_stop_datetime('allfolders'),
        global_timers.get_elapsed_seconds('allfolders'),
        allfolders_counters.get('rules_in_set'),
        allfolders_counters.get('folders_processed'),
        allfolders_counters.get('emails_seen'),
        allfolders_counters.get('emails_matched'),
        allfolders_counters.get('rules_checked'),
        allfolders_counters.get('actions_taken')
    )

    return ret_str

