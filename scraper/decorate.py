import json
import sys
import os
import requests
from urllib.parse import quote

ADDRESS_CACHE_FILE = 'address_cache.json'
API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')


def load_cache():
    try:
        with open(ADDRESS_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def is_fixed_location(place):
    nameLower = place['name'].lower()
    KEYWORDS = [
        'vérellátó', 'vérell.',
        'transzfúziós', 'transzf.',
        'forráspont pécs',
        'sugár üzletközpont'
    ]
    return nameLower.endswith("intézeti") or any(keyword in nameLower for keyword in KEYWORDS)


def call_map_api(address):
    encoded_address = quote(address)

    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={API_KEY}&components=country:HU"
    data = requests.get(url).json()

    zeroResults = data['status'] == 'ZERO_RESULTS'
    inaccurate = not zeroResults and data['results'][0]['geometry']['location_type'] != 'ROOFTOP'

    if zeroResults or inaccurate:
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={encoded_address}&key={API_KEY}&region=hu"
        data = requests.get(url).json()

    return data


def call_geocode_api_best_effort(address):
    # tolerate network errors, flaky API responses, unknown addresses

    ATTEMPTS = 5
    dropped_street = False
    for _ in range(ATTEMPTS):
        try:
            data = call_map_api(address)

            if data['status'] == 'OK':
                return data
            elif data['status'] == 'ZERO_RESULTS' and not dropped_street:
                address = address.split(',')[0]  # drop street
                dropped_street = True

        except Exception as _:
            pass

    raise Exception(f"Failed to get coordinates for address: {address}")


def get_coordinates_cached(address, cache):
    if address in cache:
        return cache[address]

    sys.stderr.write(f"Fetching {address}...\n")

    data = call_geocode_api_best_effort(address)

    l = data['results'][0]['geometry']['location']
    coords = [l['lat'], l['lng']]

    cache[address] = coords
    return coords


if __name__ == "__main__":

    places = json.load(sys.stdin)
    addresses = load_cache()

    for place in places:
        place['is_fixed_location'] = is_fixed_location(place)
        place['coords'] = get_coordinates_cached(place['address'], addresses)

    # save
    with open(ADDRESS_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(addresses, f, indent=4, ensure_ascii=False)

    json.dump(places, sys.stdout, indent=4, ensure_ascii=False)
