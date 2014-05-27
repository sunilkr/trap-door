from ConfigParser import SafeConfigParser
import sys

class CfgParser(object):

    def __init__(self):
        self.parser = SafeConfigParser()

    def parse(self,cfg):
        config = {'trapdoor':{}}
        trapcfg = config['trapdoor']
        self.parser.read(cfg)
        trap = 'trapdoor'
        sections = self.parser.sections()
        if trap not in sections:
            raise AttributeError, "'{0}' section is missing in {1}".format(trap,str(sections))

        trapcfg['iface'] = self.parser.get(trap,'iface').split(",")
        trapcfg['filters'] = self.parser.get(trap,'filters').split(",")
        trapcfg['loggers'] = self.parser.get(trap,'loggers').split(",")

        for index, section in enumerate(trapcfg['filters']):
            trapcfg['filters'][index] =  self._section_to_dict(section)

        for index, section in enumerate(trapcfg['loggers']):
            trapcfg['loggers'][index] = self._section_to_dict(section)

        return config

    def _section_to_dict(self,section):
        config = {}
        options = self.parser.options(section)
        sections = self.parser.sections()

        for option in options:
            value = self.parser.get(section,option)
            if value in sections:
                value = self._section_to_dict(value)
            config[option] = value
        
        return config

if __name__ == "__main__":
    import pprint
    parser = CfgParser()
    config = parser.parse('config/config.cfg')
    pprint.pprint(config,indent=2)

