package main

import (
	"fmt"
	"os"
	"strconv"
)

var P = []int{3, 5, 7, 11, 13, 17, 19, 23}

func main() {
	N, _ := strconv.Atoi(os.Args[1])
	d := make([]uint16, N+1)
	for i := 1; i <= N; i++ {
		for j := i; j <= N; j += i {
			d[j]++
		}
	}
	type W struct {
		visits    int
		sumd      float64
		e         [8][3]int
		lane      int
		alld      float64
		alln      int
	}
	var ws []W
	var lo []int
	for y := 1000; y*2 <= N; y *= 2 {
		lo = append(lo, y)
		ws = append(ws, W{})
	}
	idx := func(x int) int {
		for i := len(lo) - 1; i >= 0; i-- {
			if x >= lo[i] && x < 2*lo[i] {
				return i
			}
		}
		return -1
	}
	for x := 1000; x < N; x++ {
		if i := idx(x); i >= 0 {
			ws[i].alld += float64(d[x])
			ws[i].alln++
		}
	}
	for x := N; x > 1; x -= int(d[x]) {
		i := idx(x)
		if i < 0 {
			continue
		}
		w := &ws[i]
		w.visits++
		w.sumd += float64(d[x])
		if x%4 == 2 {
			w.lane++
		}
		for k, p := range P {
			e := 0
			for y := x; y%p == 0; y /= p {
				e++
			}
			if e > 2 {
				e = 2
			}
			w.e[k][e]++
		}
	}
	fmt.Println("window_lo  visits  lane%   R=mean_d_orbit/mean_d_all   prod_L(p<=23)   L3     L5     L7     pi3(0)")
	for i, w := range ws {
		if w.visits < 200 {
			continue
		}
		R := (w.sumd / float64(w.visits)) / (w.alld / float64(w.alln))
		prod := 1.0
		var Ls []float64
		for k, p := range P {
			v := float64(w.visits)
			// E[e+1] with e>=2 bucket approximated by e=2 (small error, p>=3)
			E := (float64(w.e[k][0]) + 2*float64(w.e[k][1]) + 3*float64(w.e[k][2])) / v
			L := (1 - 1/float64(p)) * E
			prod *= L
			Ls = append(Ls, L)
		}
		fmt.Printf("%9d %7d  %5.3f   %8.4f                  %8.4f       %.4f %.4f %.4f  %.4f\n", lo[i], w.visits, float64(w.lane)/float64(w.visits), R, prod, Ls[0], Ls[1], Ls[2], float64(w.e[0][0])/float64(w.visits))
	}
}
