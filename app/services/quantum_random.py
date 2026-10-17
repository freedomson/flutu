import json
import re

import requests

ANU_PERMUTATIONS_PAGE = "https://qrng.anu.edu.au/random-permutations/"
ANU_AJAX_ENDPOINT = "https://qrng.anu.edu.au/wp-admin/admin-ajax.php"


def choose_direction() -> bool:
    """Fetch a fresh ANU quantum-random permutation and map it to a direction."""
    page_response = requests.get(
        ANU_PERMUTATIONS_PAGE,
        headers={"User-Agent": "Flutu/1.0"},
        timeout=20,
    )
    page_response.raise_for_status()
    nonce_match = re.search(
        r'name="permutation_nonce_field"\s+value="([^"]+)"', page_response.text
    )
    if not nonce_match:
        raise ValueError("Could not retrieve the random generator nonce.")

    response = requests.post(
        ANU_AJAX_ENDPOINT,
        data={
            "set_num": "1",
            "max_num": "2",
            "action": "permutation_action",
            "permutation_nonce_field": nonce_match.group(1),
            "_wp_http_referer": "/random-permutations/",
        },
        headers={
            "Referer": ANU_PERMUTATIONS_PAGE,
            "User-Agent": "Flutu/1.0",
        },
        timeout=20,
    )
    response.raise_for_status()
    result = response.json()
    if isinstance(result, str):
        result = json.loads(result)
    if not isinstance(result, dict):
        raise ValueError("The generator returned an invalid response.")

    permutations = result.get("output") if result.get("type") == "success" else None
    if not isinstance(permutations, list) or not permutations:
        raise ValueError("The generator did not return a permutation.")
    values = permutations[0]
    if not isinstance(values, list) or not values or values[-1] not in (1, 2):
        raise ValueError("The generator returned an invalid permutation.")
    return values[-1] == 2
