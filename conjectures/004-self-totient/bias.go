// Test of the prime-index bias model for conjecture 004 (Claude, D007).
//
//	go run bias.go -terms 1000000000 -output bias_1e9.json
//	go run bias.go -terms 10000000 -a1 3 -output bias_a1_3.json
//
// Model (H). For a prime index p > a_1 we have a_p = p - 1 exactly (L2), so the
// residues of prime-index terms follow p - 1 (Dirichlet): d | a_p with
// probability 1/phi(d). If all other terms were equidistributed,
//
//	C_d(n) ~ (n - 1 - pi) / d + pi / phi(d),     pi = #{primes p < n},
//
// and by the Moebius formula
//
//	pred(n) = (n - 1 - pi) * phi(n)/n + pi * prod_{q | n} (q - 2)/(q - 1).
//
// Consequences checked here:
//   (a) density of q | a_n  =  1/q + (pi(N)/N) / (q(q-1)) + o(1/log N);
//   (b) composite-index terms alone have q | a_n density 1/q + o(1/log N);
//   (c) the normalized residual (a_n - pred(n)) / (phi(n) pi(n)/n) tends to 0,
//       while the unmodeled residual (a_n - phi(n)) / (phi(n) pi(n)/n) does not.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"math"
	"os"
)

var qs = []int{2, 3, 5, 7, 11, 13}

type qstat struct {
	Q              int     `json:"q"`
	Predicted      float64 `json:"predicted_K_1_over_q_q_minus_1"`
	KAll           float64 `json:"K_all"`            // (density_all - 1/q) / (pi(N)/N)
	KComposite     float64 `json:"K_composite"`      // (density_composite - 1/q) / (pi(N)/N)
	PrimeDensity   float64 `json:"density_among_prime_indices"`
	PrimeExpected  float64 `json:"expected_among_primes_1_over_q_minus_1"`
}

type window struct {
	From, To      int
	Count         int
	ModelMean     float64 `json:"model_residual_mean"`
	ModelRMS      float64 `json:"model_residual_rms"`
	ModelMaxAbs   float64 `json:"model_residual_max_abs"`
	BaseMean      float64 `json:"unmodeled_residual_mean"`
	BaseRMS       float64 `json:"unmodeled_residual_rms"`
	BaseMaxAbs    float64 `json:"unmodeled_residual_max_abs"`
}

type checkpoint struct {
	N        int     `json:"n"`
	PiOverN  float64 `json:"pi_over_n"`
	Q        []qstat `json:"q_stats"`
	Decade   window  `json:"decade"`
}

