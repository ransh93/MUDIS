import copy
import logic.constants as constants
from logic.mud_generator import MudGenerator

class GeneralizedRuleHistory(object):
    def __init__(self, rule_creation_type, source_rules):
        self.rule_creation_type = rule_creation_type
        self.source_rules = source_rules

class MudGeneralization(object):
    def __init__(self, identical_rules, first_non_similar_from_rules, first_non_similar_to_rules,
                 second_non_similar_from_rules, second_non_similar_to_rules, generalized_from_rules, generalized_to_rules,
                 first_mud_name, first_mud_location, second_mud_name, second_mud_location, device_type, device_name, mongo_dal):
        self.identical_from_rules = []
        self.identical_to_rules = []
        self.non_similar_from_rules = []
        self.non_similar_to_rules = []
        self.generalized_from_rules = []
        self.generalized_to_rules = []
        self.from_rules = []
        self.to_rules = []

        # identical rules from/to separation
        for identical_rule in identical_rules:
            rule_hist = GeneralizedRuleHistory(constants.IDENTICAL_BASED_SIMILARITY, None)
            if identical_rule.rule_type == "from":
                self.identical_from_rules.append((identical_rule, rule_hist))
            else:
                self.identical_to_rules.append((identical_rule, rule_hist))

        # create combined non similar from and to rules
        rule_hist = GeneralizedRuleHistory(constants.NON_SIMILARITY_BASED, None)
        first_non_similar_from_rules_with_hist = [(rule, rule_hist) for rule in first_non_similar_from_rules]
        second_non_similar_from_rules_with_hist = [(rule, rule_hist) for rule in second_non_similar_from_rules]
        first_non_similar_to_rules_with_hist = [(rule, rule_hist) for rule in first_non_similar_to_rules]
        second_non_similar_to_rules_with_hist = [(rule, rule_hist) for rule in second_non_similar_to_rules]

        self.non_similar_from_rules = first_non_similar_from_rules_with_hist + second_non_similar_from_rules_with_hist
        self.non_similar_to_rules = first_non_similar_to_rules_with_hist + second_non_similar_to_rules_with_hist

        #self.non_similar_from_rules = first_non_similar_from_rules + second_non_similar_from_rules
        #self.non_similar_to_rules = first_non_similar_to_rules + second_non_similar_to_rules

        # create generalized similar from and to rules
        self.create_generalized_rules(generalized_from_rules, "from")
        self.create_generalized_rules(generalized_to_rules, "to")

        # this code came to solve the problem where we add identical rules with no consideration of the generalized rules.
        # when we are adding and identical rule we check that it does not fall inside a generalized rules
        # if it falls inside we wont add it and if not we will add it because its a new rule
        for identical_rule in self.identical_from_rules:
            is_exists = False
            for gen_rule in self.generalized_from_rules:
                if gen_rule[0].compare(identical_rule[0]):
                    is_exists = True
            if not is_exists:
                self.from_rules.append(identical_rule)

        for identical_rule in self.identical_to_rules:
            is_exists = False
            for gen_rule in self.generalized_to_rules:
                if gen_rule[0].compare(identical_rule[0]):
                    is_exists = True
            if not is_exists:
                self.to_rules.append(identical_rule)

        self.from_rules += self.non_similar_from_rules + self.generalized_from_rules
        self.to_rules += self.non_similar_to_rules + self.generalized_to_rules

        #self.from_rules = self.identical_from_rules + self.non_similar_from_rules + self.generalized_from_rules
        #self.to_rules = self.identical_to_rules + self.non_similar_to_rules + self.generalized_to_rules

        # TODO: address the url and system info parameters to put the real ones
        generalized_title_name = "{}_and_{}_generalization".format(first_mud_name, second_mud_name)
        mud_generator = MudGenerator(1, 'https://example.com', 48, True, generalized_title_name)
        generalized_mud_name = "{}_and_{}_generalization.json".format(first_mud_name, second_mud_name)
        #mud_generator.generate_mud(self.from_rules, self.to_rules, mongo_dal, generalized_mud_name,
        #                           generalized_title_name, first_mud_location, second_mud_location,
        #                           device_name, device_type)

    def create_generalized_rules(self, rules_to_generalize, direction):
        for base_rule,relations_rules in rules_to_generalize.items():
            domain_based_similarity_existence = self.check_domain_based_similarity_existence(relations_rules)
            for relations_rule in relations_rules:
                rule = relations_rule[0]
                similarity_vector = relations_rule[1]
                if similarity_vector.primary_similarity_type == constants.PORT_PROTOCOL_BASED_SIMILARITY and domain_based_similarity_existence:
                    rule_hist = GeneralizedRuleHistory(constants.PORT_PROTOCOL_BASED_SIMILARITY, (base_rule, rule))
                    self.add_generalized_rule((rule, rule_hist), direction)  # added only the rule and not the similarity vector
                elif similarity_vector.primary_similarity_type == constants.PORT_PROTOCOL_BASED_SIMILARITY:
                    rule_hist = GeneralizedRuleHistory(constants.PORT_PROTOCOL_BASED_SIMILARITY, (base_rule, rule))
                    self.add_generalized_rule((rule, rule_hist), direction)
                    self.add_generalized_rule((base_rule, rule_hist), direction)
                elif similarity_vector.primary_similarity_type == constants.IP_BASED_SIMILARITY and domain_based_similarity_existence:
                    rule_hist = GeneralizedRuleHistory(constants.IP_BASED_SIMILARITY, (base_rule, rule))
                    self.add_generalized_rule((rule, rule_hist), direction)
                elif similarity_vector.primary_similarity_type == constants.IP_BASED_SIMILARITY:
                    rule_hist = GeneralizedRuleHistory(constants.IP_BASED_SIMILARITY, (base_rule, rule))
                    self.add_generalized_rule((rule, rule_hist), direction)
                    self.add_generalized_rule((base_rule, rule_hist), direction)
                elif similarity_vector.primary_similarity_type == constants.DOMAIN_BASED_SIMILARITY:
                    if constants.PORT_PROTOCOL_BASED_SIMILARITY in similarity_vector.get_all_vector_similarity_types():
                        new_rule = copy.deepcopy(rule)
                        generalized_domain = base_rule.get_generalized_domain()
                        new_rule.set_dns_to_generalized_domain(generalized_domain) # set the new domain
                        rule_hist = GeneralizedRuleHistory(constants.DOMAIN_BASED_SIMILARITY, (base_rule, rule))
                        self.add_generalized_rule((new_rule, rule_hist), direction)
                    else:
                        new_rule1 = copy.deepcopy(rule)
                        new_rule2 = copy.deepcopy(base_rule)
                        generalized_domain = base_rule.get_generalized_domain()
                        new_rule1.set_dns_to_generalized_domain(generalized_domain)  # set the new domain
                        new_rule2.set_dns_to_generalized_domain(generalized_domain)  # set the new domain
                        rule_hist = GeneralizedRuleHistory(constants.DOMAIN_BASED_SIMILARITY, (base_rule, rule))
                        self.add_generalized_rule((new_rule1, rule_hist), direction)
                        self.add_generalized_rule((new_rule2, rule_hist), direction)


    def check_domain_based_similarity_existence(self, relations_rules):
        for relations_rule in relations_rules:
            similarity_vector = relations_rule[1]
            if constants.DOMAIN_BASED_SIMILARITY in similarity_vector.get_all_vector_similarity_types():
                return True

    def add_generalized_rule(self, rule, direction):
        if direction == "from":
            self.add_generalized_rule_logic(rule, self.generalized_from_rules)
        else:
            self.add_generalized_rule_logic(rule, self.generalized_to_rules)

    def add_generalized_rule_logic(self, new_rule, rules):
        inserted = 0
        if hasattr(new_rule[0].matches[0], 'dns_name') and new_rule[0].matches[0].dns_name == "api.amazon.com":
            print("here")
        for rule in rules:
            #if new_rule[0].compare(rule[0]) and not rule[0].compare(new_rule[0]):
            if new_rule[0].compare(rule[0]) and new_rule[0].matches[0].is_domain_generalized:
                # take out rule and add new_rule instead
                rules.remove(rule)
                '''
                if inserted == 0:
                    rules.append(new_rule)
                    inserted = 1
                return
                '''
            elif new_rule[0].compare(rule[0]) and not new_rule[0].matches[0].is_domain_generalized:
                return
            elif new_rule[0].compare(rule[0]) and rule[0].compare(new_rule[0]):
                # do nothing its the same rule
                return
            elif not new_rule[0].compare(rule[0]) and rule[0].compare(new_rule[0]):
                # do nothing / add nothing
                return
            '''
            elif not new_rule.compare(rule) and not rule.compare(new_rule):
                # its a new rule so you can add it
                rules.append(new_rule)
                return
            '''
        rules.append(new_rule)
