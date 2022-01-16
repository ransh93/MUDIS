
# GENERAL
UPLOAD_FOLDER = r'/code/uploads/'
ALLOWED_EXTENSIONS = {'json'}
SIMILARITY_VALUE = 0.5
CLOUD_BROKERS = ["", ""]

# SIMILARITY TYPES
DOMAIN_BASED_SIMILARITY = "DOMAIN_BASED_SIMILARITY"
IP_BASED_SIMILARITY = "IP_BASED_SIMILARITY"
PORT_PROTOCOL_BASED_SIMILARITY = "PORT_PROTOCOL_BASED_SIMILARITY"
ICMP_BASED_SIMILARITY = "ICMP_BASED_SIMILARITY"
IDENTICAL_BASED_SIMILARITY = "IDENTICAL_BASED_SIMILARITY"
NON_SIMILARITY_BASED = "NON_SIMILARITY_BASED"

# METADATA
METADATA_KEY = "ietf-mud:mud"
ACTIONS_KEY = "actions"
ACTIONS_RULE_KEY = "forwarding"

# ACL
ACL_ALL_KEY = "ietf-access-control-list:access-lists"
ACL_KEY = "acl"
ACL_NAME_KEY = "name"
ACL_TYPE_KEY = "type"
ACL_ACES_KEY = "aces"
ACL_ACES_ACE_KEY = "ace"

# IPV4
IPV4_PROTOCOL_KEY = "protocol"
IPV4_FROM_DNS_NAME_KEY = "ietf-acldns:dst-dnsname"
IPV4_TO_DNS_NAME_KEY = "ietf-acldns:src-dnsname"
IPV4_DESTINATION_IP_KEY = "destination-ipv4-network"
IPV4_SOURCE_IP_KEY = "source-ipv4-network"

# UDP
UDP_DESTINATION_PORT_KEY = "destination-port"
UDP_SOURCE_PORT_KEY = "source-port"
UDP_OPERATOR_KEY = "operator"
UDP_PORT_KEY = "port"

# TCP
TCP_DESTINATION_PORT_KEY = "destination-port"
TCP_SOURCE_PORT_KEY = "source-port"
TCP_OPERATOR_KEY = "operator"
TCP_PORT_KEY = "port"
TCP_DIRECTION_INITIATED_KEY = "ietf-mud:direction-initiated"

# ICMP
ICMP_TYPE = "type"
ICMP_CODE = "code"

# Muds coordinator table
DATA_TO_COLUMNS = ['_id', 'mud_name', 'device_type', 'device_name', 'dev_location', 'mud_file_path']
