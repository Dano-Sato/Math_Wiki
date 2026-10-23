// Exhaustive enumeration for conjecture 008 (Claude): rows of 1..n in which no
// run of k >= 2 consecutive entries has a sum divisible by k (an integer mean).
//
//	go run count.go -max 40 -output experiment.json
//
// Every solution is recorded and classified against the four known families
// (sigma_1, sigma_2 and their reversals). The search is exhaustive.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"time"
)

type result struct {
	N         int     `json:"n"`
	Count     int     `json:"count"`
	Known     int     `json:"known_family_solutions"`
	Sporadic  [][]int `json:"sporadic_solutions"`
	Nodes     int64   `json:"nodes"`
	Seconds   float64 `json:"seconds"`
}

// xorRow returns sigma_m: position i (0-based) holds (i XOR m) + 1, or nil if that is not a permutation of 1..n.
func xorRow(n, m int) []int {
	p := make([]int, n)
	for i := range p {
		v := i ^ m
		if v >= n {
			return nil
		}
		p[i] = v + 1
	}
	return p
}

func reversed(p []int) []int {
	q := make([]int, len(p))
	for i, v := range p {
		q[len(p)-1-i] = v
	}
	return q
}

func key(p []int) string { return fmt.Sprint(p) }

func run(n int) result {
	start := time.Now()
	known := map[string]bool{}
	for _, m := range []int{1, 2} {
		if p := xorRow(n, m); p != nil {
			known[key(p)] = true
			known[key(reversed(p))] = true
		}
	}
	path := make([]int, 0, n)
	prefix := []int{0}
	used := make([]bool, n+1)
	res := result{N: n}
	var dfs func()
	dfs = func() {
		res.Nodes++
		m := len(path)
		if m == n {
			res.Count++
			if known[key(path)] {
				res.Known++
			} else {
				res.Sporadic = append(res.Sporadic, append([]int(nil), path...))
			}
			return
		}
		for v := 1; v <= n; v++ {
			if used[v] {
				continue
			}
			total := prefix[m] + v
			ok := true
			for k := 2; k <= m+1; k++ {
				if (total-prefix[m+1-k])%k == 0 {
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
			dfs()
			path = path[:m]
			prefix = prefix[:m+1]
			used[v] = false
		}
	}
	dfs()
	if res.Known != len(known) {
		panic(fmt.Sprintf("n=%d: a known family member was not found", n))
	}
	res.Seconds = time.Since(start).Seconds()
	return res
}

func main() {
	maxN := flag.Int("max", 40, "largest n")
	output := flag.String("output", "experiment.json", "output JSON")
	flag.Parse()
	var results []result
	for n := 1; n <= *maxN; n++ {
		r := run(n)
		fmt.Fprintf(os.Stderr, "n=%2d count=%d known=%d sporadic=%d (%.1fs)\n", n, r.Count, r.Known, len(r.Sporadic), r.Seconds)
		results = append(results, r)
		out, _ := json.MarshalIndent(map[string]any{
			"implementation": "count.go (Claude)",
			"results":        results,
			"scope":          "Exhaustive enumeration for each listed n.",
		}, "", "  ")
		if err := os.WriteFile(*output, append(out, '\n'), 0o644); err != nil {
			panic(err)
		}
	}
}
