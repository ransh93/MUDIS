import json
from logic.mud import Mud
import logic.constants as constants
from logic.access_list import AccessList


class Parser:
    def __init__(self, mud_path):
        self.mud_path = mud_path
        self.data = self.load_data(mud_path)
        self.mud = None

    def load_data(self, mud_path):
        with open(mud_path, 'r') as j:
            json_data = json.load(j)
        return json_data

    def parse(self):
        self.parse_metadata()

    def parse_metadata(self):
        metadata = self.data[constants.METADATA_KEY]
        version = metadata["mud-version"]
        last_update = metadata["last-update"]
        system_info = metadata["systeminfo"]
        from_policy_name = metadata["from-device-policy"]["access-lists"]["access-list"][0]["name"]
        to_policy_name = metadata["to-device-policy"]["access-lists"]["access-list"][0]["name"]
        self.mud = Mud(version, last_update, system_info, from_policy_name, to_policy_name)

    def parse_access_lists(self):
        acls = self.data[constants.ACL_ALL_KEY][constants.ACL_KEY]
        from_access_list = acls[0]
        to_access_list = acls[1]

        self.mud.from_access_list = AccessList(from_access_list[constants.ACL_NAME_KEY], from_access_list[constants.ACL_TYPE_KEY], "from")
        self.mud.from_access_list.parse(from_access_list[constants.ACL_ACES_KEY][constants.ACL_ACES_ACE_KEY])

        self.mud.to_access_list = AccessList(to_access_list[constants.ACL_NAME_KEY], to_access_list[constants.ACL_TYPE_KEY], "to")
        self.mud.to_access_list.parse(to_access_list[constants.ACL_ACES_KEY][constants.ACL_ACES_ACE_KEY])
