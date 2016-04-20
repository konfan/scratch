package main
import (
	"fmt"
)

func add() func(int) int {
	sum := 0
	return func(x int) int {
		sum += x
		return sum
	}
}

func fibonacci() func() int {
	prev, cur := 0,1
	return func() int {
		t := prev
		prev, cur = cur, prev + cur
		return t
	}
}

func main () {
	//x := add()
	f := fibonacci()
	for i:=0; i<=10; i++ {
		fmt.Println(f())
	}
}
