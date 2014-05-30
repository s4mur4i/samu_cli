import ConfigParser
import io

from error import SAMUError

class Config(object):

    def __init__(self):
        self.config_file = None
        self.parser = ConfigParser.RawConfigParser()

    def __section_from_dotted(self, section):
        s = section.split('.', 1)
        if len(s) == 2:
            return '%s "%s"' % tuple(s)
        else:
            return section

    def __section_to_dotted(self, section):
        s = section.split('"')
        if len(s) == 3:
            return '%s.%s' % (s[0][:-1], s[1])
        else:
            return section

    def open(self, cfgfile):
        self.config_file = cfgfile
        self.parser.read(self.config_file)

    def write(self):
        if self.config_file is None:
            raise SAMUError("Unable to save config file because file name is unset")
        file_ = open(self.config_file, 'wt')
        self.parser.write(file_)
        file_.close()

    def close(self):
        pass

    def has(self, section, option):
        section = self.__section_from_dotted(section)
        return self.parser.has_option(section, option)

    def set(self, section, option, value):
        section = self.__section_from_dotted(section)
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        self.parser.set(section, option, value)

    def get(self, section, option):
        section = self.__section_from_dotted(section)
        if not self.parser.has_section(section):
            return None
        try:
            return self.parser.get(section, option)
        except ConfigParser.NoOptionError:
            return None

    def get_or_default_value(self, section, option, default_value):
        res = self.get(section, option)
        return res if res is not None else default_value

    def remove(self, section, option):
        section = self.__section_from_dotted(section)
        if not self.parser.has_section(section):
            return
        if not self.parser.has_option(section, option):
            return
        self.parser.remove_option(section, option)

    def get_options(self, section):
        section = self.__section_from_dotted(section)
        if not self.parser.has_section(section):
            return []
        else:
            return self.parser.options(section)

    def get_sections(self):
        return [self.__section_to_dotted(s) for s in self.parser.sections()]

class SystemConfig(Config):

    def __init__(self):
        super(SystemConfig, self).__init__()
        self.config_file_fallback = os.path.expanduser('~/.samu.config')
        self.config_file_default = Dirs.get_full_path('etc/samu.config')

    def open(self, cfgfile=None):
        if not cfgfile:
            # fallback is useful because mostly there is no need for multiple configuration,
            # but there is a chance, in this case the default file is used wich is per-zwa, not per-user...
            if os.path.exists(self.config_file_fallback) and not os.path.exists(self.config_file_default):
                cfgfile = self.config_file_fallback
            else:
                cfgfile = self.config_file_default

        super(SystemConfig, self).open(cfgfile)
