def get_completion_footer(global_timers, mainfolder_counters, allfolders_counters):
    ret_str = '''
*********************************************************************
**
** Rules Enforcement Completed.
**
** Start Time:                    {0}
** Completion Time:               {1}
** Total Elapsed Time (seconds):  {2}
**
*********************************************************************
**'''.format(
        global_timers.get_start_datetime('overall'),
        global_timers.get_stop_datetime('overall'),
        global_timers.get_elapsed_seconds('overall')
    )

    ret_str += '''
** Process Details for Main Folder:
**
** Start Time:                    {0}
** Completion Time:               {1}
** Total Elapsed Time (seconds):  {2}
**
** Total Emails Seen:    {3}
** Total Emails Matched: {4}
** Total Rules Checked:  {5}
** Total Actions Taken:  {6}
**
*********************************************************************
**'''.format(
        global_timers.get_start_datetime('mainfolder'),
        global_timers.get_stop_datetime('mainfolder'),
        global_timers.get_elapsed_seconds('mainfolder'),
        mainfolder_counters.get('emails_seen'),
        mainfolder_counters.get('emails_matched'),
        mainfolder_counters.get('rules_checked'),
        mainfolder_counters.get('actions_taken')
    )

    ret_str += '''
** Process Details for All Folders:
**
** Start Time:                    {0}
** Completion Time:               {1}
** Total Elapsed Time (seconds):  {2}
**
** Total Emails Seen:    {3}
** Total Emails Matched: {4}
** Total Rules Checked:  {5}
** Total Actions Taken:  {6}
**
*********************************************************************
**'''.format(
        global_timers.get_start_datetime('allfolders'),
        global_timers.get_stop_datetime('allfolders'),
        global_timers.get_elapsed_seconds('allfolders'),
        allfolders_counters.get('emails_seen'),
        allfolders_counters.get('emails_matched'),
        allfolders_counters.get('rules_checked'),
        allfolders_counters.get('actions_taken')
    )

    return ret_str

