package main
import (
	"fmt"
	"sync"
)

type Fetcher interface {
	// Fetch returns the body of URL and
	// a slice of URLs found on that page.
	Fetch(url string) (body string, urls []string, err error)
}

type URLCache struct {
	m map[string]int
	l sync.Mutex
}

func (cache *URLCache) crawled(url string) bool {
	cache.l.Lock()
	defer cache.l.Unlock()
	_, ok := cache.m[url]

	if !ok {
		cache.m[url] = 1
		return false
	}
	return true
}

var cache URLCache = URLCache{m: make(map[string]int)}

// Crawl uses fetcher to recursively crawl
// pages starting with url, to a maximum of depth.
func Crawl(url string, depth int, fetcher Fetcher, ch chan int) {
	// TODO: Fetch URLs in parallel.
	// TODO: Don't fetch the same URL twice.
	// This implementation doesn't do either:

	if cache.crawled(url) {
		ch <- 1
		return 
	}

	if depth <= 0 {
		ch <- 1
		return
	}

	body, urls, err := fetcher.Fetch(url)
	if err != nil {
		fmt.Println(err)
		ch <- 1
		return
	}
	fmt.Printf("found: %s %q\n", url, body)

	ctl := make(chan int)
	counter := 0
	for _, u := range urls {
		go Crawl(u, depth-1, fetcher, ctl)
		counter++
	}
	for i := 0; i < counter; i++ {
		<-ctl
	}
	ch <- 1
	return
}

func main() {
	ch := make(chan int)
	go Crawl("http://golang.org/", 4, fetcher, ch)
	<- ch
}

// fakeFetcher is Fetcher that returns canned results.
type fakeFetcher map[string]*fakeResult

type fakeResult struct {
	body string
	urls []string
}

func (f fakeFetcher) Fetch(url string) (string, []string, error) {
	if res, ok := f[url]; ok {
		return res.body, res.urls, nil
	}
	return "", nil, fmt.Errorf("not found: %s", url)
}

// fetcher is a populated fakeFetcher.
var fetcher = fakeFetcher{
	"http://golang.org/": &fakeResult{
	"The Go Programming Language",
	[]string{
		"http://golang.org/pkg/",
		"http://golang.org/cmd/",
	},
},
"http://golang.org/pkg/": &fakeResult{
"Packages",
[]string{
	"http://golang.org/",
	"http://golang.org/cmd/",
	"http://golang.org/pkg/fmt/",
	"http://golang.org/pkg/os/",
},
	},
	"http://golang.org/pkg/fmt/": &fakeResult{
	"Package fmt",
	[]string{
		"http://golang.org/",
		"http://golang.org/pkg/",
	},
},
"http://golang.org/pkg/os/": &fakeResult{
"Package os",
[]string{
	"http://golang.org/",
	"http://golang.org/pkg/",
},
	},
}
