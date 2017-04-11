package main

import "fmt"

type ErrorNegative float64

func (e ErrorNegative) String() string {
	return ""
}

func (e ErrorNegative) Error() string {
	return ""
}

func check1(val interface{}) {
	switch val.(type) {
	case fmt.Stringer:
		fmt.Println("Stringer")
	case error:
		fmt.Println("error")
	}
}

func check2(val interface{}) {
	switch val.(type) {
	case error:
		fmt.Println("error")
	case fmt.Stringer:
		fmt.Println("Stringer")
	}
}

func main() {
	var v ErrorNegative
	check1(v)
	fmt.Println("---------------")
	check2(v)
}
