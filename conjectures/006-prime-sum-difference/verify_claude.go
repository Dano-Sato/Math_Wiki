// Independent check of conjecture 006 (Claude). Written from the statement,
// not from the existing scripts.
//
//	go run verify_claude.go -all 1500 -sizes 5000,10000,30000,50000 -output verify_claude.json
//
// nu_n: maximum matching in the graph on {1..2n} with x ~ y iff x+y and |x-y|
// are both prime. The graph is bipartite (odd / even), so we use Hopcroft-Karp.
// kappa_n: maximum matching among non-multiples of 3, computed by dynamic
// programming on the two residue chains (not by the greedy rule of L3).
// Every reported matching is re-checked edge by edge.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"
)

var isComposite []bool

func prime(x int) bool { return x >= 2 && !isComposite[x] }

// hopcroftKarp on left = odd numbers, right = even numbers.
func hopcroftKarp(n int) (int, []int) {
	N := 2 * n
	var primes []int
	for p := 2; p <= N; p++ {
		if prime(p) {
			primes = append(primes, p)
		}
	}
	adj := make([][]int32, N+1)
	for x := 1; x <= N; x += 2 {
		for _, p := range primes {
			for _, y := range [2]int{x - p, x + p} {
				if y >= 1 && y <= N && y%2 == 0 && prime(x+y) {
					adj[x] = append(adj[x], int32(y))
				}
			}
		}
	}
	matchL := make([]int, N+1) // odd -> even partner
	matchR := make([]int, N+1) // even -> odd partner
	dist := make([]int, N+1)
	const inf = 1 << 30
	bfs := func() bool {
		queue := []int{}
		found := false
		for x := 1; x <= N; x += 2 {
			if matchL[x] == 0 {
				dist[x] = 0
				queue = append(queue, x)
			} else {
				dist[x] = inf
			}
		}
		for len(queue) > 0 {
			x := queue[0]
			queue = queue[1:]
			for _, y := range adj[x] {
				w := matchR[y]
				if w == 0 {
					found = true
				} else if dist[w] == inf {
					dist[w] = dist[x] + 1
					queue = append(queue, w)
				}
			}
		}
		return found
	}
	var dfs func(x int) bool
	dfs = func(x int) bool {
		for _, yy := range adj[x] {
			y := int(yy)
			w := matchR[y]
			if w == 0 || (dist[w] == dist[x]+1 && dfs(w)) {
				matchL[x], matchR[y] = y, x
				return true
			}
		}
		dist[x] = inf
		return false
	}
	size := 0
	for bfs() {
		for x := 1; x <= N; x += 2 {
			if matchL[x] == 0 && dfs(x) {
				size++
			}
		}
	}
	// re-check
	used := make([]bool, N+1)
	for x := 1; x <= N; x += 2 {
		if y := matchL[x]; y != 0 {
			d := x - y
			if d < 0 {
				d = -d
			}
			if used[x] || used[y] || !prime(x+y) || !prime(d) {
				panic(fmt.Sprintf("bad pair (%d,%d)", x, y))
			}
			used[x], used[y] = true, true
		}
	}
	return size, matchL
}

// kappa by DP: maximum matching on paths x - x+3 (edge iff 2x+3 prime), x not divisible by 3.
func kappa(n int) int {
	N := 2 * n
	total := 0
	for _, start := range []int{1, 2} {
		// chain start, start+3, ...; DP over "previous vertex free / used"
		free, used := 0, -1 << 30 // best size with previous vertex unmatched / matched
		prev := -1
		for x := start; x <= N; x += 3 {
			nf, nu := max(free, used), -1<<30
			if prev >= 0 && prime(prev+x) {
				nu = free + 1 // match prev with x (prev must be unmatched)
			}
			free, used = nf, nu
			prev = x
		}
		total += max(free, used)
	}
	return total
}

type row struct {
	N         int  `json:"n"`
	Nu        int  `json:"nu"`
	Kappa     int  `json:"kappa"`
	Predicted int  `json:"predicted_min_n_t_plus_kappa"`
	Holds     bool `json:"formula_holds"`
}

func main() {
	all := flag.Int("all", 1500, "check every n from 1 to this value")
	sizes := flag.String("sizes", "5000,10000,30000,50000", "extra sizes")
	output := flag.String("output", "verify_claude.json", "output JSON")
	flag.Parse()
	list := []int{}
	for n := 1; n <= *all; n++ {
		list = append(list, n)
	}
	for _, s := range strings.Split(*sizes, ",") {
		if s == "" {
			continue
		}
		v, err := strconv.Atoi(strings.TrimSpace(s))
		if err != nil {
			panic(err)
		}
		list = append(list, v)
	}
	maxN := 0
	for _, n := range list {
		maxN = max(maxN, n)
	}
	isComposite = make([]bool, 4*maxN+10)
	for i := 2; i*i < len(isComposite); i++ {
		if !isComposite[i] {
			for j := i * i; j < len(isComposite); j += i {
				isComposite[j] = true
			}
		}
	}
	start := time.Now()
	var rows []row
	var failures []int
	for _, n := range list {
		nu, _ := hopcroftKarp(n)
		k := kappa(n)
		t := 2 * n / 3
		pred := min(n, t+k)
		r := row{n, nu, k, pred, nu == pred}
		rows = append(rows, r)
		if !r.Holds && n >= 4 {
			failures = append(failures, n)
		}
		if n > *all {
			fmt.Fprintf(os.Stderr, "n=%d nu=%d kappa=%d predicted=%d holds=%v (%.1fs)\n", n, nu, k, pred, r.Holds, time.Since(start).Seconds())
		}
	}
	out, _ := json.MarshalIndent(map[string]any{
		"implementation":       "verify_claude.go (Claude, Hopcroft-Karp + path DP, independent of existing scripts)",
		"checked_all_n_through": *all,
		"extra_sizes":          *sizes,
		"failures_n_ge_4":      failures,
		"rows":                 rows,
		"seconds":              time.Since(start).Seconds(),
		"scope":                "Exact maximum matchings for the listed n only.",
	}, "", " ")
	if err := os.WriteFile(*output, append(out, '\n'), 0o644); err != nil {
		panic(err)
	}
	fmt.Fprintf(os.Stderr, "failures (n>=4): %v\n", failures)
}
