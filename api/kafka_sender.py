import threading
import queue
from confluent_kafka import Producer


class KafkaEventSender:
    """Background, non-blocking Kafka sender (fire-and-forget).

    Events are queued in-memory and a daemon thread flushes them to the
    confluent_kafka.Producer. If the queue is full, events are dropped to
    avoid blocking the request path.
    """

    def __init__(self, conf, max_queue=10000, poll_interval=0.1):
        try:
            self._producer = Producer(conf)
        except Exception as e:
            print(f"Failed to connect to Kafka: {e}")
            self._producer = None
            return

        self._queue = queue.Queue(maxsize=max_queue)
        self._poll_interval = poll_interval
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def available(self):
        return self._producer is not None

    def send(self, topic, value):
        if not self.available():
            return
        try:
            self._queue.put_nowait((topic, value))
        except queue.Full:
            # Drop event if queue is full (non-blocking, fire-and-forget)
            return

    def _run(self):
        while self._running:
            try:
                topic, value = self._queue.get(timeout=self._poll_interval)
            except queue.Empty:
                topic = None

            if topic is not None:
                try:
                    self._producer.produce(topic, value=value)
                except Exception:
                    # Swallow to keep background thread alive
                    pass

            # Serve delivery callbacks without blocking
            try:
                self._producer.poll(0)
            except Exception:
                pass

    def stop(self, timeout=1.0):
        self._running = False
        self._thread.join(timeout)
        if self._producer:
            try:
                # attempt a non-blocking flush
                self._producer.flush(0)
            except Exception:
                pass
