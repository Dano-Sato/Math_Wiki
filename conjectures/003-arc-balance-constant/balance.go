// Computation for conjecture 003 (Claude): circular arrangements of a set
// in which every arc-sum range is at most max - min.
//
//	go run balance.go -output experiment.json
//
// "exact" rows exhaust all arrangements (rotation and reflection removed), so
// found=false there is a finite proof. "anneal" rows are heuristic: a found
// witness is re-checked from the definition; a failure proves nothing.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"math/rand"
	"os"
	"sort"
	"strconv"
	"strings"
	"time"
)

// worst returns max over k=1..n-1 of (max - min) of circular k-arc sums.
func worst(p []int64) int64 {
	n := len(p)
	var w int64
	for k := 1; k < n; k++ {
		var s int64
		for i := 0; i < k; i++ {
			s += p[i]
		}
		lo, hi := s, s
		for i := 1; i < n; i++ {
			s += p[(i+k-1)%n] - p[i-1]
			lo, hi = min(lo, s), max(hi, s)
		}
		w = max(w, hi-lo)
	}
	return w
}

// exact searches for an arrangement with worst(p) <= bound.
// p[0] is fixed to the smallest value (rotation) and p[1] < p[n-1] (reflection).
func exact(vals []int64, bound int64) ([]int64, int64) {
	n := len(vals)
	path := []int64{vals[0]}
	prefix := []int64{0, vals[0]} // prefix[m] = sum of path[:m]
	used := make([]bool, n)
	used[0] = true
	lo := make([]int64, n)
	hi := make([]int64, n)
	for k := range lo {
		lo[k], hi[k] = 1<<62, -(1 << 62)
	}
	lo[1], hi[1] = vals[0], vals[0]
	var nodes int64
	var visit func() bool
	visit = func() bool {
		nodes++
		m := len(path)
		if m == n {
			if path[1] > path[n-1] {
				return false
			}
			return worst(path) <= bound
		}
		for j := 1; j < n; j++ {
			if used[j] || (j > 1 && vals[j] == vals[j-1] && !used[j-1]) {
				continue
			}
			v := vals[j]
			total := prefix[m] + v
			// new linear arcs ending at the new element, lengths 1..m+1
			saveLo := make([]int64, 0, m+1)
			saveHi := make([]int64, 0, m+1)
			ok := true
			for k := 1; k <= m+1 && k < n; k++ {
				s := total - prefix[m+1-k]
				saveLo, saveHi = append(saveLo, lo[k]), append(saveHi, hi[k])
				lo[k], hi[k] = min(lo[k], s), max(hi[k], s)
				if hi[k]-lo[k] > bound {
					ok = false
					break
				}
			}
			if ok {
				used[j] = true
				path = append(path, v)
				prefix = append(prefix, total)
				if visit() {
					return true
				}
				path, prefix = path[:m], prefix[:m+1]
				used[j] = false
			}
			for k := len(saveLo); k >= 1; k-- {
				lo[k], hi[k] = saveLo[k-1], saveHi[k-1]
			}
		}
		return false
	}
	if visit() {
		return path, nodes
	}
	return nil, nodes
}

func anneal(vals []int64, bound int64, rng *rand.Rand, limit time.Duration) ([]int64, int) {
	n := len(vals)
	deadline := time.Now().Add(limit)
	restarts := 0
	for time.Now().Before(deadline) {
		restarts++
		p := append([]int64(nil), vals...)
		rng.Shuffle(n, func(i, j int) { p[i], p[j] = p[j], p[i] })
		e := worst(p)
		steps := 400000
		scale := float64(bound) / 8
		for s := 0; s < steps; s++ {
			i, j := rng.Intn(n), rng.Intn(n)
			if i == j {
				continue
			}
			p[i], p[j] = p[j], p[i]
			ne := worst(p)
			temp := scale * (1 - float64(s)/float64(steps)) * (1 - float64(s)/float64(steps))
			if ne <= e || (temp > 0 && rng.Float64() < expNeg(float64(ne-e)/temp)) {
				e = ne
				if e <= bound {
					return p, restarts
				}
			} else {
				p[i], p[j] = p[j], p[i]
			}
			if s&4095 == 0 && time.Now().After(deadline) {
				break
			}
		}
	}
	return nil, restarts
}

func expNeg(x float64) float64 {
	// exp(-x) without importing math for one call site
	if x > 50 {
		return 0
	}
	r, term := 1.0, 1.0
	for i := 1; i < 60; i++ {
		term *= -x / float64(i)
		r += term
	}
	if r < 0 {
		return 0
	}
	return r
}

