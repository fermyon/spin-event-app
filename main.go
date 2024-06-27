package main

import (
	cloudevents "github.com/cloudevents/sdk-go/v2"
	spinhttp "github.com/fermyon/spin/sdk/go/v2/http"
	"log"
	"net/http"
)

func init() {
	spinhttp.Handle(func(w http.ResponseWriter, r *http.Request) {
		event, err := cloudevents.NewEventFromHTTPRequest(r)
		if err != nil {
			log.Printf("failed to parse CloudEvent from request: %v", err)
			http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
		}
		_, err = w.Write([]byte(event.String()))
		if err != nil {
			log.Printf("error occured while writing response.")
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
		}
		log.Println(event.String())
		w.Header().Set("Content-Type", "text/plain")
	})
}

func main() {}
