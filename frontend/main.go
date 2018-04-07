package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
)

func upload(w http.ResponseWriter, r *http.Request) {
	fmt.Println("method:", r.Method)
	if r.Method == "POST" {
		r.ParseMultipartForm(32 << 20)
		file, handler, err := r.FormFile("uploadfile")
		if err != nil {
			fmt.Println(err)
			return
		}
		f, err := os.Create("./uploads/" + handler.Filename)

		buf := bytes.NewBuffer(nil)
		io.Copy(buf, file)
		f.Write(buf.Bytes())
		defer f.Close()
		defer file.Close()

		h := sha256.New()

		h.Write(buf.Bytes())

		bs := h.Sum(nil)

		f1, _ := os.Create("./analysis/" + hex.EncodeToString(bs))
		f2, _ := os.Create("./binaries/" + hex.EncodeToString(bs))

		defer f1.Close()
		defer f2.Close()

		f2.Write(buf.Bytes())

		http.Redirect(w, r, "/reports/"+hex.EncodeToString(bs), 301)
	}
}

func getReport(w http.ResponseWriter, r *http.Request) {
	fmt.Println("method:", r.Method)
	if r.Method == "GET" {
		fmt.Println(r.RequestURI)
		hash := strings.Split(r.RequestURI, "/")[2]

		fmt.Println(hash)
	}
}

func main() {
	fmt.Println("Starting go web server on port 8080")
	http.HandleFunc("/upload", upload)
	http.HandleFunc("/reports/", getReport)
	http.Handle("/", http.FileServer(http.Dir("./web")))
	if err := http.ListenAndServe(":8080", nil); err != nil {
		panic(err)
	}
}
