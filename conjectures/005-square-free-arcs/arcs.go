// Computation for conjecture 005 (Claude): circles of 1..n in which no run of
// two or more (and fewer than n) consecutive numbers sums to a perfect square.
//
//	go run arcs.go -max 60 -output experiment.json
//
// L1 (the forced obstruction): the n runs of length n-1 have sums T-1,...,T-n,
// T = n(n+1)/2, so a square in [n(n-1)/2, n(n+1)/2) makes n impossible.
// For the other n we look for a witness by randomized depth-first search with
// restarts. A witness is re-checked from the definition; "not found" proves nothing,
// except in -exact mode, where the search is exhaustive (p_1 = 1, p_2 < p_n).
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"math"
	"math/rand"
	"os"
	"time"
)

func isSquare(x int) bool {
	r := int(math.Sqrt(float64(x)))
	for r*r > x {
		r--
	}
	for (r+1)*(r+1) <= x {
		r++
	}
	return r*r == x
}

// forced reports whether some square lies in [n(n-1)/2, n(n+1)/2).
func forced(n int) bool {
	for x := n * (n - 1) / 2; x < n*(n+1)/2; x++ {
		if isSquare(x) {
			return true
		}
	}
	return false
}

// check verifies a full circle from the definition.
func check(p []int) bool {
	n := len(p)
	for i := 0; i < n; i++ {
		s := p[i]
		for L := 2; L < n; L++ {
			s += p[(i+L-1)%n]
			if isSquare(s) {
				return false
			}
		}
	}
	return true
}

type searcher struct {
	n       int
	path    []int
	prefix  []int // prefix[m] = sum of path[:m]
	used    []bool
	nodes   int64
	limit   int64
	rng     *rand.Rand
	order   []int
	exact   bool
	stopped bool
}

// fits checks the linear runs ending at the new value v (lengths 2..len+1, < n).
func (s *searcher) fits(v int) bool {
	m := len(s.path)
	total := s.prefix[m] + v
	for L := 2; L <= m+1 && L < s.n; L++ {
		if isSquare(total - s.prefix[m+1-L]) {
			return false
		}
	}
	return true
}

func (s *searcher) dfs() bool {
	s.nodes++
	if s.limit > 0 && s.nodes > s.limit {
		s.stopped = true
		return false
	}
	m := len(s.path)
	if m == s.n {
		if s.exact && s.path[1] > s.path[s.n-1] {
			return false
		}
		return check(s.path)
	}
	cand := make([]int, 0, s.n)
	for _, v := range s.order {
		if !s.used[v] {
			cand = append(cand, v)
		}
	}
	if !s.exact {
		s.rng.Shuffle(len(cand), func(i, j int) { cand[i], cand[j] = cand[j], cand[i] })
	}
	for _, v := range cand {
		if !s.fits(v) {
			continue
		}
		s.used[v] = true
		s.path = append(s.path, v)
		s.prefix = append(s.prefix, s.prefix[m]+v)
		if s.dfs() {
			return true
		}
		if s.stopped {
			return false
		}
		s.path, s.prefix = s.path[:m], s.prefix[:m+1]
		s.used[v] = false
	}
	return false
}

func newSearcher(n int, rng *rand.Rand, exact bool, limit int64) *searcher {
	s := &searcher{n: n, used: make([]bool, n+1), rng: rng, exact: exact, limit: limit}
	for v := 1; v <= n; v++ {
		s.order = append(s.order, v)
	}
	first := 1
	if !exact {
		first = 1 + rng.Intn(n)
	}
	s.path = []int{first}
	s.prefix = []int{0, first}
	s.used[first] = true
	return s
}

// badArcs counts runs of length 2..n-1 whose sum is a square.
func badArcs(p []int, sq []bool) int {
	n := len(p)
	bad := 0
	for i := 0; i < n; i++ {
		s := p[i]
		for L := 2; L < n; L++ {
			s += p[(i+L-1)%n]
			if sq[s] {
				bad++
			}
		}
	}
	return bad
}

