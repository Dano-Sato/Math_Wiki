// Independent implementation (Claude, D004) of the alternating coprime greedy
// sequence. Written from the definition, not from verify.py.
//
//	go run explore.go -terms 100000000 -output explore_1e8.json
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
)

func gcd(a, b uint64) uint64 {
	for b != 0 {
		a, b = b, a%b
	}
	return a
}

func factor(n uint64) [][2]uint64 {
	var out [][2]uint64
	for p := uint64(2); p*p <= n; p++ {
		if n%p == 0 {
			e := uint64(0)
			for n%p == 0 {
				n /= p
				e++
			}
			out = append(out, [2]uint64{p, e})
		}
	}
	if n > 1 {
		out = append(out, [2]uint64{n, 1})
	}
	return out
}

// literal follows the definition word for word: scan m = 1, 2, 3, ...
func literal(count int) []uint64 {
	seq := []uint64{1, 2}
	used := map[uint64]bool{1: true, 2: true}
	for len(seq) < count {
		n := uint64(len(seq) + 1)
		s := seq[len(seq)-1] + seq[len(seq)-2]
		m := uint64(1)
		for used[m] || m%2 != n%2 || gcd(m, s) != 1 {
			m++
		}
		seq = append(seq, m)
		used[m] = true
	}
	return seq
}

type record struct {
	Index        uint64      `json:"index"`
	Value        uint64      `json:"value"`
	Displacement int64       `json:"displacement"`
	Factors      [][2]uint64 `json:"factors"`
}

type checkpoint struct {
	Terms          uint64 `json:"terms"`
	MaxValue       uint64 `json:"maximum_value"`
	CoveredThrough uint64 `json:"covered_through"`
	MaxAhead       int64  `json:"max_ahead"`  // max a_n - n
	MaxBehind      int64  `json:"max_behind"` // max n - a_n
}

func main() {
	terms := flag.Uint64("terms", 100000000, "number of terms")
	output := flag.String("output", "explore.json", "output JSON path")
	flag.Parse()
	N := *terms

	size := N + N/4 + 1024
	used := make([]uint64, size/64+1)
	isUsed := func(m uint64) bool { return used[m>>6]>>(m&63)&1 == 1 }
	mark := func(m uint64) { used[m>>6] |= 1 << (m & 63) }

	first := make([]uint64, 0, 30)
	litN := uint64(20000)
	if litN > N {
		litN = N
	}
	prefix := make([]uint64, 0, litN)

	// p | S_n counts for small odd primes, split by parity of n.
	primes := []uint64{3, 5, 7, 11, 13}
	divCount := map[string][]uint64{"odd": make([]uint64, len(primes)), "even": make([]uint64, len(primes))}
	turns := map[string]uint64{}
	// how many candidates were rejected by gcd before the chosen one
	var rejectHist [64]uint64
	// L5 pivot statistics: t = 2a_n - S_n, pivot = (S±1)/2 with parity n
	tHist := map[int64]uint64{}
	var pivotUsed, pivotChosen uint64
	// C1 events: R_Q | S_n for odd primorials R_Q
	type c1 struct {
		Q, R, Events, PivotUsed uint64
		MaxLocal              int64 // max(|e_n|,|e_{n-1}|,|e_{n-2}|) over events with pivot used
	}
	c1s := []*c1{{Q: 13, R: 15015}, {Q: 17, R: 255255}, {Q: 19, R: 4849845}, {Q: 23, R: 111546435}}
	var e1, e2 int64 // e_{n-1}, e_{n-2}
	abs := func(x int64) int64 {
		if x < 0 {
			return -x
		}
		return x
	}

	var aheadRecs, behindRecs []record
	var cps []checkpoint
	var maxAhead, maxBehind int64
	var maxVal uint64
	least := [2]uint64{4, 3} // least unused even, odd
	next := uint64(10)
	p1, p2 := uint64(1), uint64(2)
	mark(1)
	mark(2)
	first = append(first, 1, 2)
	prefix = append(prefix, 1, 2)

	for n := uint64(3); n <= N; n++ {
		par := n & 1
		s := p1 + p2
		key := "even"
		if par == 1 {
			key = "odd"
		}
		turns[key]++
		for i, p := range primes {
			if s%p == 0 {
				divCount[key][i]++
			}
		}
		m := least[par]
		rej := 0
		for isUsed(m) || gcd(m, s) != 1 {
			if !isUsed(m) {
				rej++
			}
			m += 2
		}
		if rej > 63 {
			rej = 63
		}
		rejectHist[rej]++
		pivot := (s + 1) / 2
		if pivot&1 != par {
			pivot = (s - 1) / 2
		}
		pu := isUsed(pivot)
		if pu {
			pivotUsed++
		}
		if m == pivot {
			pivotChosen++
		}
		tHist[int64(2*m)-int64(s)]++
		d0 := int64(m) - int64(n)
		for _, c := range c1s {
			if s%c.R == 0 {
				c.Events++
				if pu {
					c.PivotUsed++
					loc := max(abs(d0), abs(e1), abs(e2))
					if loc > c.MaxLocal {
						c.MaxLocal = loc
					}
				}
			}
		}
		e1, e2 = d0, e1
		mark(m)
		for isUsed(least[par]) {
			least[par] += 2
		}
		p1, p2 = p2, m
		if m > maxVal {
			maxVal = m
		}
		d := int64(m) - int64(n)
		if d > maxAhead {
			maxAhead = d
			aheadRecs = append(aheadRecs, record{n, m, d, factor(m)})
		}
		if -d > maxBehind {
			maxBehind = -d
			behindRecs = append(behindRecs, record{n, m, d, factor(m)})
		}
		if len(first) < 30 {
			first = append(first, m)
		}
		if n <= litN {
			prefix = append(prefix, m)
		}
		if n == next || n == N {
			cov := least[0]
			if least[1] < cov {
				cov = least[1]
			}
			cps = append(cps, checkpoint{n, maxVal, cov - 1, maxAhead, maxBehind})
			fmt.Fprintf(os.Stderr, "%d terms: ahead %d behind %d\n", n, maxAhead, maxBehind)
			if n == next {
				next *= 10
			}
		}
	}

	lit := literal(int(litN))
	match := len(lit) == len(prefix)
	for i := range lit {
		if !match || lit[i] != prefix[i] {
			match = false
			break
		}
	}

	ratio := map[string][]float64{}
	for k, v := range divCount {
		r := make([]float64, len(v))
		for i := range v {
			r[i] = float64(v[i]) / float64(turns[k])
		}
		ratio[k] = r
	}

	out := map[string]any{
		"implementation":          "explore.go (Claude, independent of verify.py)",
		"terms":                   N,
		"prefix_30":               first,
		"matches_literal_prefix":  match,
		"literal_prefix_terms":    litN,
		"checkpoints":             cps,
		"ahead_records":           aheadRecs,
		"behind_records":          behindRecs,
		"small_primes":            primes,
		"fraction_p_divides_S":    ratio,
		"gcd_rejections_histogram": rejectHist[:],
		"pivot_used_fraction":     float64(pivotUsed) / float64(N-2),
		"pivot_chosen_fraction":   float64(pivotChosen) / float64(N-2),
		"t_histogram":             tHist,
		"c1_events":               c1s,
		"scope":                   "Finite computation only.",
	}
	b, _ := json.MarshalIndent(out, "", "  ")
	if err := os.WriteFile(*output, append(b, '\n'), 0o644); err != nil {
		panic(err)
	}
}
