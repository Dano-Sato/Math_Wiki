package main

import (
	"fmt"
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
	lo := N / 8
	// lane distribution of d(m), m = n/2 odd, in [lo, N]
	K := 64
	lane := make([]float64, K+1)
	orb := make([]float64, K+1)
	nl, no := 0.0, 0.0
	for n := lo; n <= N; n++ {
		if n%4 == 2 {
			k := int(d[n/2])
			if k > K {
				k = K
			}
			lane[k]++
			nl++
		}
	}
	// orbit: transitions conditioned on d(m) of current point
	var trans [65][65]float64
	prev := -1
	for x := N; x >= lo; x -= int(d[x]) {
		if x%4 != 2 {
			prev = -1
			continue
		}
		k := int(d[x/2])
		if k > K {
			k = K
		}
		orb[k]++
		no++
		if prev >= 0 {
			trans[prev][k]++
		}
		prev = k
	}
	fmt.Println("d(m)  lane_frac  orbit_frac  ratio")
	for k := 2; k <= 16; k += 2 {
		fmt.Printf("%4d  %.5f    %.5f     %.3f\n", k, lane[k]/nl, orb[k]/no, (orb[k]/no)/(lane[k]/nl))
	}
	fmt.Println("P(next d(m)=2 | current d(m)=k) vs lane frac of d=2:", fmt.Sprintf("%.4f", lane[2]/nl))
	for k := 2; k <= 12; k += 2 {
		row := 0.0
		for j := 0; j <= K; j++ {
			row += trans[k][j]
		}
		fmt.Printf("  k=%2d: %.4f\n", k, trans[k][2]/row)
	}
}
