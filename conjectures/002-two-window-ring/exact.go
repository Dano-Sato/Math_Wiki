// Independent exact search (Claude, D005) for E_n of the two-window ring.
// Written from the definition, not from verify.py.
//
//	go run exact.go -from 3 -to 16 -output exact.json
//
// feasible(n, b) decides whether some circular permutation of 1..n has both
// R_2 <= b and R_3 <= b. Rotation fixes p_1 = 1 and reversal keeps
// p_2 < p_n. There is no node or time limit, so "false" is a finite proof.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"time"
)

type search struct {
	n, b     int
	path     []int
	used     []bool
	nodes    int64
	deadline time.Time // zero: no limit
	timedOut bool
}

// slack checks that the largest and smallest unused values can still get two
// neighbours whose pair sums fit the pair window [hi2-b, lo2+b]. The window
// only shrinks as the path grows, so this never prunes a feasible branch.
// Possible neighbours of an unused value: other unused values, the current
// end of the path, and p_1 = 1 (the ring closes onto it).
func (s *search) slack(lo2, hi2 int) bool {
	low, high := hi2-s.b, lo2+s.b
	last := s.path[len(s.path)-1]
	big, little := 0, 0
	for v := s.n; v >= 2; v-- {
		if !s.used[v] {
			big = v
			break
		}
	}
	if big == 0 {
		return true
	}
	for v := 2; v <= s.n; v++ {
		if !s.used[v] {
			little = v
			break
		}
	}
	// two smallest candidates for big's neighbours: 1 and min(last, smallest other unused)
	second := last
	for v := 2; v < second; v++ {
		if !s.used[v] && v != big {
			second = v
			break
		}
	}
	if big+second > high {
		return false
	}
	// two largest candidates for little's neighbours among last and other unused values
	first, next, seen := last, 1, 0
	for v := s.n; v >= 2 && seen < 2; v-- {
		if s.used[v] || v == little {
			continue
		}
		seen++
		if v > first {
			first, next = v, first
		} else if v > next {
			next = v
		}
	}
	return little+next >= low
}

func (s *search) visit(lo2, hi2, lo3, hi3 int) bool {
	s.nodes++
	if s.timedOut || (!s.deadline.IsZero() && s.nodes&0xfffff == 0 && time.Now().After(s.deadline)) {
		s.timedOut = true
		return false
	}
	k := len(s.path)
	last := s.path[k-1]
	// pair window bounds the next value directly
	vmin, vmax := hi2-s.b-last, lo2+s.b-last
	if k >= 2 {
		prev := s.path[k-2]
		if m := hi3 - s.b - last - prev; m > vmin {
			vmin = m
		}
		if m := lo3 + s.b - last - prev; m < vmax {
			vmax = m
		}
	}
	if vmin < 2 {
		vmin = 2
	}
	if vmax > s.n {
		vmax = s.n
	}
	for v := vmin; v <= vmax; v++ {
		if s.used[v] {
			continue
		}
		pair := last + v
		l2, h2 := min(lo2, pair), max(hi2, pair)
		l3, h3 := lo3, hi3
		if k >= 2 {
			t := s.path[k-2] + last + v
			l3, h3 = min(lo3, t), max(hi3, t)
		}
		if k == s.n-1 {
			if s.path[1] > v {
				continue
			}
			// close the ring: pairs (v,1), triples (last,v,1), (v,1,p_2)
			c2 := v + 1
			l2, h2 = min(l2, c2), max(h2, c2)
			for _, t := range []int{last + v + 1, v + 1 + s.path[1]} {
				l3, h3 = min(l3, t), max(h3, t)
			}
			if h2-l2 <= s.b && h3-l3 <= s.b {
				s.path = append(s.path, v)
				return true
			}
			continue
		}
		s.used[v] = true
		s.path = append(s.path, v)
		if s.slack(l2, h2) && s.visit(l2, h2, l3, h3) {
			return true
		}
		s.path = s.path[:k]
		s.used[v] = false
	}
	return false
}

