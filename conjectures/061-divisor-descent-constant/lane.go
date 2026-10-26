package main

import (
	"fmt"
	"math"
	"os"
	"strconv"
)

func main() {
	N, _ := strconv.Atoi(os.Args[1])
	d := make([]uint16, N+1)
	for i := 1; i <= N; i++ {
		for j := i; j <= N; j += i {
			d[j]++
		}
	}
	// a(x): steps to reach 0
	a := make([]int32, N+1)
	for n := 1; n <= N; n++ {
		a[n] = a[n-int(d[n])] + 1
	}
	// prefix sums of d over all n and over lane n = 2 mod 4
	Fall := make([]float64, N+1)
	Flane := make([]float64, N+1)
	Clane := make([]int32, N+1)
	for n := 1; n <= N; n++ {
		Fall[n] = Fall[n-1] + float64(d[n])
		Flane[n] = Flane[n-1]
		Clane[n] = Clane[n-1]
		if n%4 == 2 {
			Flane[n] += float64(d[n])
			Clane[n]++
		}
	}
	mu := func(F []float64, C []int32, y int, lane bool) float64 {
		w := y / 32
		if w < 64 {
			w = 64
		}
		lo, hi := y-w, y+w
		if lo < 1 {
			lo = 1
		}
		if hi > N {
			hi = N
		}
		if lane {
			return (F[hi] - F[lo-1]) / float64(C[hi]-C[lo-1])
		}
		return (F[hi] - F[lo-1]) / float64(hi-lo+1)
	}
	// renewal predictions: sum over y of 1/mu(y)
	pAll, pLane := 0.0, 0.0
	next := 1000
	fmt.Println("x            a(x)*log(x)/x   a/pred_all   a/pred_lane")
	for y := 2; y <= N; y++ {
		pAll += 1 / mu(Fall, nil, y, false)
		pLane += 1 / mu(Flane, Clane, y, true)
		if y == next || y == N {
			// average over x in (y/2, y] would be smoother; use a(y) and neighbours
			s := 0.0
			for x := y - 999; x <= y; x++ {
				s += float64(a[x])
			}
			ax := s / 1000
			fmt.Printf("%-12d %.5f        %.5f      %.5f\n", y, ax*math.Log(float64(y))/float64(y), ax/pAll, ax/pLane)
			next *= 4
		}
	}
}
