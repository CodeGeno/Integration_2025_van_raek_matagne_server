from enum import Enum

class AccountRoleEnum(Enum):
	ADMINISTRATOR = "Administrateur"
	STUDENT = "Etudiant"
	PROFESSOR = "Enseignant"
	EDUCATOR = "Educateur"


class GenderEnum(Enum):
    MALE = "Masculin"
    FEMALE = "Féminin"