// feasible returns a witness, the node count, and whether the search was
// cut off by the deadline (then "no witness" proves nothing).
func feasible(n, b int, limit time.Duration) ([]int, int64, bool) {
	s := &search{n: n, b: b, path: []int{1}, used: make([]bool, n+1)}
	if limit > 0 {
		s.deadline = time.Now().Add(limit)
	}
	s.used[1] = true
	const inf = 1 << 30
	if s.visit(inf, -inf, inf, -inf) {
		return s.path, s.nodes, false
	}
	return nil, s.nodes, s.timedOut
}

func widths(p []int) (int, int) {
	n := len(p)
	lo2, hi2, lo3, hi3 := 1<<30, -1, 1<<30, -1
	for i := 0; i < n; i++ {
		a := p[i] + p[(i+1)%n]
		t := a + p[(i+2)%n]
		lo2, hi2 = min(lo2, a), max(hi2, a)
		lo3, hi3 = min(lo3, t), max(hi3, t)
	}
	return hi2 - lo2, hi3 - lo3
}

type trial struct {
	Bound    int     `json:"bound"`
	Found    bool    `json:"found"`
	TimedOut bool    `json:"timed_out"`
	Nodes    int64   `json:"nodes"`
	Seconds  float64 `json:"seconds"`
}

type row struct {
	N int `json:"n"`
	// Optimum is exact unless Status says otherwise.
	Status  string  `json:"status"`
	Optimum int     `json:"optimum,omitempty"`
	Excess  int     `json:"excess_over_floor_half"`
	Witness []int   `json:"witness,omitempty"`
	Widths  [2]int  `json:"widths"`
	Trials  []trial `json:"trials"`
}

func main() {
	from := flag.Int("from", 3, "smallest n")
	to := flag.Int("to", 16, "largest n")
	floorOnly := flag.Bool("floor-only", false, "only test bound floor(n/2)")
	limit := flag.Duration("timeout", 0, "per-bound time limit (0 = none; a timeout proves nothing)")
	output := flag.String("output", "exact.json", "output JSON")
	flag.Parse()
	var rows []row
	for n := *from; n <= *to; n++ {
		r := row{N: n, Status: "unknown"}
		for b := n / 2; b <= n/2+1; b++ {
			start := time.Now()
			w, nodes, cut := feasible(n, b, *limit)
			r.Trials = append(r.Trials, trial{b, w != nil, cut, nodes, time.Since(start).Seconds()})
			if w != nil {
				x, y := widths(w)
				if max(x, y) > b {
					panic("witness check failed")
				}
				r.Witness, r.Widths, r.Excess = w, [2]int{x, y}, b-n/2
				// floor(n/2) is a proven lower bound (L1), so a witness at the
				// floor, or at floor+1 after an exhausted floor search, is optimal.
				if b == n/2 || !r.Trials[0].TimedOut {
					r.Status, r.Optimum = "exact", b
				} else {
					r.Status = "upper bound only"
				}
				break
			}
			if *floorOnly || cut {
				if !cut {
					r.Status, r.Excess = "floor infeasible", 1
				}
				if *floorOnly {
					break
				}
			}
		}
		if r.Witness == nil && len(r.Trials) == 2 && !r.Trials[0].TimedOut && !r.Trials[1].TimedOut {
			r.Status = "COUNTEREXAMPLE to 002: floor(n/2)+1 exhausted"
		}
		fmt.Fprintf(os.Stderr, "n=%d %s E=%d (floor+%d) trials=%v\n", n, r.Status, r.Optimum, r.Excess, r.Trials)
		rows = append(rows, r)
		out, _ := json.MarshalIndent(map[string]any{
			"implementation": "exact.go (Claude, independent of verify.py)",
			"rows":           rows,
			"scope":          "Exact minima for the listed n only; no general proof.",
		}, "", "  ")
		if err := os.WriteFile(*output, append(out, '\n'), 0o644); err != nil {
			panic(err)
		}
	}
}
