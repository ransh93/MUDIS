class Mud:
    def __init__(self, version, last_update, system_info, from_policy_name, to_policy_name):
        self.version = version
        self.last_update = last_update
        self.system_info = system_info
        self.from_policy_name = from_policy_name
        self.to_policy_name = to_policy_name
        self.to_access_list = None
        self.from_access_list = None

    # TODO: make all access_list action private
    def set_access_list(self, list_type, access_list):
        if list_type == 'to':
            self.to_access_list = access_list
        else:
            self.from_access_list = access_list

    def get_total_rules_count(self):
        to_access_list_count = len(self.to_access_list.aces)
        from_access_list_count = len(self.from_access_list.aces)
        total_count = to_access_list_count + from_access_list_count
        return total_count

    def show_all_matches(self):
        print("Showing all to device matches:")
        to_aces = self.to_access_list.aces
        for ace in to_aces:
            print(f"\t Showing ACE - {ace.name}")
            matches = ace.matches
            for match in matches:
                match.print_match()

        print("Showing all from device matches:")
        from_aces = self.from_access_list.aces
        for ace in from_aces:
            print(f"\t Showing ACE - {ace.name}")
            matches = ace.matches
            for match in matches:
                match.print_match()


    def compare_muds(self, mud_to_compare):
        first_mud_from_acl = self.from_access_list
        second_mud_from_acl = mud_to_compare.from_access_list
        identical_from_dt, different_from_dt = first_mud_from_acl.compare(second_mud_from_acl)

        first_mud_to_acl = self.to_access_list
        second_mud_to_acl = mud_to_compare.to_access_list
        identical_to_dt, different_to_dt = first_mud_to_acl.compare(second_mud_to_acl)

        identical_from_dt.extend(identical_to_dt) # from and to identical dt
        different_from_dt.extend(different_to_dt)  # from and to identical dt

        return identical_from_dt, different_from_dt



