package main
import "fmt"

type Inter struct {
	protocol uint8
	name string
	val	float64
}

func main() {
	fmt.Println("hello")
	b := make([]int, 1)
	fmt.Println(cap(b))
	b = append(b,1,2,3,4,5)
	fmt.Println(b)
	fmt.Println(cap(b))

	s := make(map[int]Inter)
	s[10] = Inter{1,"2",1.5}
	fmt.Println(s[10])
}
