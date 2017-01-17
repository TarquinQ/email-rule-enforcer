import datetime
from modules.models.TimerFlag import TimerFlag


class GlobalTimerFlags():
    def __init__(self):
        self.keepalive = TimerFlag(name="KeepAlive")
        self.sync_full = TimerFlag(name="SyncFull")
        self.sync_new = TimerFlag(name="SyncNewFromInbox")

    def wait_for_next_deadline(self):
        """This blocks until the next available action gets called"""
        self.get_Timer_with_next_deadline.join()

    def get_name_of_Timer_with_next_deadline(self):
        return self.get_Timer_with_next_deadline().name

    def get_Timer_with_next_deadline(self):
        soonest_timer = self.keepalive
        if self.sync_full.next_deadline < soonest_timer.next_deadline:
            soonest_timer = self.sync_full
        if self.sync_new.next_deadline < soonest_timer.next_deadline:
            soonest_timer = self.sync_new
        return soonest_timer

    def set_from_config(self, config):
        # Set Default increments
        self.keepalive.timer.set_default_incr(config['daemon_keepalive'])
        self.sync_full.timer.set_default_incr(config['full_scan_delay'])
        self.sync_new.timer.set_default_incr(config['daemon_monitor_inbox_delay'])

        # Start the keepalive timer
        self.keepalive.reset_timer_default()

        # Start the Monitor Inbox timer
        self.sync_new.reset_timer_default()

        # Calculate the next non-startup timer for sync_full
        if config['full_scan_align_to_timing'] is False:
            self.sync_full.reset_timer_default()
        else:
            # This is what we are aiming to get to: a scan will occur at this time (and any periodics beforehand)
            time_base = config['full_scan_align_to_timing_base']
            period = config['full_scan_delay']
            now = datetime.datetime.now()
            target_hours, target_mins = (int(i) for i in config['full_scan_align_to_timing_base'].split(':'))  # This value is pre-validated to match "[00-23]:[00-59]"
            compare_hours = now.hour
            compare_mins = now.minute
            # convert to seconds, and make sure that we account for the 00:00 > 23:00 conundrum....
            if target_hours < compare_hours:
                target_hours += 24
            target_s = ((60 * target_hours) + target_mins) * 60
            compare_s = ((60 * compare_hours) + compare_mins) * 60
            # Now we just work out when the next run should be, in order to hit the timing_base
            while compare_s < target_s:
                target_s = target_s - period
            next_deadline_hours = ((target_s//60)//60)
            next_deadline_mins = ((target_s//60) % 60)
            if next_deadline_hours > 23:
                next_deadline_hours = next_deadline_hours - 24
                next_deadline_days = 1
            else:
                next_deadline_days = 0
            next_deadline = now + datetime.timedelta(days=next_deadline_days)
            next_deadline.replace(hour=next_deadline_hours, minute=next_deadline_mins)
            # And new we set the timer to go off at that time
            self.sync_full.reset_timer_datetime(next_deadline)