type row struct {
	Family  string  `json:"family"`
	N       int     `json:"n"`
	Method  string  `json:"method"`
	Values  []int64 `json:"values"`
	Bound   int64   `json:"bound_max_minus_min"`
	Found   bool    `json:"found"`
	Worst   int64   `json:"witness_worst,omitempty"`
	Witness []int64 `json:"witness,omitempty"`
	Nodes   int64   `json:"nodes,omitempty"`
	Seconds float64 `json:"seconds"`
}

func powers(n, e int) []int64 {
	v := make([]int64, n)
	for i := range v {
		x := int64(i + 1)
		v[i] = 1
		for k := 0; k < e; k++ {
			v[i] *= x
		}
	}
	return v
}

func convex(n int, rng *rand.Rand) []int64 {
	gaps := make([]int64, n-1)
	for i := range gaps {
		gaps[i] = 1 + rng.Int63n(1000)
	}
	sort.Slice(gaps, func(i, j int) bool { return gaps[i] < gaps[j] })
	v := []int64{0}
	for _, g := range gaps {
		v = append(v, v[len(v)-1]+g)
	}
	return v
}

func main() {
	output := flag.String("output", "experiment.json", "output JSON")
	exactMax := flag.Int("exact-max", 12, "largest n for exhaustive search")
	annealMax := flag.Int("anneal-max", 40, "largest n for heuristic search")
	limit := flag.Duration("limit", 20*time.Second, "time limit per heuristic instance")
	set := flag.String("set", "", "check one comma-separated set exactly and exit")
	optimum := flag.Bool("optimum", false, "with -set: print the exact optimum min max_k R_k")
	flag.Parse()
	if *set != "" {
		var vals []int64
		for _, f := range strings.Split(*set, ",") {
			x, err := strconv.ParseInt(strings.TrimSpace(f), 10, 64)
			if err != nil {
				panic(err)
			}
			vals = append(vals, x)
		}
		sort.Slice(vals, func(i, j int) bool { return vals[i] < vals[j] })
		if *optimum {
			// binary search; the Steinitz-type lemma L1 gives 2(max-min) as an upper bound
			lo, hi := vals[len(vals)-1]-vals[0], 2*(vals[len(vals)-1]-vals[0])
			for lo < hi {
				mid := (lo + hi) / 2
				if w, _ := exact(vals, mid); w != nil {
					hi = mid
				} else {
					lo = mid + 1
				}
			}
			fmt.Printf("optimum=%d range=%d\n", lo, vals[len(vals)-1]-vals[0])
			return
		}
		w, nodes := exact(vals, vals[len(vals)-1]-vals[0])
		fmt.Printf("set=%v bound=%d found=%v witness=%v nodes=%d\n", vals, vals[len(vals)-1]-vals[0], w != nil, w, nodes)
		return
	}
	rng := rand.New(rand.NewSource(20261023))
	var rows []row
	add := func(family string, vals []int64, n int) {
		bound := vals[len(vals)-1] - vals[0]
		start := time.Now()
		r := row{Family: family, N: n, Values: vals, Bound: bound}
		if n <= *exactMax {
			w, nodes := exact(vals, bound)
			r.Method, r.Nodes = "exact", nodes
			if w != nil {
				r.Found, r.Witness = true, w
			}
		} else {
			w, _ := anneal(vals, bound, rng, *limit)
			r.Method = "anneal"
			if w != nil {
				r.Found, r.Witness = true, w
			}
		}
		if r.Found {
			r.Worst = worst(r.Witness)
			if r.Worst > bound {
				panic("witness check failed")
			}
		}
		r.Seconds = time.Since(start).Seconds()
		fmt.Fprintf(os.Stderr, "%-8s n=%2d %-6s found=%v %.1fs\n", family, n, r.Method, r.Found, r.Seconds)
		rows = append(rows, r)
		out, _ := json.MarshalIndent(map[string]any{
			"implementation": "balance.go (Claude)",
			"rows":           rows,
			"scope":          "exact rows are finite proofs; anneal rows with found=false prove nothing.",
		}, "", "  ")
		if err := os.WriteFile(*output, append(out, '\n'), 0o644); err != nil {
			panic(err)
		}
	}
	for n := 3; n <= *annealMax; n++ {
		if n > *exactMax && n%5 != 0 && n != 13 && n != 16 {
			continue
		}
		add("squares", powers(n, 2), n)
		add("cubes", powers(n, 3), n)
		add("convex", convex(n, rng), n)
	}
}
