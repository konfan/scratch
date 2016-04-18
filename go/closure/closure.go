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

func main () {
	x := add()
	for i:=0; i<=100; i++ {
		fmt.Println(x(i))
	}
}
