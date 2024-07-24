import cloudevents.conversion
import cloudevents.http
import cloudevents.http.event
from spin_sdk.http import IncomingHandler, Request, Response, send
import cloudevents

class IncomingHandler(IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        print("Request received")
        if request.method == "GET":
            event = cloudevents.http.CloudEvent.create({
                "type": "com.spin-app-python.person",
                "source": "http://spin-app-python.default.svc.cluster.local/event",
            }, {"user1": {"id": 12, "name": "Quyum", "age": 24}})
            data = cloudevents.conversion.to_binary(event)
            
            # Change to the address of your event gateway service (kubectl get svc -A)
            lister_address = "http://kubebuilder-controller-manager-service.kubebuilder-system.svc.cluster.local"
            request = Request("POST", lister_address, data[0], data[1])
            try:
                response = send(request)
            except Exception as e:
                print("Error sending event", e)
            print(f"Response: {response.body}")
            return Response(200, {"content-type": "application/json"}, {"message": "Successfully sent CloudEvent!"})
            
        if request.method == "POST":
            event = cloudevents.http.from_http(request.headers, request.body)
            print(f"Received event: {str(event)}")
            return Response(
                200,
                {"content-type": "application/json"},
                {"message": "Successfully received CloudEvent!"}
            )

        return Response(200, {"content-type": "application/json"}, {"message": "Method not allowed"})