// anneal minimizes the number of square runs with random transpositions.
func anneal(n int, rng *rand.Rand, deadline time.Time) ([]int, int) {
	total := n * (n + 1) / 2
	sq := make([]bool, total+1)
	for r := 1; r*r <= total; r++ {
		sq[r*r] = true
	}
	restarts := 0
	for time.Now().Before(deadline) {
		restarts++
		p := rng.Perm(n)
		for i := range p {
			p[i]++
		}
		e := badArcs(p, sq)
		const steps = 300000
		for s := 0; s < steps && e > 0; s++ {
			i, j := rng.Intn(n), rng.Intn(n)
			if i == j {
				continue
			}
			p[i], p[j] = p[j], p[i]
			ne := badArcs(p, sq)
			t := 1.5 * (1 - float64(s)/steps)
			if ne <= e || (t > 0.02 && rng.Float64() < math.Exp(float64(e-ne)/t)) {
				e = ne
			} else {
				p[i], p[j] = p[j], p[i]
			}
			if s&1023 == 0 && time.Now().After(deadline) {
				break
			}
		}
		if e == 0 {
			return p, restarts
		}
	}
	return nil, restarts
}

// ---- row (line) version: runs of length 2..n, including the whole row ----

func badRuns(p []int, sq []bool) int {
	bad := 0
	for i := range p {
		s := p[i]
		for j := i + 1; j < len(p); j++ {
			s += p[j]
			if sq[s] {
				bad++
			}
		}
	}
	return bad
}

func squares(limit int) []bool {
	sq := make([]bool, limit+1)
	for r := 1; r*r <= limit; r++ {
		sq[r*r] = true
	}
	return sq
}

// rowExact exhausts all rows of 1..n up to reversal (p_1 < p_n).
func rowExact(n int) ([]int, int64) {
	sq := squares(n * (n + 1) / 2)
	path := []int{}
	prefix := []int{0}
	used := make([]bool, n+1)
	var nodes int64
	var dfs func() bool
	dfs = func() bool {
		nodes++
		m := len(path)
		if m == n {
			return path[0] < path[n-1] || n == 1
		}
		for v := 1; v <= n; v++ {
			if used[v] {
				continue
			}
			total := prefix[m] + v
			ok := true
			for L := 2; L <= m+1; L++ {
				if sq[total-prefix[m+1-L]] {
					ok = false
					break
				}
			}
			if !ok {
				continue
			}
			used[v] = true
			path = append(path, v)
			prefix = append(prefix, total)
			if dfs() {
				return true
			}
			path, prefix = path[:m], prefix[:m+1]
			used[v] = false
		}
		return false
	}
	if dfs() {
		return path, nodes
	}
	return nil, nodes
}

func rowAnneal(n int, rng *rand.Rand, deadline time.Time) ([]int, int) {
	sq := squares(n * (n + 1) / 2)
	restarts := 0
	for time.Now().Before(deadline) {
		restarts++
		p := rng.Perm(n)
		for i := range p {
			p[i]++
		}
		e := badRuns(p, sq)
		const steps = 300000
		for s := 0; s < steps && e > 0; s++ {
			i, j := rng.Intn(n), rng.Intn(n)
			if i == j {
				continue
			}
			p[i], p[j] = p[j], p[i]
			ne := badRuns(p, sq)
			t := 1.5 * (1 - float64(s)/steps)
			if ne <= e || (t > 0.02 && rng.Float64() < math.Exp(float64(e-ne)/t)) {
				e = ne
			} else {
				p[i], p[j] = p[j], p[i]
			}
			if s&1023 == 0 && time.Now().After(deadline) {
				break
			}
		}
		if e == 0 {
			return p, restarts
		}
	}
	return nil, restarts
}

type row struct {
	N        int    `json:"n"`
	Forced   bool   `json:"forced_obstruction"`
	Status   string `json:"status"`
	Witness  []int  `json:"witness,omitempty"`
	Restarts int    `json:"restarts,omitempty"`
	Nodes    int64  `json:"nodes,omitempty"`
	Seconds  float64 `json:"seconds"`
}

