package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"github.com/gorilla/mux"
	"io/ioutil"
	"log"
	"net/http"
	"sync"
)

func main() {
	upstreamServerinit()
}
func upstreamServerinit() {
	r := mux.NewRouter()
	r.HandleFunc("/", helloServer)
	r.HandleFunc("/api/sample/resource", helloServer)
	r.HandleFunc("/api/sample/resource/", helloServer)
	r.HandleFunc("/api/sample/resource/{id:[0-9]+}", helloServer)
	r.HandleFunc("/api/sample/resource/{id:[0-9]+}/employee/{id:[0-9]+}", helloServer)
	http.Handle("/", r)
	fmt.Printf("Upstream server started at port 8081")
	_ = http.ListenAndServe(":8081", nil)
}

/*
//urltokens struct
type urltokens struct {
	key   string `json:"key"`
	color string `json:"color"`
*/

func helloServer(w http.ResponseWriter, r *http.Request) {
	fmt.Println(r.RequestURI)
	switch r.Method {
	case "GET":
		vars := mux.Vars(r)
		id := vars["id"]
		fmt.Println("\nGET Request")
		if len(id) != 0 {
			fmt.Println("\nValue of id:=", string(id))
		}
		q := r.URL.Query()
		k := q.Get("key")
		c := q.Get("color")
		if len(c) != 0 || len(k) != 0 {
			w.Header().Set("Content-Type", "application/json")
			_, _ = w.Write([]byte(("{ \"key \":" + k + ",\"color\":" + c + "}")))
		}
		tokeniz, err := getData(id)
		fmt.Println("Data reverted :=", string(tokeniz))
		if err != nil {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(404)
		} else {
			var prettyJSON bytes.Buffer
			errosr := json.Indent(&prettyJSON, tokeniz, "", " ")
			if errosr != nil {
				log.Println("JSON parse error: ", errosr)
				return
			}
			jsonb := prettyJSON.Bytes()
			var m map[string]interface{}
			err = json.Unmarshal(jsonb, &m)
			if err != nil {
				return
			}
			m["Url"] = r.RequestURI
			newJson, err := json.Marshal(m)
			if err != nil {
				log.Println("JSON parse error: ", err)
				return
			}
			w.Header().Set("Content-Type", "application/json")
			_, err = w.Write(newJson)
			if err != nil {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(404)
				return
			}
		}

	case "POST":
		// Call ParseForm() to parse the raw query and update r.PostForm and r.Form.
		body, err := ioutil.ReadAll(r.Body)
		if err != nil {
			panic(err)
		}
		var prettyJSON bytes.Buffer
		error := json.Indent(&prettyJSON, body, "", " ")
		if error != nil {
			log.Println("JSON parse error: ", error)
			return
		}
		jsonb := prettyJSON.Bytes()
		var m map[string]interface{}
		err = json.Unmarshal(jsonb, &m)
		if err != nil {
			return
		}
		m["Url"] = r.RequestURI
		newJson, err := json.Marshal(m)

		vars := mux.Vars(r)
		id := vars["id"]
		fmt.Println("\nPOST Request")
		if len(id) != 0 {
			fmt.Println("\nValue of id :=", string(id))
		}
		fmt.Println("Data reverted :=", string(body))
		val := &testVector{
			Plaintext:     string(newJson),
			tokenizedData: newJson,
			uniqueToken:   id,
		}
		update(id, *val)
		w.Header().Set("Content-Type", "application/json")
		_, err = w.Write(newJson)
		if err != nil {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(404)
			return
		}
	case "PATCH":
		// Call ParseForm() to parse the raw query and update r.PostForm and r.Form.
		body, err := ioutil.ReadAll(r.Body)
		if err != nil {
			panic(err)
		}
		var prettyJSON bytes.Buffer
		error := json.Indent(&prettyJSON, body, "", " ")
		if error != nil {
			log.Println("JSON parse error: ", error)
			return
		}
		vars := mux.Vars(r)
		id := vars["id"]
		fmt.Println("\nPATCH Request")
		if len(id) != 0 {
			fmt.Println("\nValue of id :=", string(id))
		}
		fmt.Println("Data reverted :=", string(body))
		da, err := getData(id)
		if err != nil {
			w.WriteHeader(406)
			_, err = w.Write([]byte("Application server does not have any existing records for this uuid"))
			if err != nil {
				w.WriteHeader(404)
				return
			}
		}
		jsonb := prettyJSON.Bytes()
		var m map[string]interface{}
		err = json.Unmarshal(jsonb, &m)
		if err != nil {
			return
		}
		m["Url"] = r.RequestURI
		newJson, err := json.Marshal(m)
		if da != nil && len(da) > 0 {
			val := &testVector{
				Plaintext:     string(newJson),
				tokenizedData: newJson,
				uniqueToken:   id,
			}
			update(id, *val)
			w.Header().Set("Content-Type", "application/json")
			_, err = w.Write(newJson)
			if err != nil {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(404)
				return
			}
		}

	case "PUT":
		// Call ParseForm() to parse the raw query and update r.PostForm and r.Form.
		body, err := ioutil.ReadAll(r.Body)
		if err != nil {
			panic(err)
		}
		var prettyJSON bytes.Buffer
		error := json.Indent(&prettyJSON, body, "", " ")
		if error != nil {
			log.Println("JSON parse error: ", error)
			return
		}
		//		token := r.Header.Get("uuid")
		vars := mux.Vars(r)
		id := vars["id"]
		fmt.Println("\nPUT Request")
		if len(id) != 0 {
			fmt.Println("\nValue of id :=", string(id))
		}
		fmt.Println("Data reverted :=", string(body))
		da, err := getData(id)

		jsonb := prettyJSON.Bytes()
		var m map[string]interface{}
		err = json.Unmarshal(jsonb, &m)
		if err != nil {
			return
		}
		m["Url"] = r.RequestURI
		newJson, err := json.Marshal(m)
		if err != nil {
			log.Println("JSON parse error: ", err)
			return
		}



		if err != nil || (da != nil && len(da) > 0) {
			val := &testVector{
				Plaintext:     string(newJson),
				tokenizedData: newJson,
				uniqueToken:   id,
			}
			update(id, *val)
			w.Header().Set("Content-Type", "application/json")
			_, err = w.Write(newJson)
			if err != nil {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(404)
				return
			}
		}

	case "DELETE":

		body, err := ioutil.ReadAll(r.Body)
		if err != nil {
			panic(err)
		}
		var prettyJSON bytes.Buffer
		error := json.Indent(&prettyJSON, body, "", " ")
		if error != nil {
			log.Println("JSON parse error: ", error)
			return
		}
		//token := r.Header.Get("uuid")
		vars := mux.Vars(r)
		id := vars["id"]
		fmt.Println("\nDELETE Request")
		if len(id) != 0 {
			fmt.Println("\nValue of id :=", string(id))
		}
		fmt.Println("Data reverted :=", string(body))

		jsonb := prettyJSON.Bytes()
		var m map[string]interface{}
		err = json.Unmarshal(jsonb, &m)
		if err != nil {
			return
		}
		m["Url"] = r.RequestURI
		newJson, err := json.Marshal(m)
		if err != nil {
			log.Println("JSON parse error: ", err)
			return
		}

		val := &testVector{
			Plaintext:     string(newJson),
			tokenizedData:newJson,
			uniqueToken:   id,
		}
		update(id, *val)
		w.Header().Set("Content-Type", "application/json")
		_, err = w.Write(newJson)
		if err != nil {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(404)
			return
		}

	default:
		fmt.Fprintf(w, "Method not supported.")
	}
}

// Setup the decoder and call the DisallowUnknownFields() method on it.
// This will cause Decode() to return a "json: unknown field ..." error
// if it encounters any extra unexpected fields in the JSON. Strictly
// speaking, it returns an error for "keys which do not match any
// non-ignored, exported fields in the destination".

type testVector struct {
	Plaintext     string `json:"input_data"`
	tokenizedData []byte
	uniqueToken   string
}

var data []testVector
var once sync.Once
var mu sync.Mutex

var db sync.Map

func update(token string, val interface{}) {
	db.Store(token, val)
}

func getData(token string) ([]byte, error) {
	val, found := db.Load(token)
	if found {
		return val.(testVector).tokenizedData, nil
	}
	return nil, nil
}
