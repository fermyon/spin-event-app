import cloudevents.conversion
import cloudevents.http
import cloudevents.http.event
from spin_sdk.http import IncomingHandler, Request, Response, send
from spin_sdk import http, variables
import cloudevents

class IncomingHandler(IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        print("Request received")
        if request.method == "GET":
            event = cloudevents.http.CloudEvent.create({
                "type": "com.spin-event-python.person",
                "source": source_url(),
            }, {"user": {"id": 12, "name": "John Doe", "age": 24}})
            data = cloudevents.conversion.to_binary(event)
            
            # Change to the address of your event gateway service (kubectl get svc -A)
            gateway_address = gateway_url()
            print(f"Sending event to {gateway_address}")
            request = Request("POST", gateway_address, data[0], data[1])
            try:
                response = send(request)
            except Exception as e:
                print("Error sending event", e)
                return Response(500, {"content-type": "application/json"}, bytes(e, "utf-8"))
            return Response(200, {"content-type": "application/json"}, bytes("{\"message\": \"Successfully sent CloudEvent!\"}", "utf-8"))
            
        if request.method == "POST":
            event = cloudevents.http.from_http(request.headers, request.body)
            print(f"Received event: {str(event)}")
            return Response(
                200,
                {"content-type": "application/json"},
                bytes("{\"message\": \"Successfully received CloudEvent!\"}", "utf-8")
            )

        return Response(200, {"content-type": "application/json"}, bytes("Method not allowed", "utf-8"))

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