package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"html/template"
	"io"
	"io/ioutil"
	"net/http"
	"os"
	"strings"
)

var taskQueue *TaskQueue

var pages *template.Template

type analysisFindings struct {
	Severity string `json:"severity"`
	File     string `json:"file"`
	Text     string `json:"text"`
}

type analysisItem struct {
	Catagory         string `json:"catagory"`
	Name             string `json:"name"`
	Language         string `json:"language"`
	ILength          int
	WLength          int
	DLength          int
	AnalysisFindings []analysisFindings `json:"findings"`
}

type analysisReport struct {
	Name         string
	Hash         string         `json:"hash"`
	Log          string         `json:"log"`
	Error        string         `json:"error"`
	AnalysisItem []analysisItem `json:"analysis"`
}

/*

{
	hash: "112233445566778899aa...",
	log: "[INFO] .... \n [ERROR] junk....",
	error: false,
	analysis: [
	  {
		 category: "linting"
		 name: "binary imports (objdump)",
		 language: "binary",
		 findings: [
	   {
			 severity: "warning",
			 file: "./server",
			 text: "import of gets(2) detected"
			}
			...
		 ]
	  }
	  ...
	]
  }
*/

/* Constant paths */
var basePath string
var templatesPath string

func init() {
	basePath = "./web"
	templatesPath = basePath + "/templates/*"

	var err error
	pages, err = template.ParseGlob(templatesPath)
	if err != nil {
		panic(err)
	}

	// Initialize task queue
	taskQueue = newTaskQueue("broker", "xl65x7jhacv", "localhost", "5672", "firmware", "reports")

	// Start report collector
	go reportCollector(taskQueue)
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}

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
		f3, _ := os.Create("./names/" + hex.EncodeToString(bs))
		f3.WriteString(handler.Filename)

		defer f1.Close()
		defer f2.Close()
		defer f3.Close()

		f2.Write(buf.Bytes())

		// Put firmware image into task queue
		taskQueue.publish <- buf.Bytes()

		http.Redirect(w, r, "/reports/"+hex.EncodeToString(bs), 301)
	}
}

func getReport(w http.ResponseWriter, r *http.Request) {
	fmt.Println("method:", r.Method)
	if r.Method == "GET" {
		fmt.Println(r.RequestURI)
		hash := strings.Split(r.RequestURI, "/")[2]

		fa, err := os.Stat("./analysis/" + hash)

		if os.IsNotExist(err) || fa.Size() == 0 {
			// Analysis does not exist or file is empty
			fmt.Println("Accessed in progress analysis" + hash)
			err = pages.ExecuteTemplate(w, "waiting.html", nil)
			fmt.Println(err)

		} else {
			// Analysis is complete
			fmt.Println("Accessed completed analysis" + hash)

			frep, frerr := ioutil.ReadFile("./analysis/" + hash)
			fname, fnerr := ioutil.ReadFile("./names/" + hash)
			check(frerr)
			check(fnerr)
			rawreport := frep
			jsonreport := analysisReport{}
			json.Unmarshal([]byte(rawreport), &jsonreport)

			jsonreport.Name = string(fname)
			for i, item := range jsonreport.AnalysisItem {
				jsonreport.AnalysisItem[i].ILength = 0
				jsonreport.AnalysisItem[i].WLength = 0
				jsonreport.AnalysisItem[i].DLength = 0
				for _, finding := range item.AnalysisFindings {
					if finding.Severity == "warning" {
						jsonreport.AnalysisItem[i].WLength++
					}
					if finding.Severity == "danger" {
						jsonreport.AnalysisItem[i].DLength++
					}
					if finding.Severity == "info" {
						jsonreport.AnalysisItem[i].ILength++
					}
				}
			}

			fmt.Println(jsonreport)

			err = pages.ExecuteTemplate(w, "report.html", jsonreport)
			fmt.Println(err)

		}

		//p, _ := loadPage(title)
		//fmt.Fprintf(w, "<h1>%s</h1><div>%s</div>", p.Title, p.Body)

		fmt.Println(hash)
	}
}

func reportCollector(taskQueue *TaskQueue) {
	jsonreport := analysisReport{}

	for msg := range taskQueue.consume {
		json.Unmarshal(msg.Body, &jsonreport)
		err := ioutil.WriteFile("./analysis/"+jsonreport.Hash, msg.Body, 0644)
		fmt.Println(err)
	}
}

func main() {
	fmt.Println("Starting go web server on port 8080")
	http.HandleFunc("/upload", upload)
	http.HandleFunc("/reports/", getReport)
	http.Handle("/", http.FileServer(http.Dir(basePath)))
	if err := http.ListenAndServe(":8080", nil); err != nil {
		panic(err)
	}
}
