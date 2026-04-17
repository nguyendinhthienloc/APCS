import time
import matplotlib.pyplot as plt
import os

# Import both sorting algorithms
from MergeSort import merge_sort
from BubbleSort import bubble_sort


def load_users(filename):
    users = []
    with open(filename, 'r', encoding='utf-8-sig') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 3:
                users.append({
                    'age': int(parts[0]),
                    'first_name': parts[1],
                    'last_name': parts[2]
                })
    return users



def benchmark_sorting(users_data):
    # Diverse test sizes from 5 to 5000
    test_sizes = [5, 10, 25, 50, 100, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 5000]
    
    merge_times = []
    bubble_times = []
    merge_stats_list = []
    bubble_stats_list = []
    
    print("Performance Comparison: Merge Sort vs Bubble Sort")
    print(f"Testing with first N users from users.txt\n")
    print(f"{'Users':<10} {'Merge Sort (s)':<20} {'Bubble Sort (s)':<20} {'Speedup':<10}")
    print("-" * 70)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    for size in test_sizes:
        # Use first N users from actual data
        test_data = users_data[:size]
        
        # Test Merge Sort with statistics
        data_copy = [u.copy() for u in test_data]
        merge_stats = {'comparisons': 0, 'writes': 0, 'max_memory': 0, 'max_depth': 0}
        start = time.perf_counter()
        sorted_merge = merge_sort(data_copy, merge_stats)
        merge_time = time.perf_counter() - start
        merge_times.append(merge_time)
        merge_stats_list.append(merge_stats)
        
        # Test Bubble Sort with statistics
        data_copy = [u.copy() for u in test_data]
        bubble_stats = {'comparisons': 0, 'swaps': 0, 'max_memory': 0, 'max_depth': 0}
        start = time.perf_counter()
        sorted_bubble = bubble_sort(data_copy, bubble_stats)
        bubble_time = time.perf_counter() - start
        bubble_times.append(bubble_time)
        bubble_stats_list.append(bubble_stats)
        
        # Write output file for this range
        output_file = os.path.join(script_dir, f'output{size}.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"First {size} users - Sorted by Age → First Name → Last Name\n")
            f.write(f"\n=== MERGE SORT STATISTICS ===\n")
            f.write(f"Time: {merge_time:.9f} seconds\n")
            f.write(f"Comparisons: {merge_stats['comparisons']:,}\n")
            f.write(f"Writes: {merge_stats['writes']:,}\n")
            f.write(f"Auxiliary Memory (max elements): {merge_stats['max_memory']:,}\n")
            f.write(f"Recursion Depth: {merge_stats['max_depth']:,}\n")
            
            f.write(f"\n=== BUBBLE SORT STATISTICS ===\n")
            f.write(f"Time: {bubble_time:.9f} seconds\n")
            f.write(f"Comparisons: {bubble_stats['comparisons']:,}\n")
            f.write(f"Swaps: {bubble_stats['swaps']:,}\n")
            f.write(f"Auxiliary Memory (max elements): {bubble_stats['max_memory']:,}\n")
            f.write(f"Recursion Depth: {bubble_stats['max_depth']:,}\n")
            
            f.write(f"\n=== SORTED DATA ===\n")
            for user in sorted_merge:
                f.write(f"  Age: {user['age']:3}, First Name: {user['first_name']:10}, Last Name: {user['last_name']:10}\n")
        
        speedup = bubble_time / merge_time if merge_time > 0 else 1
        print(f"{size:<10} {merge_time:<20.9f} {bubble_time:<20.9f} {speedup:<10.2f}x")
    
    return test_sizes, merge_times, bubble_times, merge_stats_list, bubble_stats_list


if __name__ == '__main__':
    # Load users from users.txt
    script_dir = os.path.dirname(os.path.abspath(__file__))
    users_file = os.path.join(script_dir, 'users.txt')
    all_users = load_users(users_file)
    
    print(f"Loaded {len(all_users)} users from users.txt\n")
    
    # Run benchmarks
    sizes, merge_times, bubble_times, merge_stats_list, bubble_stats_list = benchmark_sorting(all_users)
    
    print(f"\nGenerated {len(sizes)} output files (output5.txt through output5000.txt)")
    
    # Create statistics summary file
    stats_file = os.path.join(script_dir, 'statistics_summary.txt')
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write("SORTING ALGORITHM STATISTICS COMPARISON\n")
        f.write("=" * 120 + "\n\n")
        
        f.write(f"{'Size':<10} {'Algorithm':<15} {'Time (s)':<15} {'Comparisons':<20} {'Swaps/Writes':<20} {'Aux Memory':<15} {'Recursion':<12}\n")
        f.write("-" * 120 + "\n")
        
        for i, size in enumerate(sizes):
            f.write(f"{size:<10} Merge Sort      {merge_times[i]:<15.9f} {merge_stats_list[i]['comparisons']:<20,} {merge_stats_list[i]['writes']:<20,} {merge_stats_list[i]['max_memory']:<15,} {merge_stats_list[i]['max_depth']:<12,}\n")
            f.write(f"{'':<10} Bubble Sort     {bubble_times[i]:<15.9f} {bubble_stats_list[i]['comparisons']:<20,} {bubble_stats_list[i]['swaps']:<20,} {bubble_stats_list[i]['max_memory']:<15,} {bubble_stats_list[i]['max_depth']:<12,}\n")
            f.write("\n")
    
    print(f"Generated: statistics_summary.txt")
    
    # Single Linear Chart: Time Complexity Comparison
    plt.figure(figsize=(14, 8))
    plt.plot(sizes, merge_times, marker='o', linewidth=2.5, markersize=8, 
             color='blue', label='Merge Sort O(n log n)', linestyle='-')
    plt.plot(sizes, bubble_times, marker='s', linewidth=2.5, markersize=8, 
             color='red', label='Bubble Sort O(n²)', linestyle='-')
    plt.xlabel('Number of Users', fontsize=12)
    plt.ylabel('Time (seconds)', fontsize=12)
    plt.title('Sorting Algorithm Time Complexity Comparison', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    
    # Add annotations for key points
    max_bubble_idx = len(bubble_times) - 1
    plt.annotate(f'{bubble_times[max_bubble_idx]:.3f}s', 
                xy=(sizes[max_bubble_idx], bubble_times[max_bubble_idx]),
                xytext=(10, 10), textcoords='offset points',
                fontsize=9, color='red', fontweight='bold')
    plt.annotate(f'{merge_times[max_bubble_idx]:.3f}s', 
                xy=(sizes[max_bubble_idx], merge_times[max_bubble_idx]),
                xytext=(10, -15), textcoords='offset points',
                fontsize=9, color='blue', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(script_dir, 'time_complexity_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print("\nExported: time_complexity_comparison.png")
    print("\nComparison complete!")