func main() {
	maxN := flag.Int("max", 60, "largest n")
	exactMax := flag.Int("exact-max", 14, "exhaustive search up to this n (for all n, as a check on L1)")
	limit := flag.Duration("limit", 30*time.Second, "time limit per n for the randomized search")
	output := flag.String("output", "experiment.json", "output JSON")
	rowMode := flag.Bool("row", false, "line version: runs of length 2..n, obstruction = T_n square")
	flag.Parse()
	rng := rand.New(rand.NewSource(20261024))
	var rows []row
	if *rowMode {
		for n := 2; n <= *maxN; n++ {
			start := time.Now()
			T := n * (n + 1) / 2
			r := row{N: n, Forced: isSquare(T)}
			if n <= *exactMax {
				w, nodes := rowExact(n)
				r.Nodes = nodes
				if w != nil {
					r.Status, r.Witness = "possible", w
				} else {
					r.Status = "impossible (exhaustive)"
				}
			} else if r.Forced {
				r.Status = "impossible (T_n square)"
			} else if w, k := rowAnneal(n, rng, time.Now().Add(*limit)); w != nil {
				r.Status, r.Witness, r.Restarts = "possible", w, k
			} else {
				r.Status = "not found (heuristic)"
			}
			if r.Witness != nil && badRuns(r.Witness, squares(T)) != 0 {
				panic("row witness check failed")
			}
			r.Seconds = time.Since(start).Seconds()
			fmt.Fprintf(os.Stderr, "row n=%2d Tsquare=%-5v %s %.1fs\n", n, r.Forced, r.Status, r.Seconds)
			rows = append(rows, r)
		}
		out, _ := json.MarshalIndent(map[string]any{
			"implementation": "arcs.go -row (Claude)",
			"rows":           rows,
			"scope":          "possible = checked witness; impossible = proof; not found (heuristic) = no conclusion.",
		}, "", "  ")
		if err := os.WriteFile(*output, append(out, '\n'), 0o644); err != nil {
			panic(err)
		}
		return
	}
	for n := 3; n <= *maxN; n++ {
		start := time.Now()
		r := row{N: n, Forced: forced(n)}
		if n <= *exactMax {
			s := newSearcher(n, rng, true, 0)
			if s.dfs() {
				r.Status, r.Witness = "possible", s.path
			} else {
				r.Status = "impossible (exhaustive)"
			}
			r.Nodes = s.nodes
		} else if r.Forced {
			r.Status = "impossible (L1)"
		} else {
			// half the budget for randomized DFS, half for annealing
			deadline := time.Now().Add(*limit / 2)
			r.Status = "not found (heuristic)"
			for time.Now().Before(deadline) {
				r.Restarts++
				s := newSearcher(n, rng, false, 200000)
				if s.dfs() {
					r.Status, r.Witness = "possible", s.path
					break
				}
				r.Nodes += s.nodes
			}
			if r.Witness == nil {
				if w, k := anneal(n, rng, time.Now().Add(*limit/2)); w != nil {
					r.Status, r.Witness = "possible", w
					r.Restarts += k
				}
			}
		}
		if r.Witness != nil && !check(r.Witness) {
			panic("witness check failed")
		}
		if r.Witness != nil && r.Forced {
			panic(fmt.Sprintf("n=%d: witness contradicts L1", n))
		}
		r.Seconds = time.Since(start).Seconds()
		fmt.Fprintf(os.Stderr, "n=%2d forced=%-5v %s %.1fs\n", n, r.Forced, r.Status, r.Seconds)
		rows = append(rows, r)
		out, _ := json.MarshalIndent(map[string]any{
			"implementation": "arcs.go (Claude)",
			"rows":           rows,
			"scope":          "possible = checked witness; impossible (exhaustive / L1) = proof; not found (heuristic) = no conclusion.",
		}, "", "  ")
		if err := os.WriteFile(*output, append(out, '\n'), 0o644); err != nil {
			panic(err)
		}
	}
}
