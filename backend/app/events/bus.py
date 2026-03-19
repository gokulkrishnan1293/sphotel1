# Event bus for cross-domain communication.
#
# All cross-domain events (e.g., billing triggers a Telegram alert, KOT update
# triggers a kitchen display refresh) must go through this bus — never by direct
# service-to-service imports.
#
# TODO: implement Valkey pub/sub in a future story (real-time events) and
#       Postgres-backed queue for at-least-once delivery (Telegram alerts).


def publish(event_type: str, payload: dict[str, object]) -> None:
    """Publish a domain event to the bus.

    Args:
        event_type: Dot-notation event name, e.g. "bill.created", "print.job_queued".
        payload: Event payload dict. Must be JSON-serialisable.
    """
    # Stub: no-op until Valkey pub/sub is wired in.
    pass
