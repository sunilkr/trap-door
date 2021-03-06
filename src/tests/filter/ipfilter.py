from util.datatypes import * 
from util.factory import *

import unittest 

class IPFilterTest(unittest.TestCase):

    def setUp(self):
        self._filter = create_object('filter.ipfilter.IPFilter')

    def test_execute(self):
        pkt = '\x00\x90\xfb\x38\xb5\x48\xb8\xca\x3a\x83\x73\x6a\x08\x00\x45\x00\x00\x3c\xbb\x72\x40\x00\x40\x06\x35\x80\xac\x1d\x01\xce\x43\xd4\x58\x0a\x92\x6c\x00\x50\x04\x48\x49\x0a\x00\x00\x00\x00\xa0\x02\x72\x10\x49\xf8\x00\x00\x02\x04\x05\xb4\x04\x02\x08\x0a\x00\x62\xf2\x78\x00\x00\x00\x00\x01\x03\x03\x07'

        config={'src':'172.29.1.206',
                'dst':'67.212.88.10',
                'both':'true'
                }
        _filter = apply_attrs(self._filter,config)

        self.assertTrue(_filter.execute([0,pkt]))
        
        config={'src':'67.212.88.10',
                'dst':'172.29.1.206',
                'both':'True'
                }
        _filter = apply_attrs(self._filter, config)

        self.assertTrue(_filter.execute([0,pkt]))

    def test_execute_inverse(self):
        pkt = '\x00\x90\xfb\x38\xb5\x48\xb8\xca\x3a\x83\x73\x6a\x08\x00\x45\x00\x00\x3c\xbb\x72\x40\x00\x40\x06\x35\x80\xac\x1d\x01\xce\x43\xd4\x58\x0a\x92\x6c\x00\x50\x04\x48\x49\x0a\x00\x00\x00\x00\xa0\x02\x72\x10\x49\xf8\x00\x00\x02\x04\x05\xb4\x04\x02\x08\x0a\x00\x62\xf2\x78\x00\x00\x00\x00\x01\x03\x03\x07'

        config={'src':'172.29.1.206',
                'both':'true',
                'inverse':'true'
                }
        _filter = apply_attrs(self._filter,config)
        self.assertFalse(_filter.execute([0,pkt]))
        
        config={'dst':'172.29.1.206',
                'both':'True',
                'inverse':'false'
                }
        _filter = apply_attrs(self._filter, config)
        self.assertTrue(_filter.execute([0,pkt]))

        config={'dst':'172.29.1.26',
                'both':'True',
                'inverse':'true'
                }
        _filter = apply_attrs(self._filter, config)
        self.assertTrue(_filter.execute([0,pkt]))

    def test_excute_with_child(self):
        config={'name':'IPFilter.TEST',
                'class':'filter.ipfilter.IPFilter',
                'src':'198.252.206.140',
                'both':'true',
                'next':{
                    'name':'TCPFilter.HTTP',
                    'class':'filter.portfilter.TCPFilter',
                    'dport':'80',
                    'both':'true'
                    }
                }
        _filter = create_chain(config)
        pkt = '\x00\x90\xfb8\xb5H\xb8\xca:\x83sj\x08\x00E\x00\x00<\x06\xea@\x00@\x06\xf2\x17\xac\x1d\x00\x14\xc6\xfc\xce\x8c\xd9_\x00P+o\xe1{\x00\x00\x00\x00\xa0\x02r\x10A\xe9\x00\x00\x02\x04\x05\xb4\x04\x02\x08\n\x00+\xe7\x91\x00\x00\x00\x00\x01\x03\x03\x07'

        self.assertTrue(_filter.execute([0,pkt]))
    
    def test_attribs(self):
        config={'name':'IPFilter.TEST',
                'src':'127.0.0.1',
                'dst':'172.0.0.1',
                'both':'True',
                'inverse':'true'
                }

        _filter = apply_attrs(self._filter, config)
        self.assertEqual(_filter.attribs(), 
                "name:IPFilter.TEST, src:127.0.0.1, dst:172.0.0.1, both:True, inverse:True")

    def test_attrs(self):
        config={'name':'IPFilter.TEST',
                'src':'127.0.0.1',
                'dst':'172.0.0.1',
                'both':'True',
                'inverse':'true'
                }
        _filter = apply_attrs(self._filter,config)
        attrs = _filter.attrs()
        self.assertEqual(attrs['src'],'127.0.0.1')
        self.assertEqual(attrs['dst'],'172.0.0.1')
        self.assertEqual(attrs['name'],'IPFilter.TEST')
        self.assertEqual(attrs['both'].lower(), 'true')
        self.assertEqual(attrs['inverse'].lower(),'true')
        with self.assertRaises(KeyError):
            self.assertEqual(attrs['next'],'None')

    def test_setattr(self):
        setattr(self._filter,'src','127.0.0.1')
        self.assertEqual(self._filter.src, '\x7f\x00\x00\x01')


if __name__ == "__main__":
    unittest.main()
