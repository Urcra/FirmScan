package main

import (
	"bytes"
	"crypto/sha1"
	"encoding/hex"
	"fmt"
	"io"
	"net/http"
	"os"
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

		h := sha1.New()

		h.Write(buf.Bytes())

		bs := h.Sum(nil)

		http.Redirect(w, r, "/reports/"+hex.EncodeToString(bs), 301)
		fmt.Fprintf(w, "%v", handler.Header)
	}
}

func main() {
	fmt.Println("Starting go web server on port 8080")
	http.Handle("/", http.FileServer(http.Dir("./web")))
	http.HandleFunc("/upload", upload)
	if err := http.ListenAndServe(":8080", nil); err != nil {
		panic(err)
	}
}
