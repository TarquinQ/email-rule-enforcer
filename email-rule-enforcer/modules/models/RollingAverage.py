class RollingAverage():
    def add(self, val):
        try:
            self.avg
        except AttributeError:
            self.avg = val
            self.sample_count = 0
        prev_count = self.sample_count
        self.sample_count += 1
        self.avg = (self.avg * prev_count + val) / self.sample_count
        return self.avg

    def get_avg(self):
        return self.avg

    def get_count(self):
        return self.sample_count

