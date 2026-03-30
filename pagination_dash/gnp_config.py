"""
Configuration for GNP Publications by Plant Location
Maps plant names to the publications they capture for GNP Information.
"""

# Mapping of publication short codes to their full names
PUBLICATION_NAMES = {
    'ET': 'et',
    'MT': 'mt',
    'Mirror': 'mirror',
    'NBT': 'nbt',
    'TIMS': 'tims'
}

# Plant-specific GNP publications configuration
# Key: Plant name, Value: List of publications (using short codes)
PLANT_GNP_PUBLICATIONS = {
    "Airoli": ["Mirror", "MT", "TIMS"],
    "Baroda": [],
    "Bhosari": ["ET", "MT", "TIMS"],
    "Bommasandra": ["ET", "TIMS", "Mirror"],
    "Butibori": [],
    "Chemmencherry": ["ET", "TIMS"],
    "Chinhat": ["ET", "NBT", "TIMS"],
    "Kandivali": ["ET", "MT", "NBT", "Mirror", "TIMS"],
    "Manesar": ["NBT", "TIMS"],
    "Nacharam": ["ET", "TIMS"],
    "Sahibabad": ["ET", "NBT", "TIMS"],
    "Saltlake": ["ET", "TIMS"],
    "Trivandrum": [],
    "Vejalpur": ["ET", "TIMS"],
}


def get_gnp_publications_for_plant(plant_name):
    """
    Get the list of GNP publications for a specific plant.

    Args:
        plant_name (str): Name of the plant

    Returns:
        list: List of publication short codes (e.g., ['ET', 'TIMS'])
    """
    return PLANT_GNP_PUBLICATIONS.get(plant_name, [])


def has_gnp_publications(plant_name):
    """
    Check if a plant has any GNP publications configured.

    Args:
        plant_name (str): Name of the plant

    Returns:
        bool: True if plant has GNP publications, False otherwise
    """
    publications = get_gnp_publications_for_plant(plant_name)
    return len(publications) > 0


def get_gnp_field_names_for_plant(plant_name):
    """
    Get the list of GNP model field names for a specific plant.
    Includes et_had_2_books, et_b1, and et_b2 fields if plant has ET publication.

    Args:
        plant_name (str): Name of the plant

    Returns:
        list: List of field names (e.g., ['et', 'et_b1', 'et_b2', 'tims', 'et_had_2_books'])
    """
    publications = get_gnp_publications_for_plant(plant_name)
    field_names = [PUBLICATION_NAMES[pub] for pub in publications if pub in PUBLICATION_NAMES]

    # Add ET special fields if plant has ET
    if 'ET' in publications:
        # Add et_b1 and et_b2 right after et in the list
        et_index = field_names.index('et')
        field_names.insert(et_index + 1, 'et_b1')
        field_names.insert(et_index + 2, 'et_b2')
        field_names.append('et_had_2_books')

    return field_names


def get_publication_display_info(plant_name):
    """
    Get display information for publications including field names and labels.
    Includes ET B-1 and ET B-2 if plant has ET publication.

    Args:
        plant_name (str): Name of the plant

    Returns:
        list: List of dicts with 'field_name', 'short_code', and 'display_label'
    """
    publications = get_gnp_publications_for_plant(plant_name)

    # Full display names for each publication
    display_labels = {
        'ET': 'ET (Economic Times)',
        'MT': 'MT (Maharashtra Times)',
        'Mirror': 'Mirror',
        'NBT': 'NBT (Navbharat Times)',
        'TIMS': 'TIMS'
    }

    result = []
    for pub in publications:
        if pub in PUBLICATION_NAMES:
            result.append({
                'field_name': PUBLICATION_NAMES[pub],
                'short_code': pub,
                'display_label': display_labels.get(pub, pub)
            })

            # Add ET B-1 and ET B-2 right after ET
            if pub == 'ET':
                result.append({
                    'field_name': 'et_b1',
                    'short_code': 'ET B-1',
                    'display_label': 'ET B-1'
                })
                result.append({
                    'field_name': 'et_b2',
                    'short_code': 'ET B-2',
                    'display_label': 'ET B-2'
                })

    return result
