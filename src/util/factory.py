from copy import deepcopy
from util.logging import Log, syslog

def create_object(class_name,**kwargs):
    mods = class_name.split(".")
    cls = mods[-1]
    mods = mods[0:-1]
    mod_instance = __import__(".".join(mods))
    del mods[0]
    for mod in mods:
        mod_instance = getattr(mod_instance,mod)

    class_obj = getattr(mod_instance,cls)
    return class_obj(**kwargs)

def apply_attrs(obj,config,force=False):
    for key,value in config.items():
        try:
            getattr(obj,key)
        except AttributeError:
            if force:
                setattr(obj,key,value)
            else:
                pass
        else:
            setattr(obj,key,value)

    return obj    

def create_chain(config):
    return __obj_chain(config)
    
def __obj_chain(config):
    print "creating %s" %config['class']
    obj = create_object(config['class'])
    obj = apply_attrs(obj,config)

    if config.has_key('next') and config['next'] != None:
        obj.set_next(__obj_chain(config['next']))
        
    return obj
