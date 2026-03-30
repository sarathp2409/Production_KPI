"""
Utility functions for pagination_dash app
"""
import json
import os


def get_competitor_choices_for_plant(plant_id=None, plant_name=None):
    """
    Load competitor names from comp_info.json based on plant location.

    Args:
        plant_id: Plant ID (e.g., "ODBCAIR30")
        plant_name: Plant display name (e.g., "Airoli")

    Returns:
        List of tuples [(competitor_name, competitor_name), ...]
        Returns empty list if no competitors found for the plant
    """
    # Load comp_info.json
    comp_info_path = os.path.join(
        os.path.dirname(__file__),
        'comp_info.json'
    )

    if not os.path.exists(comp_info_path):
        return []

    try:
        with open(comp_info_path, 'r') as f:
            comp_info = json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

    # Try to match by plant_name (case-insensitive)
    if plant_name:
        plant_key = plant_name.lower()
        if plant_key in comp_info:
            competitors = comp_info[plant_key]
            return [(comp, comp) for comp in competitors]

    # If plant_id is provided, try to map it to plant_name
    if plant_id:
        from upload_from_pi.plant_ids import plant_details
        plant = next((p for p in plant_details if p['id'] == plant_id), None)
        if plant:
            plant_key = plant['display_name'].lower()
            if plant_key in comp_info:
                competitors = comp_info[plant_key]
                return [(comp, comp) for comp in competitors]

    return []


def get_all_competitor_names():
    """
    Get all unique competitor names across all plants.

    Returns:
        List of unique competitor names sorted alphabetically
    """
    comp_info_path = os.path.join(
        os.path.dirname(__file__),
        'comp_info.json'
    )

    if not os.path.exists(comp_info_path):
        return []

    try:
        with open(comp_info_path, 'r') as f:
            comp_info = json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

    # Collect all unique competitor names
    all_competitors = set()
    for competitors_list in comp_info.values():
        all_competitors.update(competitors_list)

    return sorted(list(all_competitors))
