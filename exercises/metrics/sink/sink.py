from conf import conf
from telemetryprocessor import TelemetryProcessor
from probelistener import ProbeListener

try:
    processor = TelemetryProcessor()
    listener = ProbeListener(conf.getListenConf(), processor)
    listener.start()
except KeyboardInterrupt:
    print("closing down")
    probelistener.stopLogging()