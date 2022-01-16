import os
from logic.mudgee_parser import Parser
import logic.constants as constants
from collections import defaultdict
from muddy.models import Protocol


class MudComparer(object):
    def __init__(self, first_mud, second_mud):
        # muds and comparision object
        self.first_mud = first_mud
        self.second_mud = second_mud
        self.two_directional_comparison = None

        # identical rules list
        self.final_identical_dt = []

        # from and to related aces
        self.first_from_related_aces = {}
        self.second_from_related_aces = {}
        self.first_to_related_aces = {}
        self.second_to_related_aces = {}

        # non empty from and to related aces - similar rules
        self.similar_first_from_related_aces = {}
        self.similar_first_to_related_aces = {}
        self.similar_second_from_related_aces = {}
        self.similar_second_to_related_aces = {}

        # divide similar rules into two categories: 1. domain similarity 2. all other similarities
        self.domain_based_similar_first_from_related_aces = defaultdict(list)
        self.not_domain_based_similar_first_from_related_aces = defaultdict(list)
        self.domain_based_similar_first_to_related_aces = defaultdict(list)
        self.not_domain_based_similar_first_to_related_aces = defaultdict(list)

        # empty from and to related aces - non similar rules
        self.non_similar_first_from_aces = []
        self.non_similar_first_to_aces = []
        self.non_similar_second_from_aces = []
        self.non_similar_second_to_aces = []

        # metrics variables
        self.M1 = 0
        self.R1 = 0
        self.M2 = 0
        self.R2 = 0
        self.L = 0

    def clean_mud_out_of_noise(self, clear_dns, clear_icmp, clear_ntp, clear_inner_ip, clear_p2p=None):
        elements_to_remove = []

        dns_port = 0
        ntp_port = 0
        protocol_icmp = ""

        if clear_dns:
            dns_port = 53
        if clear_ntp:
            ntp_port = 123
        if clear_icmp:
            protocol_icmp = "ICMP"

        for ace in self.first_mud.from_access_list.aces:
            port = ace.get_ace_port()
            protocol = ace.get_ip_version_and_protocol()[1]
            identifier = ace.get_ace_identifier()
            if port == dns_port or port == ntp_port or protocol == protocol_icmp:
                elements_to_remove.append(ace)
            elif clear_p2p and port:
                for port_range in clear_p2p:
                    start = port_range[0]
                    end = port_range[1]
                    protocol_match = port_range[2]
                    if start <= port <= end and protocol == protocol_match:
                        elements_to_remove.append(ace)
            elif clear_inner_ip and identifier and "192.168" in identifier:
                elements_to_remove.append(ace)


        self.first_mud.from_access_list.aces = [x for x in self.first_mud.from_access_list.aces if x not in elements_to_remove]
        elements_to_remove.clear()

        for ace in self.first_mud.to_access_list.aces:
            port = ace.get_ace_port()
            protocol = ace.get_ip_version_and_protocol()[1]
            identifier = ace.get_ace_identifier()
            if port == dns_port or port == ntp_port or protocol == protocol_icmp:
                elements_to_remove.append(ace)
            elif clear_p2p and port:
                for port_range in clear_p2p:
                    start = port_range[0]
                    end = port_range[1]
                    protocol_match = port_range[2]
                    if start <= port <= end and protocol == protocol_match:
                        elements_to_remove.append(ace)
            elif clear_inner_ip and identifier and "192.168" in identifier:
                elements_to_remove.append(ace)

        self.first_mud.to_access_list.aces = [x for x in self.first_mud.to_access_list.aces if x not in elements_to_remove]
        elements_to_remove.clear()

        for ace in self.second_mud.from_access_list.aces:
            port = ace.get_ace_port()
            protocol = ace.get_ip_version_and_protocol()[1]
            identifier = ace.get_ace_identifier()
            if port == dns_port or port == ntp_port or protocol == protocol_icmp:
                elements_to_remove.append(ace)
            elif clear_p2p and port:
                for port_range in clear_p2p:
                    start = port_range[0]
                    end = port_range[1]
                    protocol_match = port_range[2]
                    if start <= port <= end and protocol == protocol_match:
                        elements_to_remove.append(ace)
            elif clear_inner_ip and identifier and "192.168" in identifier:
                elements_to_remove.append(ace)

        self.second_mud.from_access_list.aces = [x for x in self.second_mud.from_access_list.aces if x not in elements_to_remove]
        elements_to_remove.clear()

        for ace in self.second_mud.to_access_list.aces:
            port = ace.get_ace_port()
            protocol = ace.get_ip_version_and_protocol()[1]
            identifier = ace.get_ace_identifier()
            if port == dns_port or port == ntp_port or protocol == protocol_icmp:
                elements_to_remove.append(ace)
            elif clear_p2p and port:
                for port_range in clear_p2p:
                    start = port_range[0]
                    end = port_range[1]
                    protocol_match = port_range[2]
                    if start <= port <= end and protocol == protocol_match:
                        elements_to_remove.append(ace)
            elif clear_inner_ip and identifier and "192.168" in identifier:
                elements_to_remove.append(ace)

        self.second_mud.to_access_list.aces = [x for x in self.second_mud.to_access_list.aces if x not in elements_to_remove]
        elements_to_remove.clear()

    def compare_muds(self):
        # two directional comparision
        first_direction_identical_dt, first_direction_different_dt = self.first_mud.compare_muds(self.second_mud)
        second_direction_identical_dt, second_direction_different_dt = self.second_mud.compare_muds(self.first_mud)


        # handling "ietf-mud:mud" rules and filtering them out so the will not harm the metrice calculation
        elements_to_remove = []

        for ace in first_direction_different_dt:
            if ace.matches[0].match_type == "ietf-mud:mud":
                elements_to_remove.append(ace)

        first_direction_different_dt = [x for x in first_direction_different_dt if x not in elements_to_remove]
        elements_to_remove.clear()

        for ace in second_direction_different_dt:
            if ace.matches[0].match_type == "ietf-mud:mud":
                elements_to_remove.append(ace)

        second_direction_different_dt = [x for x in second_direction_different_dt if x not in elements_to_remove]
        elements_to_remove.clear()


        # TODO: use this as the identical rules
        self.final_identical_dt = self.get_final_identical_dt(first_direction_identical_dt, second_direction_identical_dt)

        # parametric initialization
        self.M1 = len(first_direction_different_dt)
        self.R1 = self.first_mud.get_total_rules_count()
        self.M2 = len(second_direction_different_dt)
        self.R2 = self.second_mud.get_total_rules_count()

        self.two_directional_comparison = (first_direction_different_dt, second_direction_different_dt)
        self.find_related_aces(first_direction_different_dt, second_direction_different_dt)

        self.find_rules_with_similarity()
        self.divide_similarity_rules()
        self.find_rules_with_no_similarity()

        self.L = self.calculate_l_value()

    # get generalized identical rules
    def get_final_identical_dt(self, first_direction_identical_dt, second_direction_identical_dt):
        final_identical_dt = []
        assert len(first_direction_identical_dt) == len(second_direction_identical_dt), "identical lists are not in the same length"

        for i in range(len(first_direction_identical_dt)):
            first_ace = first_direction_identical_dt[i]
            second_ace = second_direction_identical_dt[i]

            # assume that ipv4 match is always the first one in the list (like the network stack)
            if first_ace.matches[0].is_domain_generalized:
                final_identical_dt.append(first_ace)
            else:
                final_identical_dt.append(second_ace)

        return final_identical_dt


    def find_related_aces(self, first_direction_dt, second_direction_dt):
        # from and to access lists
        first_from_aces = []
        second_from_aces = []
        first_to_aces = []
        second_to_aces = []

        for ace in first_direction_dt:
            if ace.rule_type == 'from':
                first_from_aces.append(ace)
            else:
                first_to_aces.append(ace)

        for ace in second_direction_dt:
            if ace.rule_type == 'from':
                second_from_aces.append(ace)
            else:
                second_to_aces.append(ace)

        # find all from related aces (do it in a bidirectional way)
        for first_acl_ace in first_from_aces:
            self.first_from_related_aces[first_acl_ace] = []
            for second_acl_ace in second_from_aces:
                if second_acl_ace not in self.second_from_related_aces:
                    self.second_from_related_aces[second_acl_ace] = []
                similarity_vector = first_acl_ace.similarity(second_acl_ace)
                similarity_vector.determine_vector_similarity_status()
                #if self.ace_similarity_logic(similarity_vector):
                if similarity_vector.is_vector_similar:
                    print(similarity_vector)
                    self.first_from_related_aces[first_acl_ace].append((second_acl_ace, similarity_vector))
                    self.second_from_related_aces[second_acl_ace].append((first_acl_ace, similarity_vector))

        # find all to related aces (do it in a bidirectional way)
        for first_acl_ace in first_to_aces:
            self.first_to_related_aces[first_acl_ace] = []
            for second_acl_ace in second_to_aces:
                if second_acl_ace not in self.second_to_related_aces:
                    self.second_to_related_aces[second_acl_ace] = []
                similarity_vector = first_acl_ace.similarity(second_acl_ace)
                similarity_vector.determine_vector_similarity_status()
                #if self.ace_similarity_logic(similarity_vector):
                if similarity_vector.is_vector_similar:
                    print(similarity_vector)
                    self.first_to_related_aces[first_acl_ace].append((second_acl_ace, similarity_vector))
                    self.second_to_related_aces[second_acl_ace].append((first_acl_ace, similarity_vector))

    def ace_similarity_logic(self, similarity_vector):
        for sim in similarity_vector:
            if True in sim[1]:
                return True
        return False

    # creates the nodes and edges representation
    def create_relations_graph(self):
        nodes = []
        edges = []

        for base_rule in self.similar_second_from_related_aces:
            relation_components = self.similar_second_from_related_aces[base_rule]
            from_nodes, from_edges = self.create_graph_element(base_rule, relation_components, 'from')

            nodes = self.concat_graph_elements(nodes, from_nodes)
            edges = self.concat_graph_elements(edges, from_edges)

        # TODO: check if i want to only present the from rules
        '''
        for base_rule in self.non_empty_first_to_related_aces:
            relation_rules = self.non_empty_first_to_related_aces[base_rule]
            to_nodes, to_edges = self.create_graph_element(base_rule, relation_rules, 'to')
        
            nodes = self.concat_graph_elements(nodes, to_nodes)
            edges = self.concat_graph_elements(edges, to_edges)
        '''
        return nodes, edges

    def concat_graph_elements(self, first_list, second_list):
        for element in second_list:
            if element not in first_list:
                first_list.append(element)
            else:
                print("WOW")

        return first_list

    def create_graph_element(self, base_rule, relation_components, direction):
        nodes = []
        edges = []

        # TODO: change the color by the different mud
        if direction == 'from':
            #color = "#FFCFCF"
            color = "#FFFFFF"
        else:
            #color = "#90ee90"
            color = "#FFFFFF"

        size = 150
        node_font = {"face": "monospace", "align": "left", "size": 24}
        shape = "box"
        physics = "false"
        smooth = {"type": "cubicBezier"}
        label_text = base_rule.get_ace_lable_text()
        generalized_domain = base_rule.get_generalized_domain()
        print(label_text)

        base_node = {
                        "id": base_rule.name,
                        "size": size,
                        "label": label_text,
                        "shape": shape,
                        "font": node_font,
                        "color": color

                    }

        #if "dc-eu01-euwest1" in label_text:
        #    nodes.append(base_node)

        nodes.append(base_node)

        for relation_component in relation_components:
            import uuid
            relation_rule, similarity_vector = relation_component # separate the rule and its similarity vector
            label_text = relation_rule.get_ace_lable_text()
            relation_node = {
                                "id": relation_rule.name,
                                "size": size,
                                "label": label_text,
                                #"color": "#90ee90",
                                "color": "#FFFFFF",
                                "shape": shape,
                                "font": node_font,
                            }

            #if "dc-na04-useast2" in label_text:
            #    nodes.append(relation_node)
            nodes.append(relation_node)


            new_node = {
                                "id": "new_node"+str(uuid.uuid1()),
                                "size": size,
                                "label": label_text.replace("api.eu", "*"),
                                #"color": "#90ee90",
                                "color": "#FFFFFF",
                                "shape": shape,
                                "font": node_font,
                            }

            nodes.append(new_node)


            edge_font = {"face": "monospace", "size": 24}
            edge = {
                        "from": base_rule.name,
                        "to": relation_rule.name,
                        "physics": physics,
                        "label": similarity_vector.primary_similarity_type,
                        #"label": "DOMAIN_BASED_SIMILARITY",
                        "arrows": "to;from",
                        "smooth": smooth,
                        "font": edge_font
                    }

            edge_new1 = {
                        "from": base_rule.name,
                        "to": "new_node",
                        "physics": physics,
                        #"label": similarity_vector.primary_similarity_type,
                        "label": "DOMAIN_BASED_SIMILARITY",
                        "arrows": "to;from",
                        "smooth": smooth,
                        "font": edge_font
                    }

            edge_new2 = {
                        "from": relation_rule.name,
                        "to": "new_node",
                        "physics": physics,
                        #"label": similarity_vector.primary_similarity_type,
                        "label": "DOMAIN_BASED_SIMILARITY",
                        "arrows": "to;from",
                        "smooth": smooth,
                        "font": edge_font
                    }



            #if edge["from"] == "from-ipv4-smartthings_hub_merged_uk-11" and edge["to"] == "from-ipv4-smartthings_hub_merged_us-10":
            #    edges.append(edge)
                #edges.append(edge_new1)
                #edges.append(edge_new2)
            #edges.append(edge)


            '''
            if not similarity_vector.primary_similarity_type == "PORT_PROTOCOL_BASED_SIMILARITY":
                edges.append(edge)


        #base_lable_text = f"Rule direction = from \n\nRule details: \n\t\t Protocol = TCP, Doamin = api.xiaoyi.com.tw \n\t\t Source port = *, Destination Port = 443 \n"
        base_lable_text = f"Rule direction = from \n\nRule details: \n\t\t Protocol = TCP, Doamin = aps1-api.tplinkra.com \n\t\t Source port = *, Destination Port = 443 \n"
        #base_lable_text = f"Rule direction = from \n\nRule details: \n\t\t Protocol = UDP, IP = 147.161.9.36/32 \n\t\t Source port = *, Destination Port = 32320 \n"

        base_node = {
                        "id": "base",
                        "size": size,
                        "label": base_lable_text,
                        "shape": shape,
                        "font": node_font,
                        "color": color

                    }

        #re_lable_text = f"Rule direction = from \n\nRule details: \n\t\t Protocol = TCP, Doamin = api.eu.xiaoyi.com \n\t\t Source port = *, Destination Port = 443 \n"
        re_lable_text = f"Rule direction = from \n\nRule details: \n\t\t Protocol = TCP, Doamin = use1-api.tplinkra.com \n\t\t Source port = *, Destination Port = 443 \n"
        #re_lable_text = f"Rule direction = from \n\nRule details: \n\t\t Protocol = UDP, IP = 147.161.9.60/32 \n\t\t Source port = *, Destination Port = 3863 \n"

        relation_node = {
            "id": "relation",
            "size": size,
            "label": re_lable_text,
            "color": color,
            "shape": shape,
            "font": node_font,
        }

        edge = {
            "from": "base",
            "to": "relation",
            "physics": physics,
            "arrows": "to;from",
            "smooth": smooth,
            "font": edge_font
        }

        nodes = [base_node,relation_node]
        edges = [edge]
        '''

        return nodes, edges

    def find_rules_with_no_similarity(self):
        self.non_similar_first_from_aces = [k for k, v in self.first_from_related_aces.items() if not v]
        self.non_similar_first_to_aces = [k for k, v in self.first_to_related_aces.items() if not v]
        self.non_similar_second_from_aces = [k for k, v in self.second_from_related_aces.items() if not v]
        self.non_similar_second_to_aces = [k for k, v in self.second_to_related_aces.items() if not v]

    def find_rules_with_similarity(self):
        self.similar_first_from_related_aces = {k:v for k, v in self.first_from_related_aces.items() if v}
        self.similar_first_to_related_aces = {k:v for k, v in self.first_to_related_aces.items() if v}
        self.similar_second_from_related_aces = {k:v for k, v in self.second_from_related_aces.items() if v}
        self.similar_second_to_related_aces = {k:v for k, v in self.second_to_related_aces.items() if v}

    '''
    def divide_similarity_rules(self):
        for k, v in self.similar_first_from_related_aces.items():
            for ace in v:
                similarity_vector = ace[1]
                if similarity_vector.primary_similarity_type == constants.DOMAIN_BASED_SIMILARITY:
                    self.domain_based_similar_first_from_related_aces[k].append(ace)
                else:
                    self.not_domain_based_similar_first_from_related_aces[k].append(ace)

        for k, v in self.similar_first_to_related_aces.items():
            for ace in v:
                similarity_vector = ace[1]
                if similarity_vector.primary_similarity_type == constants.DOMAIN_BASED_SIMILARITY:
                    self.domain_based_similar_first_to_related_aces[k].append(ace)
                else:
                    self.not_domain_based_similar_first_to_related_aces[k].append(ace)
    '''

    def divide_similarity_rules(self):
        for k, v in self.similar_first_from_related_aces.items():
            for ace in v:
                similarity_vector = ace[1]
                # add port based similarity to check if the domain and port are similar and not only the domain
                if similarity_vector.primary_similarity_type == constants.DOMAIN_BASED_SIMILARITY \
                        and constants.PORT_PROTOCOL_BASED_SIMILARITY in similarity_vector.get_all_vector_similarity_types():
                    self.domain_based_similar_first_from_related_aces[k].append(ace)
                else:
                    self.not_domain_based_similar_first_from_related_aces[k].append(ace)

        for k, v in self.similar_first_to_related_aces.items():
            for ace in v:
                similarity_vector = ace[1]
                # add port based similarity to check if the domain and port are similar and not only the domain
                if similarity_vector.primary_similarity_type == constants.DOMAIN_BASED_SIMILARITY \
                        and constants.PORT_PROTOCOL_BASED_SIMILARITY in similarity_vector.get_all_vector_similarity_types():
                    self.domain_based_similar_first_to_related_aces[k].append(ace)
                else:
                    self.not_domain_based_similar_first_to_related_aces[k].append(ace)


        '''
        for k, v in self.similar_first_to_related_aces.items():
            similarity_vector = v[0][1]
            if similarity_vector.primary_similarity_type == constants.DOMAIN_BASED_SIMILARITY:
                self.domain_based_similar_first_to_related_aces[k] = v
            else:
                self.not_domain_based_similar_first_to_related_aces[k] = v
        '''

    def prepare_similarity_rules_for_presentation(self, similarity_rules):
        final_similarity_rules = []
        for k, v in similarity_rules[0].items():
            for related_rule in v:
                # this can duplicate k when there is more then one similarity
                final_similarity_rules.append((k, related_rule[0]))
            #final_similarity_rules.append((k, v[0]))

        for k, v in similarity_rules[1].items():
            for related_rule in v:
                # this can duplicate k when there is more then one similarity
                final_similarity_rules.append((k, related_rule[0]))
            #final_similarity_rules.append((k, v[0]))

        return final_similarity_rules

    def prepare_non_similarity_rules_for_presentation(self, non_similarity_rules):
        final_non_similarity_rules = []
        first_mud_non_similar_rules = non_similarity_rules[0]
        second_mud_non_similar_rules = non_similarity_rules[1]
        max_len = max(len(first_mud_non_similar_rules), len(second_mud_non_similar_rules))
        min_len = min(len(first_mud_non_similar_rules), len(second_mud_non_similar_rules))

        for i in range(max_len):
            if i < min_len:
                final_non_similarity_rules.append((first_mud_non_similar_rules[i], second_mud_non_similar_rules[i]))
            elif i >= len(first_mud_non_similar_rules):
                final_non_similarity_rules.append((None, second_mud_non_similar_rules[i]))
            else:
                final_non_similarity_rules.append((first_mud_non_similar_rules[i], None))

        return final_non_similarity_rules

    # the logic of choosing and calculating the L value
    def calculate_l_value(self):
        first_mud_related_rules = len(self.similar_first_from_related_aces) + len(self.similar_first_to_related_aces)
        second_mud_related_rules = len(self.similar_second_from_related_aces) + len(self.similar_second_to_related_aces)

        return min(first_mud_related_rules, second_mud_related_rules)

    def odd_rules_out_of_total_rules(self):
        return 1 - (self.M1 + self.M2) / (self.R1 + self.R2)

    def odd_rules_without_similar_rules_out_of_total_rules(self):
        return 1 - (self.M1 + self.M2 - (2 * self.L)) / (self.R1 + self.R2)

    def generalization_rating(self):
        try:
            return 1 - (self.M1 + self.M2 - (2 * self.L)) / (self.M1 + self.M2)
        except ZeroDivisionError:
            return 0
