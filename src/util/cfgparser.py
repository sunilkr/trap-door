from ConfigParser import SafeConfigParser
import sys

class CfgParser(object):

    def __init__(self):
        self.parser = SafeConfigParser()

    def parse(self,cfg):
        self.parser.read(cfg)
        sections = self.parser.sections()
        self.config = {sections[0] : self._section_to_dict(sections[0])}
        return self.config

    def _section_to_dict(self,section):
        config = {}
        options = self.parser.options(section)
        sections = self.parser.sections()

        for option in options:
            value = self.parser.get(section,option)
            parsed = []
            if ',' in value:
                values = self._split_(value,',')
                for value in values:
                    if value in sections:
                        value = self._section_to_dict(value)
                    parsed.append(value)
            elif value in sections:
                parsed = self._section_to_dict(value)
            else:
                parsed = value

            config[option] = parsed
        
        return config

    def _split_(self, value, sep):
        values = value.split(sep)
        res = []
        for value in values:
            if len(value) != 0:
                res.append(value)
        return res
    
    def pprint(self):
        self._print_(self.config, 0)
    
    def _print_(self,config, lvl):
        pref = "  "*lvl
        print pref+"{"
        for k, v in config.items(): 
            if isinstance(v, dict):
                print pref +"  "+ k +"\t:"
                self._print_(v, lvl+2)
            elif isinstance(v, list):
                print pref +"  "+ k +"\t: ["
                for i in v:
                    if isinstance(i, dict):
                        self._print_(i, lvl+2)
                    else:
                        print pref + "      {0}".format(i)
                print pref + "  ]"
            else:
                print pref +"  {0}\t: {1}".format(k, v)
        print pref + "}"

if __name__ == "__main__":
    import pprint
    parser = CfgParser()
    config = parser.parse('config/config.cfg')
    pprint.pprint(config,indent=2)