func main() {
	terms := flag.Int("terms", 100000000, "number of terms")
	a1 := flag.Int("a1", 1, "initial value a_1 (odd)")
	output := flag.String("output", "bias.json", "output JSON")
	flag.Parse()
	N := *terms

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
	size := N + 1
	if *a1 > N {
		size = *a1 + 1
	}
	count := make([]int32, size)
	var pb, divs []int
	addTerm := func(v int) {
		if v <= 0 {
			panic("non-positive term; use an odd a_1")
		}
		if v < len(spf) {
			pb = primesOf(v, pb)
		} else {
			pb = pb[:0]
			x := v
			for p := 2; p*p <= x; p++ {
				if x%p == 0 {
					pb = append(pb, p)
					for x%p == 0 {
						x /= p
					}
				}
			}
			if x > 1 {
				pb = append(pb, x)
			}
		}
		divs = append(divs[:0], 1)
		for _, p := range pb {
			m := len(divs)
			for i := 0; i < m; i++ {
				divs = append(divs, divs[i]*p)
			}
		}
		for _, d := range divs {
			if d < len(count) {
				count[d]++
			}
		}
	}
	addTerm(*a1)

	allDiv := make([]int, len(qs))
	primeDiv := make([]int, len(qs))
	compDiv := make([]int, len(qs))
	primes, composites := 0, 0 // among indices 2..n
	var cps []checkpoint
	next := 1000
	var w window
	var mSum, mSq, bSum, bSq float64
	resetWindow := func(from int) {
		w = window{From: from}
		mSum, mSq, bSum, bSq = 0, 0, 0, 0
	}
	resetWindow(101)

	for n := 2; n <= N; n++ {
		pb = primesOf(n, pb)
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
		phi := n
		g := 1.0
		for _, q := range pb {
			phi = phi / q * (q - 1)
			g *= float64(q-2) / float64(q-1)
		}
		isPrime := int(spf[n]) == n
		v := int(total)

		// residuals, using pi = number of prime indices before n that exceed a_1
		if n > 100 {
			pi := float64(primes)
			pred := (float64(n-1)-pi)*float64(phi)/float64(n) + pi*g
			scale := float64(phi) * pi / float64(n)
			rm := (float64(v) - pred) / scale
			rb := (float64(v) - float64(phi)) / scale
			w.Count++
			mSum += rm
			mSq += rm * rm
			bSum += rb
			bSq += rb * rb
			w.ModelMaxAbs = math.Max(w.ModelMaxAbs, math.Abs(rm))
			w.BaseMaxAbs = math.Max(w.BaseMaxAbs, math.Abs(rb))
		}

		for i, q := range qs {
			if v%q == 0 {
				allDiv[i]++
				if isPrime {
					primeDiv[i]++
				} else {
					compDiv[i]++
				}
			}
		}
		if isPrime {
			if n > *a1 {
				primes++
			}
		} else {
			composites++
		}
		addTerm(v)

		if n == next || n == N {
			m := float64(n - 1)
			piN := float64(primes) / float64(n)
			c := checkpoint{N: n, PiOverN: piN}
			for i, q := range qs {
				fq := 1 / float64(q)
				c.Q = append(c.Q, qstat{
					Q:             q,
					Predicted:     1 / float64(q*(q-1)),
					KAll:          (float64(allDiv[i])/m - fq) / piN,
					KComposite:    (float64(compDiv[i])/float64(composites) - fq) / piN,
					PrimeDensity:  float64(primeDiv[i]) / float64(primes),
					PrimeExpected: 1 / float64(q-1),
				})
			}
			if w.Count > 0 {
				k := float64(w.Count)
				w.To = n
				w.ModelMean, w.ModelRMS = mSum/k, math.Sqrt(mSq/k)
				w.BaseMean, w.BaseRMS = bSum/k, math.Sqrt(bSq/k)
			}
			c.Decade = w
			cps = append(cps, c)
			fmt.Fprintf(os.Stderr, "N=%d pi/N=%.5f | K2 all=%.4f comp=%.4f (pred .5) | K3 all=%.4f comp=%.4f (pred %.4f) | resid model mean=%.3f rms=%.3f max=%.2f ; unmodeled mean=%.3f rms=%.3f\n",
				n, piN, c.Q[0].KAll, c.Q[0].KComposite, c.Q[1].KAll, c.Q[1].KComposite, c.Q[1].Predicted,
				w.ModelMean, w.ModelRMS, w.ModelMaxAbs, w.BaseMean, w.BaseRMS)
			resetWindow(n + 1)
			if n == next {
				next *= 10
			}
			out, _ := json.MarshalIndent(map[string]any{
				"implementation": "bias.go (Claude, D007)",
				"a1":             *a1,
				"terms_so_far":   n,
				"model":          "C_d(n) ~ (n-1-pi)/d + pi/phi(d); pred(n) = (n-1-pi) phi(n)/n + pi prod_{q|n}(q-2)/(q-1)",
				"checkpoints":    cps,
				"scope":          "Finite computation only. K = (density - 1/q)/(pi(N)/N); residuals are normalized by phi(n) pi(n)/n.",
			}, "", "  ")
			if err := os.WriteFile(*output, append(out, '\n'), 0o644); err != nil {
				panic(err)
			}
		}
	}
}
