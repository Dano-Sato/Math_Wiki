// Independent incremental matching review of conjecture 006.
// Run from this directory: go run review_incremental.go -max 30000
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
)

func main() {
	limit := flag.Int("max", 30000, "check every n up to this value")
	output := flag.String("output", "review_incremental.json", "JSON output")
	flag.Parse()
	prime := make([]bool, 4**limit+1)
	for i := 2; i < len(prime); i++ {
		prime[i] = true
	}
	for p := 2; p*p < len(prime); p++ {
		if prime[p] {
			for j := p * p; j < len(prime); j += p {
				prime[j] = false
			}
		}
	}
	adj := make([][]int, 2**limit+1)
	mate := make([]int, len(adj))
	seen := make([]int, len(adj))
	parent := make([]int, len(adj))
	usedInternal := make([]bool, len(adj))
	queue := make([]int, 0, len(adj))
	stamp, matching, kappa, searches := 0, 0, 0, 0
	augment := func(root int) bool {
		stamp++
		searches++
		queue = append(queue[:0], root)
		seen[root] = stamp
		for head := 0; head < len(queue); head++ {
			u := queue[head]
			for _, v := range adj[u] {
				if seen[v] == stamp {
					continue
				}
				seen[v], parent[v] = stamp, u
				if mate[v] == 0 {
					for v != 0 {
						p := parent[v]
						old := mate[p]
						mate[p], mate[v] = v, p
						v = old
					}
					return true
				}
				w := mate[v]
				if seen[w] != stamp {
					seen[w] = stamp
					queue = append(queue, w)
				}
			}
		}
		return false
	}
	rows := make([]map[string]int, 0, *limit)
	failures := []int{}
	witnesses := map[int][][2]int{}
	for x := 1; x <= 2**limit; x++ {
		// Add one vertex and all incident edges. A maximum matching in the old
		// graph needs at most one augmentation, starting at this new vertex.
		for y := 1 + x%2; y < x; y += 2 {
			if prime[x+y] && prime[x-y] {
				adj[x] = append(adj[x], y)
				adj[y] = append(adj[y], x)
			}
		}
		if x > 3 && x%3 != 0 && !usedInternal[x-3] && prime[2*x-3] {
			usedInternal[x-3], usedInternal[x] = true, true
			kappa++
		}
		upper := x/3 + kappa
		if upper > x/2 {
			upper = x / 2
		}
		// This same elementary upper bound is valid for odd prefix lengths.
		if matching < upper && augment(x) {
			matching++
		}
		if x%2 != 0 {
			continue
		}
		n := x / 2
		rows = append(rows, map[string]int{"n": n, "kappa": kappa, "predicted": upper, "maximum": matching})
		if matching != upper {
			failures = append(failures, n)
		}
		if n <= 20 || n%5000 == 0 || n == 7425 || n == 7426 || (n >= 4 && matching != upper) {
			pairs := [][2]int{}
			for a := 1; a <= x; a++ {
				b := mate[a]
				if b == 0 {
					continue
				}
				if b > x || mate[b] != a {
					panic("invalid matching")
				}
				if a < b {
					if !prime[a+b] || !prime[b-a] {
						panic("nonprime pair")
					}
					pairs = append(pairs, [2]int{a, b})
				}
			}
			if len(pairs) != matching {
				panic("wrong cardinality")
			}
			witnesses[n] = pairs
		}
		if n%5000 == 0 {
			fmt.Printf("n=%d kappa=%d predicted=%d maximum=%d searches=%d\n", n, kappa, upper, matching, searches)
		}
		if n >= 4 && matching != upper {
			fmt.Printf("Counterexample: n=%d\n", n)
			break
		}
	}
	report := map[string]any{"date": "2026-10-24", "definition_version": "006-0.1", "algorithm": "incremental vertex insertion and alternating BFS; exact maximum at every prefix", "rows": rows, "failed_sizes": failures, "witnesses": witnesses, "augmentation_searches": searches}
	data, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		panic(err)
	}
	if err := os.WriteFile(*output, append(data, '\n'), 0644); err != nil {
		panic(err)
	}
}
