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
        self.sync_new.timer.set_default_incr(config['daemon_monitor_inbox_delay'])
        self.sync_full.timer.set_default_incr(config['full_scan_delay'])
        if config['full_scan_align_to_timing'] is True:
            self.sync_full.set_deadline_base(config['full_scan_align_to_timing_base'])

        # Start the Timers
        self.keepalive.reset_timer_default()
        self.sync_new.reset_timer_default()
        self.sync_full.reset_timer_default()
