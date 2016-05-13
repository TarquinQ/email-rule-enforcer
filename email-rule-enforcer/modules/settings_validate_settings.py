def validate_config(config):
    """
    Validates the config files and full config-XML tree

    This ensures that the following conditions are met:
    * Mandatory values are set
    * Value-dependencies are set (eg smtp_auth = true => smtp_U&P must be also set)
    * Other conditions are required
    """

    configfail = 13378411
    def die_with_errormsg_conf(msg, configfail):
        die_with_errormsg(msg, configfail)

    def assert_value_type(setting, value, expected_type):
    if not insinstance(value, expected_type):
        die_with_errormsg_conf('Incorrect value set for config setting "' + setting + '"; Expected type: ' + expected_type + ', got value: ' + str(value))

    def assert_value_type_optional(setting, value, expected_type):
        if val is not None:
            assert_value_type(setting, value, expected_type)

    # Basic: Check Mandatory values

    # Basic General behaviour
    setting = 'empty_trash_on_exit'
    expected_type = bool
    assert_value_type(setting, config[setting], expected_type)

    setting = 'mark_as_read_on_move'
    expected_type = bool
    assert_value_type(setting, config[setting], expected_type)

    setting = 'send_notification_email_on_completion'
    expected_type = bool
    assert_value_type(setting, config[setting], expected_type)

    val = 'console_loglevel'
    expected_type = int
    assert_value_type(setting, config[setting], expected_type)

    setting = 'empty_trash_on_exit'
    expected_type = bool
    assert_value_type(setting, config[setting], expected_type)

    setting = 'send_notification_email_on_completion'
    expected_type = bool
    assert_value_type(setting, config[setting], expected_type)

    def validate_imap_server_settings(config):
        conf_prefix = 'imap'
        setting = conf_prefix + 'server_name'
        expected_type = str
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'server_port'
        expected_type = int
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'use_tls'
        expected_type = bool
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'username'
        expected_type = str
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'password'
        expected_type = str
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'initial_folder'
        expected_type = str
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'deletions_folder'
        expected_type = str
        assert_value_type(setting, config[setting], expected_type)

    def validate_smtp_server_settings(config):
        conf_prefix = 'smtp'
        setting = conf_prefix + 'server_name'
        expected_type = str
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'server_port'
        expected_type = int
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'use_tls'
        expected_type = str
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'auth_required'
        expected_type = bool
        assert_value_type(setting, config[setting], expected_type)

        if (config[conf_prefix + 'auth_required']):
            setting = conf_prefix + 'username'
            expected_type = str
            assert_value_type(setting, config[setting], expected_type)

            setting = conf_prefix + 'password'
            expected_type = str
            assert_value_type(setting, config[setting], expected_type)

    validate_imap_server_settings(config)
    validate_smtp_server_settings(config)

