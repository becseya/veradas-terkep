import json
import sys
import os
import requests
from urllib.parse import quote
from datetime import datetime

ADDRESS_CACHE_FILE = 'address_cache.json'
LOCATION_HISTORY_FILE = 'location_history.json'
API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')


def load_cache():
    try:
        with open(ADDRESS_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def load_history():
    try:
        with open(LOCATION_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def isFixedLocation(place):
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


def get_intervals(start: str, end: str):
    INTERVALS = [
        ("morning", 8, 10),
        ("beforeLunch", 10, 13),
        ("afterLunch", 13, 17),
        ("evening", 17, 19),
    ]

    start_hour = int(start.split(':')[0])
    end_hour = int(end.split(':')[0])

    result = []
    for name, interval_start, interval_end in INTERVALS:
        if start_hour < interval_end and end_hour > interval_start:
            result.append(name)

    return result


def get_place_id(place):
    # We are using coordinates as a UID to tolerate minor changes in address / name.
    return '_'.join(map(str, place['coords']))


def compare_appointment_lists(current, old):
    # TODO: Detect if future appointment is being removed
    # TODO: Fading past appointments are not a real change
    # TODO: Might contain 'NEW' appointment, even if already present in history
    if set(current) == set(old):
        return 'SAME'
    else:
        return 'CHANGED'


def update_history(history, place):
    id = get_place_id(place)
    appointments = list(place['appointments'].keys())
    now = datetime.now().isoformat()

    if id not in history:
        history[id] = {
            'appointments': appointments,
            'lastModified': now,
        }
        state = 'NEW'
    else:
        old_appointments = history[id]['appointments']
        state = compare_appointment_lists(appointments, old_appointments)

        if state != 'SAME':
            history[id]['appointments'] = appointments
            history[id]['lastModified'] = now

    return state


def cull_history(history, places):
    current_ids = {get_place_id(place) for place in places}

    for id in list(history.keys()):
        if id not in current_ids:
            del history[id]


def get_day_of_week(date_str: str) -> int:
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.weekday()  # Monday is 0 and Sunday is 6


if __name__ == "__main__":

    places = json.load(sys.stdin)
    addresses = load_cache()
    history = load_history()

    for place in places:
        place['isFixedLocation'] = isFixedLocation(place)
        place['coords'] = get_coordinates_cached(place['address'], addresses)

        for date, apt in place['appointments'].items():
            apt['intervals'] = get_intervals(apt['start'], apt['end'])
            apt['dayOfWeek'] = get_day_of_week(date)

        place['state'] = update_history(history, place)
        place['lastModified'] = history[get_place_id(place)]['lastModified']

    cull_history(history, places)

    # save
    with open(ADDRESS_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(addresses, f, indent=4, ensure_ascii=False)

    with open(LOCATION_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

    json.dump(places, sys.stdout, indent=4, ensure_ascii=False)
