class Config(dict):
    def clone_nopasswd(self):
        new_copy = self.copy()
        new_copy['imap_password'] = '**Password Hidden**'
        new_copy['smtp_password'] = '**Password Hidden**'
        new_copy['imap_folders_to_exclude'] = '**Folder List Here**'
        return new_copy

