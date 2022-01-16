from muddy.maker import make_mud, make_acl_names, make_policy, make_acls, make_support_info
from muddy.models import Direction, MatchType
import logic.constants as constants
import json
import random
import uuid


class MudGenerator(object):
    def __init__(self, version, mud_url, is_supported, cache_validity, system_info):
        self.support_info = make_support_info(version, mud_url, is_supported, cache_validity, system_info)
        self.mud_name = f'mud-{random.randint(10000, 99999)}'

        self.policies = {}
        self.from_acl = []
        self.to_acl = []
        self.acl = []

    def generate_mud(self, from_rules, to_rules, mongo_dal, generalized_mud_name, generalized_title_name,
                     first_mud_location, second_mud_location, device_name, device_type):

        # TODO: MatchType.IS_CLOUD read more about it

        if len(from_rules) == 0 or len(to_rules) == 0:
            return

        # handel from rules
        direction_initiated = Direction.FROM_DEVICE
        for rule in from_rules:
            ip_version, protocol = rule.get_ip_version_and_protocol()
            identifier = rule.get_ace_identifier()  # get domain of ip
            port = rule.get_ace_port()  # get port
            # in order to be compatible to weird mud from icm paper
            if port is None or identifier is None or protocol is None or protocol == "ICMP":
                continue
            acl_names = make_acl_names(self.mud_name, ip_version, direction_initiated)
            self.policies.update(make_policy(direction_initiated, acl_names))
            if len(self.from_acl) == 0:
                self.from_acl.append(make_acls([ip_version], identifier, protocol, MatchType.IS_CLOUD, direction_initiated,
                              [port], None, acl_names))
            else:
                acl = (make_acls([ip_version], identifier, protocol, MatchType.IS_CLOUD, direction_initiated,
                              [port], None, acl_names))
                self.from_acl[0]["aces"]["ace"].append(acl["aces"]["ace"][0])


        # handel to rules
        direction_initiated = Direction.TO_DEVICE
        for rule in to_rules:
            ip_version, protocol = rule.get_ip_version_and_protocol()
            identifier = rule.get_ace_identifier()  # get domain of ip
            port = rule.get_ace_port()  # get port
            # in order to be compatible to weird mud from icm paper
            if port is None or identifier is None or protocol is None:
                continue
            acl_names = make_acl_names(self.mud_name, ip_version, direction_initiated)
            self.policies.update(make_policy(direction_initiated, acl_names))
            if len(self.to_acl) == 0:
                self.to_acl.append(make_acls([ip_version], identifier, protocol, MatchType.IS_CLOUD, direction_initiated,
                                   [port], None, acl_names))
            else:
                acl = (make_acls([ip_version], identifier, protocol, MatchType.IS_CLOUD, direction_initiated,
                                 [port], None, acl_names))
                self.to_acl[0]["aces"]["ace"].append(acl["aces"]["ace"][0])

        self.acl = self.from_acl + self.to_acl

        # when they are None is means we have no rules and policies
        if len(self.acl) != 0 or len(self.policies) != 0:
            mud = make_mud(self.support_info, self.policies, self.acl)

            # write our mud file to the server disk
            #full_mud_file_path = "{}\{}".format(constants.UPLOAD_FOLDER, generalized_mud_name)
            #f = open(full_mud_file_path, "w")
            #mud_content = f.write(json.dumps(mud, indent=4))
            #f.close()

            # insert the mud file into the database
            #self.insert_mud_into_db(mongo_dal, mud, full_mud_file_path, generalized_title_name , first_mud_location, second_mud_location, device_name, device_type)

    def insert_mud_into_db(self, mongo_dal, mud_content, full_mud_file_path, generalized_title_name, first_mud_location, second_mud_location, device_name, device_type):
        # prepare mud db data
        creator = "mudgee"
        mud_location = "generalization_{}_{}".format(first_mud_location, second_mud_location)

        # set all dict data
        generalized_mud_data = dict()
        generalized_mud_data['_id'] = str(uuid.uuid4())
        generalized_mud_data['mud_name'] = generalized_title_name
        generalized_mud_data['device_name'] = device_name
        generalized_mud_data['device_type'] = device_type
        generalized_mud_data['creator'] = creator
        generalized_mud_data['dev_location'] = mud_location
        generalized_mud_data['mud_file_path'] = full_mud_file_path
        generalized_mud_data['mud_content'] = mud_content

        # insert the given data in to the DB
        mongo_dal.insert(generalized_mud_data)

        # TODO: add a check that this inserted mud is not exist and if not insert
