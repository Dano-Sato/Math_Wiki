// Independent check of conjecture 038 (Claude). Written from the statement,
// not from explore.py.
//
//	go run verify_claude.go -limit 1000000000 -output verify_claude_1e9.json
//
// A_k(x) = #{m <= x : omega(m) = k}. Going from x-1 to x only A_j changes,
// j = omega(x), and only by +1. Then A_j^2 >= A_{j-1} A_{j+1} can only improve,
// while the inequalities at k = j-1 and k = j+1 (whose right sides contain A_j)
// can only get worse. So if all inequalities hold at x-1, it suffices to test
// k = j-1 and k = j+1 at x. All arithmetic is exact uint64 (A_k <= x <= 4e9
// keeps A_k^2 below 2^64).
//
// Besides pass/fail, it records for each k the smallest ratio
// A_k^2 / (A_{k-1} A_{k+1}) over all x at which both neighbours are positive,
// to show where the inequality is tightest.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"math"
	"os"
	"time"
)

type tight struct {
	K        int     `json:"k"`
	MinRatio float64 `json:"min_ratio"`
	AtX      int     `json:"at_x"`
	Counts   []uint64 `json:"counts_at_x"`
}

func main() {
	limit := flag.Int("limit", 1000000000, "largest x")
	output := flag.String("output", "verify_claude.json", "output JSON")
	flag.Parse()
	N := *limit
	if N > 4000000000 {
		panic("limit too large for exact uint64 squares")
	}
	start := time.Now()

	// omega sieve: omega[p] == 0 when reached means p is prime
	omega := make([]uint8, N+1)
	for p := 2; p <= N; p++ {
		if omega[p] == 0 {
			for m := p; m <= N; m += p {
				omega[m]++
			}
		}
	}
	sieveTime := time.Since(start).Seconds()

	// independent cross-check of omega on small m by trial division
	for m := 1; m <= 200000 && m <= N; m++ {
		x, c := m, 0
		for p := 2; p*p <= x; p++ {
			if x%p == 0 {
				c++
				for x%p == 0 {
					x /= p
				}
			}
		}
		if x > 1 {
			c++
		}
		if int(omega[m]) != c {
			panic(fmt.Sprintf("omega mismatch at %d", m))
		}
	}

	A := make([]uint64, 16)
	A[0] = 1 // m = 1
	maxK := 0
	best := make([]tight, 16)
	for k := range best {
		best[k] = tight{K: k, MinRatio: math.Inf(1)}
	}
	var checks int64
	var failure map[string]any
	test := func(k, x int) {
		if k < 1 || k+1 >= len(A) || A[k-1] == 0 || A[k+1] == 0 {
			return
		}
		checks++
		lhs, rhs := A[k]*A[k], A[k-1]*A[k+1]
		if lhs < rhs && failure == nil {
			failure = map[string]any{"x": x, "k": k, "counts": append([]uint64(nil), A[:maxK+1]...)}
		}
		r := float64(lhs) / float64(rhs)
		if r < best[k].MinRatio {
			best[k] = tight{K: k, MinRatio: r, AtX: x, Counts: append([]uint64(nil), A[:maxK+1]...)}
		}
	}
	for x := 2; x <= N; x++ {
		j := int(omega[x])
		A[j]++
		if j > maxK {
			maxK = j
		}
		test(j-1, x)
		test(j+1, x)
	}
	// final full check at x = N as a consistency test
	for k := 1; k < maxK; k++ {
		if A[k]*A[k] < A[k-1]*A[k+1] {
			panic("final state violates log-concavity but no failure was recorded")
		}
	}
	var bests []tight
	for k := 1; k < maxK; k++ {
		bests = append(bests, best[k])
	}
	out, _ := json.MarshalIndent(map[string]any{
		"implementation":     "verify_claude.go (Claude, independent of explore.py)",
		"limit_x":            N,
		"first_failure":      failure,
		"targeted_checks":    checks,
		"max_omega":          maxK,
		"counts_at_limit":    A[:maxK+1],
		"tightest_by_k":      bests,
		"sieve_seconds":      sieveTime,
		"total_seconds":      time.Since(start).Seconds(),
		"method":             "only k = omega(x) +- 1 can newly fail when x increases; exact uint64 arithmetic",
		"scope":              "Finite verification for all integer cutoffs x <= limit_x.",
	}, "", "  ")
	if err := os.WriteFile(*output, append(out, '\n'), 0o644); err != nil {
		panic(err)
	}
	fmt.Println(string(out))
}
