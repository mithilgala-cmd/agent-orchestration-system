from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.trace import Status, StatusCode

# Setup OpenTelemetry
provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

class AgentTracer:
    @staticmethod
    def start_span(name: str):
        return tracer.start_as_current_span(name)

    @staticmethod
    def log_decision(span, agent_name: str, decision: str):
        span.set_attribute("agent.name", agent_name)
        span.set_attribute("agent.decision", decision)
        span.add_event("decision_made", {"decision": decision})

    @staticmethod
    def log_tool_call(span, tool_name: str, inputs: dict):
        span.set_attribute("tool.name", tool_name)
        span.set_attribute("tool.inputs", str(inputs))
        span.add_event("tool_invoked", {"tool": tool_name})
