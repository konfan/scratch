package main
import (
	"fmt"
)



func test(ch chan int){
	for i:= 0; i < 10; i++ {
		ch <- i
	}
	close(ch)
}


func main() {
	c := make(chan int)
	go test(c)
	for i:= range c {
		fmt.Println(i)
	}
}

