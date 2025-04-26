from enum import Enum

class AccountRoleEnum(Enum):
    PROFESSOR = "Professeur"
    ADMINISTRATOR = "Administrateur"
    EDUCATOR = "Educateur"
    STUDENT = "Etudiant"


class GenderEnum(Enum):
    MALE = "Masculin"
    FEMALE = "Féminin"