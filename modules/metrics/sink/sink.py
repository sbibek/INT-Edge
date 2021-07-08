from conf import conf
from telemetryprocessor import TelemetryProcessor
from probelistener import ProbeListener
from metaserver import MetaServer

try:
    processor = TelemetryProcessor()
    metaserver = MetaServer(processor)
    listener = ProbeListener(conf.getListenConf(), processor)
    metaserver.start()
    listener.start()
except KeyboardInterrupt:
    print("closing down")
    probelistener.stopLogging()