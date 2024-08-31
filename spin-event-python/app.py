import cloudevents.conversion
import cloudevents.http
import cloudevents.http.event
from spin_sdk.http import IncomingHandler, Request, Response, send
from spin_sdk import http, variables
import cloudevents

class IncomingHandler(IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        if request.method == "GET":
            event = cloudevents.http.CloudEvent.create({
                "type": "com.spin-event-python.person",
                "source": source_url(),
            }, {"user": {"id": 12, "name": "John Doe", "age": 24}})
            data = cloudevents.conversion.to_binary(event)
            
            gateway_address = gateway_url()
            print(f"Sending event to {gateway_address}")
            request = Request("POST", gateway_address, data[0], data[1])
            try:
                response = send(request)
                if response.status != 200:
                    print("Failed to publish event, got response: ", response)
                    return build_response(response.status, response.body)
                return build_response(200, "{\"message\": \"Successfully sent event!\"}")
            except Exception as e:
                print("Error sending event", e)
                return build_response(500, "{\"message\": \"Failed to send event!\"}")
            
        if request.method == "POST":
            event = cloudevents.http.from_http(request.headers, request.body)
            print(f"Received event: {str(event)}")
            return build_response(200, "{\"message\": \"Successfully received event!\"}")
        
        return build_response(405, "{\"message\": \"Method not allowed!\"}")

def source_url():
    app_svc = variables.get("spin_app_svc")
    namespace = variables.get("spin_app_namespace")
    source = f"http://{app_svc}.{namespace}.svc.cluster.local/event"
    return source

def gateway_url():
    gateway_name = variables.get("gateway_name")
    namespace = variables.get("gateway_namespace")
    gateway = f"http://{gateway_name}-service.{namespace}.svc.cluster.local"
    return gateway

def build_response(status, body):
    return Response(status, {"content-type": "application/json"}, bytes(body, "utf-8"))