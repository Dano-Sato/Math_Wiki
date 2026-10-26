// Predict the orbit's visit bias from ancestor counts only: w_k(y) = number of depth-k preimages of y
// under T(n) = n - d(n). Compare d-weighted means with the actual trunk orbit in the same window.
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
	lo, hi := N/16, N/4 // window well below the top so ancestors are not truncated
	// lane mean of d in window
	sl, cl := 0.0, 0.0
	for y := lo; y <= hi; y++ {
		if y%4 == 2 {
			sl += float64(d[y])
			cl++
		}
	}
	laneMean := sl / cl
	// actual orbit from N
	so, co := 0.0, 0.0
	for x := N; x > lo; x -= int(d[x]) {
		if x <= hi && x%4 == 2 {
			so += float64(d[x])
			co++
		}
	}
	fmt.Printf("window [%d,%d]  orbit mean d / lane mean d = %.4f  (=> c_lane = %.4f)\n", lo, hi, so/co/laneMean, laneMean*co/so)
	w := make([]float32, N+1)
	nw := make([]float32, N+1)
	for i := range w {
		w[i] = 1
	}
	for k := 1; k <= 40; k++ {
		for i := range nw {
			nw[i] = 0
		}
		for n := N; n >= 1; n-- {
			nw[n-int(d[n])] += w[n]
		}
		// normalise to avoid overflow
		s := 0.0
		for y := lo; y <= hi; y++ {
			s += float64(nw[y])
		}
		scale := float32(float64(hi-lo+1) / s)
		for i := range nw {
			nw[i] *= scale
		}
		w, nw = nw, w
		if k <= 3 || k%5 == 0 {
			sw, swd := 0.0, 0.0
			for y := lo; y <= hi; y++ {
				if y%4 == 2 {
					sw += float64(w[y])
					swd += float64(w[y]) * float64(d[y])
				}
			}
			fmt.Printf("depth %2d: weighted mean d / lane mean d = %.4f  (=> c_lane = %.4f)\n", k, swd/sw/laneMean, laneMean*sw/swd)
		}
	}
}
