from ConfigParser import SafeConfigParser
import sys
from StringIO import StringIO

class CfgParser(object):

    #def __init__(self):
    #    self.parser = SafeConfigParser()

    def parse(self,cfg):
        self.parser = SafeConfigParser()
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

    def flatten(self, config, out):
        self.parser = SafeConfigParser()
        self.parser.add_section('trapdoor')
        for key, value in config.items():
            self._enflat(key, value, 'trapdoor')
        self.parser.write(out)
        return True

    def _enflat(self, key, value, parent):
        if isinstance(value, dict):
            if not self.parser.has_option(parent, key): #if it has, it was parent was 'list'
                self.parser.set(parent, key, value['name'])

            self.parser.add_section(value['name'])
            for k, v in value.items():
                self._enflat(k, v, value['name'])

        elif isinstance(value, list):
            for v in value:
                if isinstance(v, dict):
                    if self.parser.has_option(parent, key):
                        opt = self.parser.get(parent, key)
                        self.parser.set(parent, key, opt+v['name']+',')
                    else:
                        self.parser.set(parent, key, v['name']+',')

                    self._enflat(key, v, parent)
                else:
                    if self.parser.has_option(parent, key):
                        opt = self.parser.get(parent, key)
                        self.parser.set(parent, key, opt+v+',')
                    else:
                        self.parser.set(parent, key, v +',')
        else:
            self.parser.set(parent, key, value) 

if __name__ == "__main__":
    import pprint
    parser = CfgParser()
    config = parser.parse('config/config.cfg')
    pprint.pprint(config,indent=2)

