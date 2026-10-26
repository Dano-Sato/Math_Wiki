// Verification at large N with ~2 bytes/integer: d(n) by a smallest-prime-factor-free divisor sieve,
// lane local means by blocks, and the actual orbit from N. Prints the lane-normalized ratio per window.
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
	// lane block means, block size B
	B := 1 << 14
	nb := N/B + 1
	bs := make([]float64, nb)
	bc := make([]float64, nb)
	for n := 2; n <= N; n += 4 {
		bs[n/B] += float64(d[n])
		bc[n/B]++
	}
	// smoothed lane mean via 2w+1 neighbouring blocks, w ~ (block index)/32
	laneMu := func(y int) float64 {
		b := y / B
		w := b / 32
		if w < 1 {
			w = 1
		}
		lo, hi := b-w, b+w
		if lo < 0 {
			lo = 0
		}
		if hi >= nb {
			hi = nb - 1
		}
		s, c := 0.0, 0.0
		for k := lo; k <= hi; k++ {
			s += bs[k]
			c += bc[k]
		}
		return s / c
	}
	// prediction sum_y 1/mu_lane(y), accumulated per block (mu constant inside a block)
	// and the orbit's visit count, per dyadic window
	fmt.Println("window_lo        visits   lane_frac   a_window/pred_lane   (raw x/log x ratio)")
	type W struct{ lo, hi, vis, lane int }
	var ws []W
	for lo := 1 << 20; lo*2 <= N; lo *= 2 {
		ws = append(ws, W{lo: lo, hi: 2 * lo})
	}
	for x := N; x > 1; x -= int(d[x]) {
		for i := range ws {
			if x >= ws[i].lo && x < ws[i].hi {
				ws[i].vis++
				if x%4 == 2 {
					ws[i].lane++
				}
			}
		}
	}
	for _, w := range ws {
		pred := 0.0
		for b := w.lo / B; b < w.hi/B; b++ {
			pred += float64(B) / laneMu(b*B+B/2)
		}
		raw := float64(w.vis) / (float64(w.hi-w.lo) / math.Log(float64(w.lo)*1.5))
		fmt.Printf("%-14d %9d   %.4f      %.4f               %.4f\n", w.lo, w.vis, float64(w.lane)/float64(w.vis), float64(w.vis)/pred, raw)
	}
}
