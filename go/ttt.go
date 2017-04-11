package main

import (
	"bufio"
	"fmt"
	"golang.org/x/crypto/ssh"
	"io"
)

type Inter struct {
	protocol uint8
	name     string
	val      float64
}

func main() {
	fmt.Println("hello")
	b := make([]int, 1)
	fmt.Println(cap(b))
	b = append(b, 1, 2, 3, 4, 5)
	fmt.Println(b)
	fmt.Println(cap(b))

	s := make(map[int]Inter)
	s[10] = Inter{1, "2", 1.5}
	fmt.Println(s[10])

	config := &ssh.ClientConfig{
		User: "root",
		Auth: []ssh.AuthMethod{
			ssh.Password("daemon.datatom"),
		},
	}

	client, err := ssh.Dial("tcp", "192.168.1.7:22", config)
	if err != nil {
		panic(err.Error())
	}
	session, err := client.NewSession()
	if err != nil {
		panic(err.Error())
	}
	defer session.Close()

	//l, _ := session.Output("ls")

	//fmt.Println(string(l[:]))

	r, err := session.StdoutPipe()
	if err != nil {
		panic(err.Error())
	}
	session.Start("netstat -anop")

	reader := bufio.NewReader(r)
	for ls, err := reader.ReadString('\n'); err != io.EOF;ls, err = reader.ReadString('\n') {
        if err != nil {
            err = nil
        }
		fmt.Println(ls)
	}

	session.Wait()
}
