import threading
import time

from nanotui import App, ProgressBar, GREEN, DEFAULT


def main():
    app = App("Progress Live Demo")

    bar = ProgressBar(x=4, y=4, width=40, color=DEFAULT, unfilled_symbol="|", fill_symbol="|")
    bar.add_progress("job", 0.0, GREEN)
    app.add_element(bar)

    stop_event = threading.Event()

    def advance_progress():
        value = 0.0
        while not stop_event.is_set() and value < 1.0:
            time.sleep(1)
            value = min(1.0, value + 0.03)
            bar.set_progress("job", value)

    worker = threading.Thread(target=advance_progress, daemon=True)
    worker.start()

    try:
        app.run()
    finally:
        stop_event.set()
        worker.join(timeout=1)
        


if __name__ == "__main__":
    main()
