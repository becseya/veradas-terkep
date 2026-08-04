import json
import math
import requests
from datetime import datetime
from firebase_functions import scheduler_fn
from firebase_admin import initialize_app, firestore, messaging

initialize_app()


@scheduler_fn.on_schedule(schedule="0 9 * * *", timezone="Europe/Budapest")
def scheduled_notification_task(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Runs every day at 9 AM.
    """
    try:
        response = requests.get("https://veradas-terkep.hu/locations.json")
        locations = response.json()
        process_notifications(locations['locations'])

    except Exception as e:
        print(f"Error in scheduled task: {e}")


def parse_details(doc):
    details_str = doc.to_dict().get('details', None)

    if details_str is None:
        return None

    try:
        details = json.loads(details_str)

        if not isinstance(details, dict):
            return None

        # Validate zones
        if 'zones' not in details or not isinstance(details['zones'], list):
            return None

        for zone in details['zones']:
            if not isinstance(zone, dict):
                return None
            if not all(key in zone for key in ['lat', 'lng', 'radiusKm', 'filter']):
                return None
            if not isinstance(zone['lat'], (int, float)) or not isinstance(zone['lng'], (int, float)):
                return None
            if not isinstance(zone['radiusKm'], (int, float)):
                return None
            if not isinstance(zone['filter'], int):
                return None

        # Validate snoozeUntil
        if 'snoozeUntil' not in details:
            return None

        details['snoozeUntil'] = datetime.fromisoformat(details['snoozeUntil'])

        return details
    except Exception:
        return None


def is_within_radius(details, location):
    def haversine_distance_km(lat1, lng1, lat2, lng2):
        EARTH_RADIUS_KM = 6371
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lng2 - lng1)

        a = (
            math.sin(d_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return EARTH_RADIUS_KM * c

    for zone in details['zones']:
        lat1 = zone['lat']
        lng1 = zone['lng']
        lat2 = location['coords'][0]
        lng2 = location['coords'][1]
        distance_km = haversine_distance_km(lat1, lng1, lat2, lng2)

        radius_km = zone.get('radiusKm', zone.get('radius'))

        if distance_km <= radius_km:
            return True

    return False


def is_at_least_one_new_appointment(details, locations):
    for location in locations:
        if is_within_radius(details, location) and location['state'] == 'NEW':
            return True

    return False


def process_notifications(locations):
    db = firestore.client()
    subscriptions_ref = db.collection('subscriptions')
    docs = subscriptions_ref.stream()

    notifications_sent = 0
    error_encountered = 0

    for doc in docs:
        try:
            token = doc.id
            details = parse_details(doc)

            if details is None:
                print(f"Deleted subscription with invalid details: {token}")
                doc.reference.delete()
                continue

            if is_at_least_one_new_appointment(details, locations):
                message = messaging.Message(
                    notification=messaging.Notification(
                        title='Új véradási helyszín a közeledben!',
                        body=f"Kattints a részletekért..."
                    ),
                    token=token
                )
                messaging.send(message)
                notifications_sent += 1

        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            error_encountered += 1

    print(
        f"Sent {notifications_sent} notifications, encountered {error_encountered} errors"
    )
