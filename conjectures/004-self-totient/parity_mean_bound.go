// 004 L18 검산: 홀수 값 개수 O(N)과 B(N)=sum phi(a_k)/a_k, 짝수·홀수 값별 평균.
//
//	go run parity_mean_bound.go 30000000 [a_n 이진 출력 경로]
//
// 두 번째 인자를 주면 a_0..a_N을 uint32 little-endian으로 저장한다(parity_correlations.py 입력).
package main

import (
	"fmt"
	"os"
	"strconv"
)

func main() {
	N, _ := strconv.Atoi(os.Args[1])
	spf := make([]int32, N+1)
	for i := 2; i <= N; i++ {
		if spf[i] == 0 {
			for j := i; j <= N; j += i {
				if spf[j] == 0 {
					spf[j] = int32(i)
				}
			}
		}
	}
	phi := make([]int32, N+1)
	phi[1] = 1
	for i := 2; i <= N; i++ {
		p := int(spf[i]); m := i / p
		if m%p == 0 { phi[i] = phi[m] * int32(p) } else { phi[i] = phi[m] * int32(p-1) }
	}
	C := make([]int32, N+1)
	a := make([]int32, N+1)
	var divs [1024]int
	var mus [1024]int
	sqd := func(x int) int { // squarefree divisors of x with mobius signs
		cnt := 1; divs[0] = 1; mus[0] = 1
		for x > 1 {
			p := int(spf[x])
			for x%p == 0 { x /= p }
			for i := 0; i < cnt; i++ { divs[cnt+i] = divs[i] * p; mus[cnt+i] = -mus[i] }
			cnt *= 2
		}
		return cnt
	}
	O := 0
	B, Be, Bo := 0.0, 0.0, 0.0
	next := 1000
	for n := 1; n <= N; n++ {
		var v int
		if n == 1 { v = 1 } else {
			c := sqd(n); s := 0
			for i := 0; i < c; i++ { s += mus[i] * int(C[divs[i]]) }
			v = s
		}
		a[n] = int32(v)
		c := sqd(v)
		for i := 0; i < c; i++ { C[divs[i]]++ }
		b := float64(phi[v]) / float64(v)
		B += b
		if v%2 == 1 { O++; Bo += b } else { Be += b }
		if n == next || n == N {
			fmt.Printf("%d O/N=%.6f B/N=%.6f avgb_even=%.6f avgb_odd=%.6f bound(1/2+O/2N)=%.6f\n", n, float64(O)/float64(n), B/float64(n), Be/float64(n-O), Bo/float64(O), 0.5+0.5*float64(O)/float64(n))
			next *= 10
		}
	}
	if len(os.Args) < 3 {
		return
	}
	f, _ := os.Create(os.Args[2])
	buf := make([]byte, 4*(N+1))
	for i := 0; i <= N; i++ { x := uint32(a[i]); buf[4*i] = byte(x); buf[4*i+1] = byte(x >> 8); buf[4*i+2] = byte(x >> 16); buf[4*i+3] = byte(x >> 24) }
	f.Write(buf); f.Close()
}
