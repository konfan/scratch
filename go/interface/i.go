package main
import "fmt"


type Self struct {
	a int
	b int
}

func (v Self) String() string {
	return fmt.Sprintf("%d,%d", v.a +1, v.b*10)
}

func main() {
	var i interface{} = "hhh"
	f, ok := i.(Self)
	fmt.Println(f,ok)
	s, ok := i.(string)
	fmt.Println(s,ok)

	sv := Self{2,3}
	fmt.Println(sv)
}
