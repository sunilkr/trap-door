import struct

CMD_STOP                = 1
CMD_ADD                 = 2
CMD_UPDATE              = 3
CMD_DELETE              = 4
CMD_FILTER_ADD_CHAIN    = 5
CMD_LOGGER_SET_FILTER   = 6
CMD_GET_CONFIG          = 7
CMD_CLEAR               = 8

STATUS_OK           = 0

ERR_NO_SUCH_ITEM    = -1
ERR_TYPE_MISMATCH   = -2
ERR_CONFLICT        = -3
ERR_CREATE_OBJECT   = -4
ERR_APPLY_ATTRS     = -5
ERR_SEE_LOG         = -100

TCP_FLAGS = {
        'FIN':1,
        'SYN':2,
        'RST':4,
        'PSH':8,
        'ACK':16,
        'URG':32
        }

ETH_TYPES = {       
        # Ethernet payload types - http://standards.ieee.org/regauth/ethertype
        0x0200 : 'PUP',         # PUP protocol
        0x0800 : 'IP',          # IP protocol
        0x0806 : 'ARP',         # address resolution protocol
        0x2000 : 'CDP',         # Cisco Discovery Protocol
        0x2004 : 'CDTP',        # Cisco Dynamic Trunking Protocol
        0x8035 : 'RARP',        # reverse addr resolution protocol
        0x8100 : '802.1Q',      # IEEE 802.1Q VLAN tagging
        0x8137 : 'IPX',         # Internetwork Packet Exchange
        0x86DD : 'IP6',         # IPv6 protocol
        0x880B : 'PPP',         # PPP
        0x8847 : 'MPLS',        # MPLS
        0x8848 : 'MPLS_MCAST',  # MPLS Multicast
        0x8863 : 'PPPoE_DISC',  # PPP Over Ethernet Discovery Stage
        0x8864 : 'PPPoE'        # PPP Over Ethernet Session Stage
        }

