// Conjecture 010: balance circular sums at step sizes one and two.
// Run from this folder: go run explore.go
package main

import (
	"encoding/json"
	"fmt"
	"math"
	"math/rand"
	"os"
)

type Row struct {
	Kind        string `json:"kind"`
	N           int    `json:"n"`
	Values      []int  `json:"values"`
	Cost        int    `json:"cost"`
	Width       int    `json:"width"`
	Witness     []int  `json:"witness"`
	Exact       bool   `json:"exact"`
	Evaluations int    `json:"evaluations"`
}

func cost(a []int) int {
	n, result := len(a), 0
	for _, d := range []int{1, 2} {
		for k := 1; k <= n/2; k++ {
			s := 0
			for j := 0; j < k; j++ {
				s += a[(d*j)%n]
			}
			lo, hi := s, s
			for i := 1; i < n; i++ {
				s += a[(d*(i+k-1))%n] - a[(d*(i-1))%n]
				if s < lo {
					lo = s
				}
				if s > hi {
					hi = s
				}
			}
			if hi-lo > result {
				result = hi - lo
			}
		}
	}
	return result
}

func exact(counts []int, n int) Row {
	values := []int{}
	for v, c := range counts {
		for j := 0; j < c; j++ {
			values = append(values, v)
		}
	}
	a := make([]int, n)
	first := values[0]
	a[0] = first
	counts[first]--
	best, evaluations := int(^uint(0)>>1), 0
	var witness []int
	var visit func(int)
	visit = func(pos int) {
		if pos == n {
			if a[1] > a[n-1] {
				return
			}
			evaluations++
			c := cost(a)
			if c < best {
				best = c
				witness = append([]int(nil), a...)
			}
			return
		}
		for v, c := range counts {
			if c == 0 {
				continue
			}
			counts[v]--
			a[pos] = v
			visit(pos + 1)
			counts[v]++
		}
	}
	visit(1)
	counts[first]++
	return Row{"grid_exact", n, values, best, values[n-1] - first, witness, true, evaluations}
}

func search(values []int, rng *rand.Rand) Row {
	n := len(values)
	lo, hi := values[0], values[0]
	for _, v := range values {
		if v < lo {
			lo = v
		}
		if v > hi {
			hi = v
		}
	}
	width := hi - lo
	target := 2 * width
	best, evaluations := int(^uint(0)>>1), 0
	var witness []int
	for restart := 0; restart < 8; restart++ {
		a := append([]int(nil), values...)
		rng.Shuffle(n, func(i, j int) { a[i], a[j] = a[j], a[i] })
		current := cost(a)
		evaluations++
		if current < best {
			best = current
			witness = append([]int(nil), a...)
		}
		if best <= target {
			break
		}
		for t := 0; t < 6000; t++ {
			i, j := rng.Intn(n), rng.Intn(n)
			a[i], a[j] = a[j], a[i]
			candidate := cost(a)
			evaluations++
			temp := float64(width) * (0.20*(1-float64(t)/6000) + 0.003)
			if candidate <= current || rng.Float64() < math.Exp(float64(current-candidate)/temp) {
				current = candidate
			} else {
				a[i], a[j] = a[j], a[i]
			}
			if current < best {
				best = current
				witness = append([]int(nil), a...)
			}
			if best <= target {
				break
			}
		}
		if best <= target {
			break
		}
	}
	return Row{"search", n, append([]int(nil), values...), best, width, witness, false, evaluations}
}

func main() {
	rows := []Row{}
	for _, n := range []int{3, 5, 7, 9, 11} {
		counts := make([]int, 5)
		var makeCounts func(int, int)
		makeCounts = func(v, left int) {
			if v == 4 {
				if left < 1 {
					return
				}
				counts[4] = left
				rows = append(rows, exact(counts, n))
				return
			}
			start := 0
			if v == 0 {
				start = 1
			}
			for c := start; c <= left; c++ {
				counts[v] = c
				makeCounts(v+1, left-c)
			}
		}
		makeCounts(0, n)
		fmt.Printf("exact n=%d cumulative cases=%d\n", n, len(rows))
	}
	rng := rand.New(rand.NewSource(20261024))
	for n := 13; n <= 51; n += 2 {
		for sample := 0; sample < 20; sample++ {
			a := make([]int, n)
			for i := range a {
				switch sample % 5 {
				case 0:
					a[i] = rng.Intn(1001)
				case 1:
					a[i] = rng.Intn(2) * 1000
				case 2:
					a[i] = rng.Intn(5) * 250
				case 3:
					a[i] = i * i
				case 4:
					a[i] = rng.Intn(11)
					if rng.Intn(5) == 0 {
						a[i] += 1000
					}
				}
			}
			rows = append(rows, search(a, rng))
		}
		fmt.Printf("search n=%d complete\n", n)
	}
	failures := []int{}
	for i, r := range rows {
		if r.Cost > 2*r.Width {
			failures = append(failures, i)
		}
	}
	report := map[string]any{"definition_version": "010-0.1", "date": "2026-10-24", "seed": 20261024, "rows": rows, "rows_over_bound": failures, "scope": "Exact multiset enumeration for grid inputs; heuristic searches certify only their saved witnesses."}
	data, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		panic(err)
	}
	if err = os.WriteFile("experiment.json", append(data, '\n'), 0644); err != nil {
		panic(err)
	}
	fmt.Println("rows over conjectured bound:", failures)
}
