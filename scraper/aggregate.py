from bs4 import BeautifulSoup
import json
import sys

soup = BeautifulSoup(sys.stdin.read(), 'html.parser')
tables = soup.find_all('table')
table_with_data = tables[1]

places = {}

for event in table_with_data.find_all('tr'):
    fields = event.find_all('td')
    if not fields:
        continue

    name = fields[3].text.strip()
    address = fields[4].text.strip()
    start = fields[1].text.strip()

    book_link = fields[0].find('a')
    if book_link:
        date = book_link.text.strip()
        end = fields[2].find_all(string=True, recursive=False)[0].strip()
        booking_id = book_link['href'].split('ssid=')[1]
    else:
        date = fields[0].text.strip()
        end = fields[2].text.strip()
        booking_id = None

    id = hash(address)
    appointment = {
        "start": start,
        "end": end,
        "booking_id": booking_id
    }

    if id in places:
        if date in places[id]['appointments']:
            raise Exception(f"Duplicate appointment for {name} on {date}")

        places[id]['appointments'][date] = appointment
    else:
        places[id] = ({
            'name': name,
            'address': address,
            'appointments': {date: appointment},
        })

places = list(places.values())

print(json.dumps(places, indent=4, ensure_ascii=False))