IP_PROTOS = [
        # Protocol (ip_p) - http://www.iana.org/assignments/protocol-numbers
        "IP",               # dummy for IP
        "ICMP",             # ICMP
        "IGMP",             # IGMP
        "GGP",              # gateway-gateway protocol
        "IPIP",             # IP in IP
        "ST",               # ST datagram mode
        "TCP",              # TCP
        "CBT",              # CBT
        "EGP",              # exterior gateway protocol
        "IGP",              # interior gateway protocol
        "BBNRCC",           # BBN RCC monitoring
        "NVP",              # Network Voice Protocol
        "PUP",              # PARC universal packet
        "ARGUS",            # ARGUS
        "EMCON",            # EMCON
        "XNET",             # Cross Net Debugger
        "CHAOS",            # Chaos
        "UDP",              # UDP
        "MUX",              # multiplexing
        "DCNMEAS",          # DCN measurement
        "HMP",              # Host Monitoring Protocol
        "PRM",              # Packet Radio Measurement
        "IDP",              # Xerox NS IDP
        "TRUNK1",           # Trunk-1
        "TRUNK2",           # Trunk-2
        "LEAF1",            # Leaf-1
        "LEAF2",            # Leaf-2
        "RDP",              # "Reliable Datagram" proto
        "IRTP",             # Inet Reliable Transaction
        "TP",               # ISO TP class 4
        "NETBLT",           # Bulk Data Transfer
        "MFPNSP",           # MFE Network Services
        "MERITINP",         # Merit Internodal Protocol
        "SEP",              # Sequential Exchange proto
        "3PC",              # Third Party Connect proto
        "IDPR",             # Interdomain Policy Route
        "XTP",              # Xpress Transfer Protocol
        "DDP",              # Datagram Delivery Proto
        "CMTP",             # IDPR Ctrl Message Trans
        "TPPP",             # TP++ Transport Protocol
        "IL",               # IL Transport Protocol
        "IP6",              # IPv6
        "SDRP",             # Source Demand Routing
        "ROUTING",          # IPv6 routing header
        "FRAGMENT",         # IPv6 fragmentation header
        "RSVP",             # Reservation protocol
        "GRE",              # General Routing Encap
        "MHRP",             # Mobile Host Routing
        "ENA",              # ENA
        "ESP",              # Encap Security Payload
        "AH",               # Authentication Header
        "INLSP",            # Integated Net Layer Sec
        "SWIPE",            # SWIPE
        "NARP",             # NBMA Address Resolution
        "MOBILE",           # Mobile IP, RFC 2004
        "TLSP",             # Transport Layer Security
        "SKIP",             # SKIP
        "ICMP6",            # ICMP for IPv6
        "NONE",             # IPv6 no next header
        "DSTOPTS",          # IPv6 destination options
        "ANYHOST",          # any host internal proto
        "CFTP",             # CFTP
        "ANYNET",           # any local network
        "EXPAK",            # SATNET and Backroom EXPAK
        "KRYPTOLAN",        # Kryptolan
        "RVD",              # MIT Remote Virtual Disk
        "IPPC",             # Inet Pluribus Packet Core
        "DISTFS",           # any distributed fs
        "SATMON",           # SATNET Monitoring
        "VISA",             # VISA Protocol
        "IPCV",             # Inet Packet Core Utility
        "CPNX",             # Comp Proto Net Executive
        "CPHB",             # Comp Protocol Heart Beat
        "WSN",              # Wang Span Network
        "PVP",              # Packet Video Protocol
        "BRSATMON",         # Backroom SATNET Monitor
        "SUNND",            # SUN ND Protocol
        "WBMON",            # WIDEBAND Monitoring
        "WBEXPAK",          # WIDEBAND EXPAK
        "EON",              # ISO CNLP
        "VMTP",             # Versatile Msg Transport
        "SVMTP",            # Secure VMTP
        "VINES",            # VINES
        "TTP",              # TTP
        "NSFIGP",           # NSFNET-IGP
        "DGP",              # Dissimilar Gateway Proto
        "TCF",              # TCF
        "EIGRP",            # EIGRP
        "OSPF",             # Open Shortest Path First
        "SPRITERPC",        # Sprite RPC Protocol
        "LARP",             # Locus Address Resolution
        "MTP",              # Multicast Transport Proto
        "AX25",             # AX.25 Frames
        "IPIPENCAP",        # yet-another IP encap
        "MICP",             # Mobile Internet Ctrl
        "SCCSP",            # Semaphore Comm Sec Proto
        "ETHERIP",          # Ethernet in IPv4
        "ENCAP",            # encapsulation header
        "ANYENC",           # private encryption scheme
        "GMTP",             # GMTP
        "IFMP",             # Ipsilon Flow Mgmt Proto
        "PNNI",             # PNNI over IP
        "PIM",              # Protocol Indep Multicast
        "ARIS",             # ARIS
        "SCPS",             # SCPS
        "QNX",              # QNX
        "AN",               # Active Networks
        "IPCOMP",           # IP Payload Compression
        "SNP",              # Sitara Networks Protocol
        "COMPAQPEER",       # Compaq Peer Protocol
        "IPXIP",            # IPX in IP
        "VRRP",             # Virtual Router Redundancy
        "PGM",              # PGM Reliable Transport
        "ANY0HOP",          # 0-hop protocol
        "L2TP",             # Layer 2 Tunneling Proto
        "DDX",              # D-II Data Exchange (DDX)
        "IATP",             # Interactive Agent Xfer
        "STP",              # Schedule Transfer Proto
        "SRP",              # SpectraLink Radio Proto
        "UTI",              # UTI
        "SMP",              # Simple Message Protocol
        "SM",               # SM
        "PTP",              # Performance Transparency
        "ISIS",             # ISIS over IPv4
        "FIRE",             # FIRE
        "CRTP",             # Combat Radio Transport
        "CRUDP",            # Combat Radio UDP
        "SSCOPMCE",         # SSCOPMCE
        "IPLT",             # IPLT
        "SPS",              # Secure Packet Shield
        "PIPE",             # Private IP Encap in IP
        "SCTP",             # Stream Ctrl Transmission
        "FC",               # Fibre Channel
        "RSVPIGN"           # RSVP-E2E-IGNORE
        ]
def to_bool(value):
    """
        Converts 'something' to boolean. Raises exception if it gets a string it doesn't handle.
        Case is ignored for strings. These string values are handled:
        True: 'True', "1", "TRue", "yes", "y", "t"
        False: "", "0", "faLse", "no", "n", "f"
        Non-string values are passed to bool.
    """
    if type(value) == type(''):
        if value.lower() in ("yes", "y", "true",  "t", "1"):
            return True
        if value.lower() in ("no",  "n", "false", "f", "0", ""):
            return False
        raise ValueError, 'Invalid value for boolean conversion:{0}'.format(value)
    return bool(value)

def ip4_to_bytes(ip):
    if ip is not None:
        arr = [int(x) for x in ip.split(".")]
        return str(bytearray(arr))
    else:
        return None

def bytes_to_ip4(value):
    if value is not None:
        return ".".join(str(x) for x in struct.unpack("BBBB",value))    
    else:
        return None

def tcp_flags_to_value(flags):
    if flags is None or flags == 'None':
        return None

    flag = 0
    for f in flags:
        flag = flag | TCP_FLAGS[f]

    return flag

def value_to_tcp_flags(value):
    flags = []
    for f,v in TCP_FLAGS.items():
        if (value & v) != 0:
            flags.append(f)
    return flags

def bytes_to_mac(value):
    return ':'.join("{:02x}".format(x) for x in  struct.unpack("BBBBBB", value))

def mac_to_bytes(value):
    vals = [int(x,16) for x in value.split(":")]
    return struct.pack("!BBBBBB", *vals)

def l3_proto_name(code):
    try:
        return ETH_TYPES[code]
    except KeyError:
        return "INVALID"

def l4_proto_name(code):
    try:
        return IP_PROTOS[code]
    except IndexError:
        return "RESERVED"



