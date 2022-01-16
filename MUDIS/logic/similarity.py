import logic.constants as constants


class SimilarityComponent(object):
    def __init__(self, match_type, is_similar,similarity_score, similarity_type):
        self.match_type = match_type
        self.is_similar = is_similar
        self. similarity_score = similarity_score
        self.similarity_type = similarity_type


class SimilarityVector(object):
    def __init__(self):
        self.similarity_components = []
        self.primary_similarity_type = None  # Domain_based -> IP_based -> PortAndProtocol_based
        self.is_vector_similar = False  # does one of the components is True

    def add_component(self, similarity_comp):
        self.similarity_components.append(similarity_comp)

    def get_all_vector_similarity_types(self):
        return [sim_component.similarity_type for sim_component in self.similarity_components if sim_component.is_similar]

    def determine_vector_similarity_status(self):
        for sim_component in self.similarity_components:
            if sim_component is None:
                print("here")
            if sim_component.is_similar and sim_component.similarity_type == constants.DOMAIN_BASED_SIMILARITY:
                self.is_vector_similar = True
                self.primary_similarity_type = constants.DOMAIN_BASED_SIMILARITY
                break
            elif sim_component.is_similar and sim_component.similarity_type == constants.IP_BASED_SIMILARITY:
                self.is_vector_similar = True
                self.primary_similarity_type = constants.IP_BASED_SIMILARITY
                break
            # added handling with "ietf-mud:mud" so he wont think they are all similar and show them in clustered ACEs
            elif sim_component.is_similar and sim_component.similarity_type != "ietf-mud:mud":
                self.is_vector_similar = True
                self.primary_similarity_type = sim_component.similarity_type

