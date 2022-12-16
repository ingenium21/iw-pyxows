from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

class Metrics:
    def __init__(self):
        "Initializes the Metrics class to work with Prometheus."
        #Create a collector registry to store the metrics
        self.registry = CollectorRegistry()

        #Create a gauge metric to track the value of some variable
        #for now we're just going with a gauge metric since that's what we need
        self.gauge_metric = Gauge(registry=self.registry)

        def set_gauge_metric(self, value):
            """Sets the gauge metric"""
            self.gauge_metric.set(value)
        
        def push_metrics_to_server(self, gatewayHost, jobName):
            """pushes the metrics to prometheus server"""
            push_to_gateway(gatewayHost, jobName, registry=self.registry)
