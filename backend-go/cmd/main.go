package main

import (
	"context"
	"fmt"
	"github.com/redis/go-redis/v9"
	"log"
	"os/exec"
)

func main() {
	ctx := context.Background()
	rdb := redis.NewClient(&redis.Options{
		Addr:     "localhost:6379",
		Password: "",
		DB:       0,
	})

	err := rdb.Set(ctx, "key", "IteraMindAI", 0).Err()
	if err != nil {
		log.Fatalf("Could not set key in Redis: %v", err)
	}

	output, err := exec.Command("/mnt/f/Dev_Faculdade/IteraMindAI/core-rust/target/debug/iteramind_core").Output()
	if err != nil {
		log.Fatalf("Error executing Rust core: %v", err)
	}

	fmt.Printf("Output from Rust Core: %s\n", output)
}
