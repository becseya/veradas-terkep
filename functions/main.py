from firebase_functions import scheduler_fn
from firebase_admin import initialize_app, firestore, messaging

initialize_app()


@scheduler_fn.on_schedule(schedule="0 9 * * *", timezone="Europe/Budapest")
def scheduled_notification_task(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Runs every day at 9 AM.
    """
    try:
        # TODO fetch location
        process_notifications()

    except Exception as e:
        print(f"Error in scheduled task: {e}")


def process_notifications():
    db = firestore.client()
    subscriptions_ref = db.collection('subscriptions')
    docs = subscriptions_ref.stream()

    notifications_sent = 0
    error_encountered = 0

    for doc in docs:
        try:
            token = doc.id

            # TODO match location radius
            # TODO one notification per appointment
            message = messaging.Message(
                notification=messaging.Notification(
                    title='Test notification!',
                    body=f"Test notification body"
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
