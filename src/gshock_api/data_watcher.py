from reactivex.subject import Subject
import logging


class DataWatcher:
    logger = logging.getLogger("DataWatcher")

    def __init__(self):
        self.subjects = {}
        self.subscribers = {}

    def add_subject(self, name: str):
        if name in self.subjects:
            return
        subject = Subject()
        self.subjects[name] = subject

    def add_subscriber_and_subject(self, subscriber, subject):
        if subscriber not in self.subscribers:
            subjects_for_this_subscriber = set()
            self.subscribers[subscriber] = subjects_for_this_subscriber
        subjects_for_this_subscriber = self.subscribers[subscriber]
        if subject not in subjects_for_this_subscriber:
            subjects_for_this_subscriber.add(subject)
        else:
            self.logger("Subject {} alreadt added...".format(subject))

    def subscriber_already_subscribed(self, subscriber, subject):
        if subscriber not in self.subscribers:
            return False
        subjects_for_this_subscriber = self.subscribers[subscriber]
        if (
            subjects_for_this_subscriber is None
            or subject not in subjects_for_this_subscriber
        ):
            return False
        return True

    def subscribe(self, subscriber_name, subject, on_next):
        if not self.subscriber_already_subscribed(subscriber_name, subject):
            self.get_processor(subject).subscribe(on_next)
            self.add_subscriber_and_subject(subscriber_name, subject)

    def subscribe_with_deferred(self, subscriber_name, subject, on_next):
        if not self.subscriber_already_subscribed(subscriber_name, subject):
            self.get_processor(subject).subscribe(on_next)
            self.add_subscriber_and_subject(subscriber_name, subject)

    def get_processor(self, name):
        return self.subjects.get(name)

    def emit_event(self, name, event):
        subject = self.subjects[name]
        if subject is not None:
            subject.on_next(event)


data_watcher = DataWatcher()
