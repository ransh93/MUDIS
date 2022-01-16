import logic.constants as constants
import jellyfish
from muddy.models import Direction, IPVersion, Protocol, MatchType
from logic.similarity import *
import copy

class AccessList():
    def __init__(self, name, list_type, rule_type):
        self.name = name
        self.list_type = list_type
        self.rule_type = rule_type
        self.aces = []

    def parse(self, aces_data):
        for ace_elem in aces_data:
            ace = Ace(self.rule_type)
            ace.parse(ace_elem)
            self.aces.append(ace)

    def compare(self, second_access_list):
        # will be a tuple of the different aces
        different_dt = []
        identical_dt = []

        for first_mud_ace in self.aces:
            is_different = True

            for second_mud_ace in second_access_list.aces:
                is_eq = first_mud_ace.compare(second_mud_ace)
                if is_eq:
                    is_different = False
                    break

            if is_different:
                different_dt.append(first_mud_ace)
            elif not first_mud_ace.is_inner:
                identical_dt.append(first_mud_ace)

        return identical_dt, different_dt


class Ace(object):
    def __init__(self, rule_type):
        self.rule_type = rule_type
        self.name = None
        self.matches = []  # list of matches
        self.actions = None
        self.is_inner = False # TODO: think what i do with it

    def parse(self, ace_elem):
        self.name = ace_elem["name"]
        self.actions = ace_elem[constants.ACTIONS_KEY][constants.ACTIONS_RULE_KEY]

        # should be static
        matches_obj = ace_elem["matches"]
        for match_item in matches_obj.items():
            match = Match(self.rule_type, match_item[0], match_item[1])
            self.matches.append(match)

    def compare(self, second_mud_ace):
        is_eq = True
        # relay on the same order inside a match
        for first_match in self.matches:
            # TODO: address it
            if first_match.match_type == "ietf-mud:mud":
                self.is_inner = False
                #return True

            for second_match in second_mud_ace.matches:
                if first_match.match_type == second_match.match_type:
                    if first_match != second_match:
                        is_eq = False
                        return is_eq

        return is_eq

    def similarity(self, second_mud_ace):
        #similarity_vector = []
        sim_vector = SimilarityVector()
        for first_match in self.matches:
            for second_match in second_mud_ace.matches:
                if first_match.match_type == second_match.match_type:
                    #break  # cant to similarity similarity
                    #sim_element = first_match.similarity(second_match)
                    #similarity_vector.append((first_match.match_type, sim_element))

                    sim_component = first_match.similarity(second_match)
                    sim_vector.add_component(sim_component)

        #return similarity_vector
        return sim_vector

    def get_ace_lable_text(self):
        lable_text = f"Rule direction = {self.rule_type} \n\nRule details: \n"
        for match in self.matches:
            lable_text += str(match.get_match_lable_text())

        return lable_text

    def get_generalized_domain(self):
        generalized_domain = None
        for match in self.matches:
            if match.generalized_domain is not None:
                generalized_domain = match.generalized_domain

        return generalized_domain

    def get_ip_version_and_protocol(self):
        ip_version = None
        protocol = None

        for match in self.matches:
            if match.match_type == "ipv4":
                ip_version = IPVersion.IPV4

            if match.match_type == "tcp":
                protocol = Protocol.TCP

            if match.match_type == "udp":
                protocol = Protocol.UDP

            if match.match_type == "icmp":
                protocol = "ICMP"

        return ip_version, protocol
        # TODO: what do i do in case of ICMP, seems muddy dose not support it


    def get_ace_identifier(self):
        identifier = self.matches[0].get_match_identifier()
        return identifier

    def get_ace_port(self):
        if self.matches[1].match_type == "tcp" or self.matches[1].match_type == "udp":
            port = self.matches[1].port
        else:
            port = None

        return port

    def set_dns_to_generalized_domain(self, generalized_domain):
        for match in self.matches:
            if match.is_contains_domain():
                match.is_domain_generalized = True
                match.generalized_domain = generalized_domain
                match.dns_name = generalized_domain

    def print_ace(self):
        print(f"name = {self.name}, rule type = {self.rule_type}")
        print("Matches:")
        for match in self.matches:
            match.print_match()





'''
class Matchs():
    def __init__(self):
        self.matches = []

    def parse(self, rule_type, matches):
        for match_item in matches.items():
            match = Match(rule_type, match_item[0], match_item[1])
            self.matches.append(match)
'''

