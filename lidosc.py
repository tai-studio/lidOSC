# read out lid angle and send via OSC
# program function:
# + read command-line arguments for OSC IP and port via argparse
# + establish connection to OSC interface (sending only)
# + read out initial lid angle and send via OSC
# + monitor lid angle changes and send via OSC



from pybooklid import LidSensor
from pythonosc import udp_client
import threading
import time


# lid readout function
def read_lid(
    sensor,
    osc_client,
    osc_message_name="/lid",
    initial_read=True,
    debug=False,
    interval: float = 0.0,
):
    """Read lid angle changes and optionally send periodic heartbeats.

    Parameters
    ----------
    sensor : LidSensor
        The lid sensor instance (not yet connected if auto_connect=False).
    osc_client : pythonosc.udp_client.SimpleUDPClient
        OSC client used for sending messages.
    osc_message_name : str
        OSC address/path.
    initial_read : bool
        Whether to perform and send an immediate initial reading.
    debug : bool
        If True, print debug information to stdout.
    interval : float
        Heartbeat interval in seconds. If > 0, the latest angle is resent at this
        cadence even if unchanged. <= 0 disables heartbeat.
    """

    latest_angle = None
    stop_event = threading.Event()
    heartbeat_thread = None

    def heartbeat_loop():
        if debug:
            print(f"[heartbeat] started (interval={interval}s)")
        # Use wait(...) so we can exit quickly on stop_event
        while not stop_event.wait(interval):
            if latest_angle is not None:
                osc_client.send_message(osc_message_name, latest_angle)
                if debug:
                    print(f"[heartbeat] {latest_angle:.1f}°")
        if debug:
            print("[heartbeat] stopping")

    try:
        sensor.connect()

        # Perform an initial blocking read if requested
        if initial_read:
            try:
                angle = sensor.read_angle()
                latest_angle = angle
                osc_client.send_message(osc_message_name, angle)
                if debug:
                    print(f"Initial lid angle: {angle:.1f}°")
            except Exception as e:  # noqa: BLE001
                if debug:
                    print(f"Initial read failed: {e}")

        # Start heartbeat thread if enabled
        if interval and interval > 0:
            heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
            heartbeat_thread.start()

        # Callback for monitor() to allow immediate debug printing
        def on_angle_change(angle):  # noqa: D401
            if debug:
                print(f"Lid angle: {angle:.1f}°")

        # Iterate over change events
        for angle in sensor.monitor(callback=on_angle_change):
            latest_angle = angle
            osc_client.send_message(osc_message_name, angle)
    except KeyboardInterrupt:
        if debug:
            print("Interrupted by user.")
    finally:
        stop_event.set()
        if heartbeat_thread is not None and heartbeat_thread.is_alive():
            heartbeat_thread.join(timeout=1.0)
        sensor.disconnect()

# initialise OSC client
def init_osc_client(ip="localhost", port=8000):
    client = udp_client.SimpleUDPClient(ip, port)
    return client



def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Read lid angle and send via OSC")
    parser.add_argument("-i", "--ip", default="localhost", help="OSC server IP address (default: %(default)s)")
    parser.add_argument("-p", "--port", type=int, default=8000, help="OSC server port (default: %(default)s)")
    parser.add_argument("-m", "--message", default="/lid", help="OSC message name (default: %(default)s)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug output")
    parser.add_argument("-d", "--interval", type=float, default=None, help="Interval to repeat sending independent of lid changes in seconds (default: %(default)s)")
    args = parser.parse_args()

    # Initialize OSC client
    osc_client = init_osc_client(args.ip, args.port)

    # Initialize lid sensor
    sensor = LidSensor(auto_connect=False)

    read_lid(
        sensor,
        osc_client,
        args.message,
        initial_read=True,
        debug=args.verbose,
        interval=args.interval,
    )




if __name__ == "__main__":
    main()
