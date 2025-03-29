from enum import Enum

class AccountTypeEnum(Enum):
    PROFESSOR = "Professeur"
    STUDENT = "Etudiant"
    ADMINISTRATOR = "Administrateur"
    EDUCATOR = "Educateur"


class GenderEnum(Enum):
    MALE = "Masculin"
    FEMALE = "Féminin"
