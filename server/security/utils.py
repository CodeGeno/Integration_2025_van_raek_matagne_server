def normalize_name(name):
    """
    Normalise un nom ou prénom en suivant ces règles:
    - Supprime les espaces en début et fin (trim)
    - Première lettre de chaque partie du nom en majuscule
    - Reste des lettres en minuscule
    - Gère les noms composés (avec espaces)
    
    Exemples:
    - "keVin " devient "Kevin"
    - " Van raEk " devient "Van Raek"
    """
    if not name:
        return name
    
    # Supprimer les espaces en début et fin
    name = name.strip()
        
    # Séparer les parties du nom (pour les noms composés)
    name_parts = name.split()
    
    # Normaliser chaque partie du nom
    normalized_parts = [part.capitalize() for part in name_parts]
    
    # Rejoindre les parties normalisées
    return " ".join(normalized_parts)

def normalize_for_email(text):
    """
    Normalise une chaîne de caractères pour une utilisation dans une adresse email:
    - Supprime les espaces en début et fin (trim)
    - Supprime tous les espaces (au lieu de les remplacer par des points)
    - Convertit en minuscules
    
    Exemples:
    - " Kevin " devient "kevin"
    - " Van Raek " devient "vanraek"
    """
    if not text:
        return text
    
    # Supprimer les espaces en début et fin et convertir en minuscules
    trimmed = text.strip().lower()
    
    # Supprimer tous les espaces
    return trimmed.replace(" ", "") 