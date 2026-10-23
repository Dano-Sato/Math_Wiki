// Computation for conjecture 004 (Claude): the self-referential totient
//
//	a_1 = 1,  a_n = #{ 1 <= k < n : gcd(a_k, n) = 1 }   (n >= 2).
//
// Only the squarefree kernel of n matters, so by inclusion-exclusion
//
//	a_n = sum over squarefree d | n of mu(d) * C(d),   C(d) = #{k < n : d | a_k},
//
// and C is updated by adding 1 to every squarefree divisor of each new term.
//
//	go run selftot.go -terms 100000000 -output experiment.json
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"math"
	"os"
)

func main() {
	terms := flag.Int("terms", 100000000, "number of terms")
	output := flag.String("output", "experiment.json", "output JSON")
	check := flag.Int("check", 3000, "compare with the literal definition up to this n")
	flag.Parse()
	N := *terms

	// smallest prime factor sieve
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
	primesOf := func(x int, buf []int) []int {
		buf = buf[:0]
		for x > 1 {
			p := int(spf[x])
			buf = append(buf, p)
			for x%p == 0 {
				x /= p
			}
		}
		return buf
	}

	// only the first terms are kept; the recurrence needs just the counts C(d)
	keep := max(40, *check)
	a := make([]int32, min(N, keep)+1)
	count := make([]int32, N+1) // C(d) for squarefree d
	var pb, divs []int
	addTerm := func(v int) {
		if v == 0 {
			// 0 is divisible by everything; never happens for n >= 2 (a_n >= 1 since a_1 = 1)
			panic("zero term")
		}
		pb = primesOf(v, pb)
		divs = append(divs[:0], 1)
		for _, p := range pb {
			m := len(divs)
			for i := 0; i < m; i++ {
				divs = append(divs, divs[i]*p)
			}
		}
		for _, d := range divs {
			count[d]++
		}
	}

	a[1] = 1
	addTerm(1)
	// statistics
	type cp struct {
		N             int     `json:"n"`
		MeanRatio     float64 `json:"mean_a_over_n"`
		MeanPhiRatio  float64 `json:"mean_a_over_phi"`
		DensityEven   float64 `json:"density_a_even"`
		Density3      float64 `json:"density_3_divides_a"`
		Density5      float64 `json:"density_5_divides_a"`
		Density7      float64 `json:"density_7_divides_a"`
		MaxOverPhi    float64 `json:"max_a_over_phi"`
		ArgMaxOverPhi int     `json:"argmax_a_over_phi"`
		MinOverPhi    float64 `json:"min_a_over_phi"`
		ArgMinOverPhi int     `json:"argmin_a_over_phi"`
		// over the last decade (n/10, n] only
		WinMax    float64 `json:"decade_max_a_over_phi"`
		WinArgMax int     `json:"decade_argmax"`
		WinMin    float64 `json:"decade_min_a_over_phi"`
		WinArgMin int     `json:"decade_argmin"`
	}
	winMax, winMin := 0.0, math.Inf(1)
	winArgMax, winArgMin := 0, 0
	var cps []cp
	var sumRatio, sumPhi float64
	var even, d3, d5, d7 int
	maxR, minR := 0.0, math.Inf(1)
	argMax, argMin := 0, 0
	next := 10
	prefix := []int32{}
	for n := 2; n <= N; n++ {
		pb = primesOf(n, pb)
		// inclusion-exclusion over squarefree divisors of n
		var total int64
		var rec func(i, d, sign int)
		rec = func(i, d, sign int) {
			if i == len(pb) {
				total += int64(sign) * int64(count[d])
				return
			}
			rec(i+1, d, sign)
			rec(i+1, d*pb[i], -sign)
		}
		rec(0, 1, 1)
		if n < len(a) {
			a[n] = int32(total)
		}
		phi := n
		for _, p := range pb {
			phi = phi / p * (p - 1)
		}
		r := float64(total) / float64(n)
		rp := float64(total) / float64(phi)
		sumRatio += r
		sumPhi += rp
		if rp > maxR {
			maxR, argMax = rp, n
		}
		if n > 2 && rp < minR {
			minR, argMin = rp, n
		}
		if rp > winMax {
			winMax, winArgMax = rp, n
		}
		if n > 2 && rp < winMin {
			winMin, winArgMin = rp, n
		}
		v := int(total)
		if v%2 == 0 {
			even++
		}
		if v%3 == 0 {
			d3++
		}
		if v%5 == 0 {
			d5++
		}
		if v%7 == 0 {
			d7++
		}
		addTerm(v)
		if n == next || n == N {
			m := float64(n - 1)
			cps = append(cps, cp{n, sumRatio / m, sumPhi / m, float64(even) / m, float64(d3) / m, float64(d5) / m, float64(d7) / m, maxR, argMax, minR, argMin,
				winMax, winArgMax, winMin, winArgMin})
			fmt.Fprintf(os.Stderr, "n=%d mean a/n=%.6f mean a/phi=%.6f even=%.5f 3|a=%.5f decade a/phi in [%.4f@%d, %.4f@%d]\n",
				n, sumRatio/m, sumPhi/m, float64(even)/m, float64(d3)/m, winMin, winArgMin, winMax, winArgMax)
			winMax, winMin = 0.0, math.Inf(1)
			if n == next {
				next *= 10
			}
		}
	}
	for i := 1; i <= 40 && i <= N; i++ {
		prefix = append(prefix, a[i])
	}

	// literal check
	gcd := func(x, y int) int {
		for y != 0 {
			x, y = y, x%y
		}
		return x
	}
	lim := min(*check, N)
	lit := []int{0, 1}
	for n := 2; n <= lim; n++ {
		c := 0
		for k := 1; k < n; k++ {
			if gcd(lit[k], n) == 1 {
				c++
			}
		}
		lit = append(lit, c)
	}
	match := true
	for n := 1; n <= lim; n++ {
		if int(a[n]) != lit[n] {
			match = false
		}
	}
	if !match {
		panic("fast and literal computations disagree")
	}

	out, _ := json.MarshalIndent(map[string]any{
		"implementation":         "selftot.go (Claude)",
		"terms":                  N,
		"prefix_40":              prefix,
		"literal_check_terms":    lim,
		"matches_literal":        match,
		"checkpoints":            cps,
		"scope":                  "Finite computation only.",
	}, "", "  ")
	if err := os.WriteFile(*output, append(out, '\n'), 0o644); err != nil {
		panic(err)
	}
}
