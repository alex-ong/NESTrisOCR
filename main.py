import time
import sys
import multiprocessing

from calibrate import mainLoop as calibrateLoop

from nestris_ocr.capturing import uncached_capture

# from nestris_ocr.scan_strat.fastest_strategy import FastestStrategy as Strategy

from nestris_ocr.scan_strat.naive_strategy import NaiveStrategy as Strategy
from nestris_ocr.network.network_client import NetClient

from nestris_ocr.network.cached_sender import CachedSender
from nestris_ocr.config import config

RATE = 1.0 / config["performance.scan_rate"]

def debug_print(msg):
    if config["debug.print_packet"]:
        print(msg)
        
def main(on_cap, check_network_close):
    strategy = Strategy()

    # The loop makes sure that the program retries constantly even when
    # capturing device is having trouble
    while True:
        try:
            ts, image = uncached_capture().get_image(rgb=True)

            if not ts and not image:
                debug_print("Exiting cleanly")
                break
        except KeyboardInterrupt:
            break
        except Exception:
            time.sleep(RATE)
            continue

        frame_end_ts = ts + RATE
        pre_strategy_ts = time.time()

        strategy.update(ts, image)
        result = strategy.to_dict()

        if config["debug.print_benchmark"]:
            elapsed_time = time.time() - ts
            print(f"Elapsed time since capture: {elapsed_time}")
            strategy_time = time.time() - pre_strategy_ts
            print(f"Strategy processing time: {strategy_time}")

        debug_print(result)

        on_cap(result, ts)

        # error = check_network_close()
        # if error is not None:
        #    return error

        time.sleep(max(frame_end_ts - time.time(), 0))


if __name__ == "__main__":
    multiprocessing.freeze_support()
    if len(sys.argv) >= 2 and sys.argv[1] == "--calibrate":
        calibrateLoop()
        sys.exit()

    print("Creating net client...")
    client = NetClient.CreateClient(config["network.host"], int(config["network.port"]))
    print("Net client created.")
    cachedSender = CachedSender(
        client, config["debug.print_packet"], config["network.protocol"]
    )

    result = None
    # try:
    print("Starting main loop")
    result = main(cachedSender.sendResult, client.checkNetworkClose)
    # except KeyboardInterrupt:
    #    pass
    uncached_capture().stop()

    if result:
        print(result)

    # todo: close and kill opencv thread if necessary...
    client.stop()
    client.join()