class Match():
    def __init__(self, rule_type, match_type, match_value):
        self.match_type = match_type
        self.rule_type = rule_type
        self.is_domain_generalized = False
        self.generalized_domain = None # will be initialized only if we find a matched domain that be generalized

        if match_type == "tcp":
            if rule_type == "from":
                is_dp = 0
                try:
                    dp = match_value[constants.TCP_DESTINATION_PORT_KEY]
                    self.operator = dp[constants.TCP_OPERATOR_KEY]
                    self.port = dp[constants.TCP_PORT_KEY]
                    is_dp = 1
                except:
                    sp = match_value[constants.TCP_SOURCE_PORT_KEY]
                    self.operator = sp[constants.TCP_OPERATOR_KEY]
                    self.port = sp[constants.TCP_PORT_KEY]
                    is_dp = 1

                # added this in order to solve cases where direction_initiated is not there
                if is_dp == 1:
                    try:
                        self.direction_initiated = match_value[constants.TCP_DIRECTION_INITIATED_KEY]
                    except:
                        self.direction_initiated = "from-device"

                is_dp = 0

            elif rule_type == "to":
                try:
                    sp = match_value[constants.TCP_SOURCE_PORT_KEY]
                    self.operator = sp[constants.TCP_OPERATOR_KEY]
                    self.port = sp[constants.TCP_PORT_KEY]
                except:
                    dp = match_value[constants.TCP_DESTINATION_PORT_KEY]
                    self.operator = dp[constants.TCP_OPERATOR_KEY]
                    self.port = dp[constants.TCP_PORT_KEY]


        # TODO: think what i do with the situation that in from o have source and vice versa
        # TODO: happens in us_yi or uk_yi
        if match_type == "udp":
            if rule_type == "from":
                # under destination_port
                try:
                    dp = match_value[constants.UDP_DESTINATION_PORT_KEY]
                    self.operator = dp[constants.UDP_OPERATOR_KEY]
                    self.port = dp[constants.UDP_PORT_KEY]
                except:
                    sp = match_value[constants.UDP_SOURCE_PORT_KEY]
                    self.operator = sp[constants.UDP_OPERATOR_KEY]
                    self.port = sp[constants.UDP_PORT_KEY]

            elif rule_type == "to":
                try:
                    sp = match_value[constants.UDP_SOURCE_PORT_KEY]
                    self.operator = sp[constants.UDP_OPERATOR_KEY]
                    self.port = sp[constants.UDP_PORT_KEY]
                except:
                    dp = match_value[constants.UDP_DESTINATION_PORT_KEY]
                    self.operator = dp[constants.UDP_OPERATOR_KEY]
                    self.port = dp[constants.UDP_PORT_KEY]


        if match_type == "ipv4":
            self.protocol = match_value[constants.IPV4_PROTOCOL_KEY]

            if rule_type == "from":
                if constants.IPV4_FROM_DNS_NAME_KEY in match_value:
                    self.dns_name = match_value[constants.IPV4_FROM_DNS_NAME_KEY].lower()
                    if '*' in self.dns_name:
                        self.is_domain_generalized = True  # checkes if the given domain is generalized (when there is a domain)
                elif constants.IPV4_DESTINATION_IP_KEY in match_value:
                    self.ipv4_network = match_value[constants.IPV4_DESTINATION_IP_KEY]

            elif rule_type == "to":
                if constants.IPV4_TO_DNS_NAME_KEY in match_value:
                    self.dns_name = match_value[constants.IPV4_TO_DNS_NAME_KEY].lower()
                    if '*' in self.dns_name:
                        self.is_domain_generalized = True  # checkes if the given domain is generalized (when there is a domain)
                elif constants.IPV4_SOURCE_IP_KEY in match_value:
                    self.ipv4_network = match_value[constants.IPV4_SOURCE_IP_KEY]

        if match_type == "icmp":
            self.icmp_type = match_value[constants.ICMP_TYPE]
            self.icmp_code = match_value[constants.ICMP_CODE]

    def similarity(self, other):
        if self.match_type == "tcp":
            if self.rule_type == "from":
                if self.operator == other.operator and self.port == other.port and self.direction_initiated == other.direction_initiated:
                    return SimilarityComponent(self.match_type, True, 1, constants.PORT_PROTOCOL_BASED_SIMILARITY)
                    #return True, 1
                else:
                    return SimilarityComponent(self.match_type, False, 0, constants.PORT_PROTOCOL_BASED_SIMILARITY)
                    #return False, 0

            elif self.rule_type == "to":
                if self.operator == other.operator and self.port == other.port:
                    return SimilarityComponent(self.match_type, True, 1, constants.PORT_PROTOCOL_BASED_SIMILARITY)
                    #return True, 1
                else:
                    return SimilarityComponent(self.match_type, False, 0, constants.PORT_PROTOCOL_BASED_SIMILARITY)
                    #return False, 0

        if self.match_type == "udp":
            if self.operator == other.operator and self.port == other.port:
                return SimilarityComponent(self.match_type, True, 1, constants.PORT_PROTOCOL_BASED_SIMILARITY)
                #return True, 1
            else:
                return SimilarityComponent(self.match_type, False, 0, constants.PORT_PROTOCOL_BASED_SIMILARITY)
                #return False, 0

        if self.match_type == "ipv4":
            if hasattr(self, 'dns_name') and hasattr(other, 'dns_name'):
                # sim_value = self.jaro_similarity(self.dns_name, other.dns_name)
                sim_value = self.domain_similarity(self.dns_name, other.dns_name)
                if self.protocol == other.protocol and sim_value >= constants.SIMILARITY_VALUE:
                    return SimilarityComponent(self.match_type, True, sim_value, constants.DOMAIN_BASED_SIMILARITY)
                    #return True, sim_value, self.generalized_domain
                else:
                    return SimilarityComponent(self.match_type, False, sim_value, constants.DOMAIN_BASED_SIMILARITY)
                    #return False, sim_value, self.generalized_domain
            elif hasattr(self, 'ipv4_network') and hasattr(other, 'ipv4_network'):
                if self.protocol == other.protocol and self.ipv4_network == other.ipv4_network:
                    return SimilarityComponent(self.match_type, True, 1, constants.IP_BASED_SIMILARITY)
                    #return True, 1
                else:
                    return SimilarityComponent(self.match_type, False, 0, constants.IP_BASED_SIMILARITY)
                    #return False, -1  # TODO: need a good metric for ips
            else:
                return SimilarityComponent(self.match_type, False, -1, "NOT IMPLEMENTED")
                #return False, -1  # in case there is a domain in one and an ip in the other

        if self.match_type == "icmp":
            if self.icmp_type == other.icmp_type and self.icmp_code == other.icmp_code:
                return SimilarityComponent(self.match_type, True, 1, constants.ICMP_BASED_SIMILARITY)
                #return True, 1
            else:
                return SimilarityComponent(self.match_type, False, 0, constants.ICMP_BASED_SIMILARITY)
                #return False, 0

        # TODO: can add more logic here
        if self.match_type == "ietf-mud:mud":
            return SimilarityComponent(self.match_type, True, 1, "ietf-mud:mud")
            #return True, 1
        else:
            return SimilarityComponent(self.match_type, False, -1, "NOT IMPLEMENTED")


    def is_contains_domain(self):
        if self.match_type == "ipv4":
            if hasattr(self, 'dns_name'):
                return True

    # if we got here it means that both domains are not equal so the similarity score can never be 1 only close to it
    def domain_similarity(self, a, b):
        lower_a = a.lower()
        lower_b = b.lower()

        a_domain_parts_rev = lower_a.split('.')[::-1]
        b_domain_parts_rev = lower_b.split('.')[::-1]
        similarity_max_score = min(len(a_domain_parts_rev), len(b_domain_parts_rev))
        similarity_score = 0
        local_generalized_domain = ""

        if self.generalized_domain is None:
            self.generalized_domain = ""

        for i in range(similarity_max_score):
            if a_domain_parts_rev[i] == "amazon-adsystem" and b_domain_parts_rev[i] == "amazon-adsystem":
                print("here")
            if a_domain_parts_rev[i] == b_domain_parts_rev[i] and a_domain_parts_rev[i] not in constants.CLOUD_BROKERS:
                similarity_score += 1
                local_generalized_domain = '.' + a_domain_parts_rev[i] + local_generalized_domain
            else:
                break

        local_generalized_domain = '*' + local_generalized_domain

        if len(local_generalized_domain.split('.')) > len(self.generalized_domain.split('.')) and len(local_generalized_domain.split('.')) > 2:
            self.generalized_domain = str(local_generalized_domain)

        #self.generalized_domain = '*' + self.generalized_domain
        return similarity_score / similarity_max_score

    def get_match_identifier(self):
        if hasattr(self, 'dns_name'):
            return self.dns_name
        elif hasattr(self, 'ipv4_network'):
            return self.ipv4_network
        else:
            return None

    def jaro_similarity(self, a, b):
        return jellyfish.jaro_similarity(a, b)

    def convert_protocol_identification(self, protocol_id):
        if protocol_id == 6:
            return "TCP"
        elif protocol_id == 17:
            return "UDP"

    def get_match_lable_text(self):
        if self.match_type == "tcp":
            if self.rule_type == "from":
                return (f"\t\t Source port = *, Destination Port = {self.port} \n")

            elif self.rule_type == "to":
                return(f"\t\t Source port = {self.port}, Destination Port = * \n")

        if self.match_type == "udp":
            if self.rule_type == "from":
                return(f"\t\t Source port = *, Destination Port = {self.port} \n")
            elif self.rule_type == "to":
                return (f"\t\t Source port = {self.port}, Destination Port = * \n")


        if self.match_type == "ipv4":
            if hasattr(self, 'dns_name'):
                self.dns_name = self.dns_name.lower()
                return(f"\t\t Protocol = {self.convert_protocol_identification(self.protocol)}, Doamin = {self.dns_name} \n")
            elif hasattr(self, 'ipv4_network'):
                return(f"\t\t Protocol = {self.convert_protocol_identification(self.protocol)}, IP = {self.ipv4_network} \n")

        if self.match_type == "icmp":
            return(f"\t\t Icmp type = {self.icmp_type}, Icmp code = {self.icmp_code} \n")


    def print_match(self):
        if self.match_type == "tcp":
            if self.rule_type == "from":
                print(f"\t\t operator = {self.operator}, port = {self.port}, direction initiated = {self.direction_initiated}")

            elif self.rule_type == "to":
                print(f"\t\t operator = {self.operator}, port = {self.port}")

        if self.match_type == "udp":
            print(f"\t\t operator = {self.operator}, port = {self.port}")

        if self.match_type == "ipv4":
            if hasattr(self, 'dns_name'):
                print(f"\t\t protocol = {self.protocol}, dns name = {self.dns_name}")
            elif hasattr(self, 'ipv4_network'):
                print(f"\t\t protocol = {self.protocol}, ipv4 network = {self.ipv4_network}")

        if self.match_type == "icmp":
            print(f"\t\t icmp type = {self.icmp_type}, icmp code = {self.icmp_code}")

    def __str__(self):
        if self.match_type == "tcp":
            if self.rule_type == "from":
                return (f"\t\t operator = {self.operator}, port = {self.port}, direction initiated = {self.direction_initiated}")

            elif self.rule_type == "to":
                return (f"\t\t operator = {self.operator}, port = {self.port}")

        if self.match_type == "udp":
            return (f"\t\t operator = {self.operator}, port = {self.port}")


        if self.match_type == "ipv4":
            if hasattr(self, 'dns_name'):
                return (f"\t\t protocol = {self.protocol}, dns name = {self.dns_name}")
            elif hasattr(self, 'ipv4_network'):
                return (f"\t\t protocol = {self.protocol}, ipv4 network = {self.ipv4_network}")

    def __eq__(self, other):
        if not isinstance(other, Match):
            # don't attempt to compare against unrelated types
            return NotImplemented

        if self.match_type == "tcp":
            if self.rule_type == "from":
                return self.operator == other.operator and self.port == other.port and self.direction_initiated == other.direction_initiated

            elif self.rule_type == "to":
                return self.operator == other.operator and self.port == other.port

        if self.match_type == "udp":
            return self.operator == other.operator and self.port == other.port

        if self.match_type == "ipv4":
            if hasattr(self, 'dns_name') and hasattr(other, 'dns_name'):
                #return self.protocol == other.protocol and self.dns_name == other.dns_name
                return self.protocol == other.protocol and self.extended_domain_identicality(self.dns_name, other.dns_name)
            elif hasattr(self, 'ipv4_network') and hasattr(other, 'ipv4_network'):
                return self.protocol == other.protocol and self.ipv4_network == other.ipv4_network
            elif not hasattr(self, 'ipv4_network') and not hasattr(other, 'ipv4_network') and not hasattr(self, 'dns_name') and not hasattr(other, 'dns_name'):
                print("There is no IP or Domain in that match, consider as the same match")
                return self.protocol == other.protocol

        if self.match_type == "icmp":
            return self.icmp_type == other.icmp_type and self.icmp_code == other.icmp_code

        # TODO: can add more logic here
        if self.match_type == "ietf-mud:mud":
            return True
        if self.match_type == "eth":
            return True

    # find if two domain are identical while considering regex wise equality *.domain.com
    def extended_domain_identicality(self, domain_a, domain_b):
        if '*' not in domain_a and '*' not in domain_b:
            return domain_a == domain_b
        elif '*' in domain_a:
            tld = domain_a.split('*.')[-1]
            return domain_b.endswith(tld)
        else:
            tld = domain_b.split('*.')[-1]
            return domain_a.endswith(tld)
