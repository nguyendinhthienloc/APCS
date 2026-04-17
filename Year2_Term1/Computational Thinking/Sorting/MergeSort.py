def merge_sort(arr, stats=None, depth=0):
    if stats is None:
        stats = {'comparisons': 0, 'writes': 0, 'max_memory': 0, 'max_depth': 0}
    
    # Track maximum recursion depth
    stats['max_depth'] = max(stats['max_depth'], depth)
    
    if len(arr) <= 1:
        return arr

    # Track auxiliary memory usage
    stats['max_memory'] = max(stats['max_memory'], len(arr))
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], stats, depth + 1)
    right = merge_sort(arr[mid:], stats, depth + 1)

    return merge(left, right, stats)


def merge(left, right, stats):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        stats['comparisons'] += 1
        # Compare by age first, then first_name, then last_name
        if (left[i]['age'] < right[j]['age'] or
            (left[i]['age'] == right[j]['age'] and left[i]['first_name'] < right[j]['first_name']) or
            (left[i]['age'] == right[j]['age'] and left[i]['first_name'] == right[j]['first_name'] and left[i]['last_name'] <= right[j]['last_name'])):
            result.append(left[i])
            stats['writes'] += 1
            i += 1
        else:
            result.append(right[j])
            stats['writes'] += 1
            j += 1

    # Copy remaining elements
    while i < len(left):
        result.append(left[i])
        stats['writes'] += 1
        i += 1
    
    while j < len(right):
        result.append(right[j])
        stats['writes'] += 1
        j += 1
    
    # Track memory for result array
    stats['max_memory'] = max(stats['max_memory'], len(result))
    
    return result


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


if __name__ == '__main__':
    import os
    import matplotlib.pyplot as plt
    import time
    
    # Load users from file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    users_file = os.path.join(script_dir, 'users.txt')
    output_file = os.path.join(script_dir, 'output_merge.txt')
    users = load_users(users_file)
    
    # Sort users and measure time
    start_time = time.time()
    sorted_users = merge_sort(users)
    sort_time = time.time() - start_time
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Sorted by Age → First Name → Last Name:\n")
        for user in sorted_users:
            f.write(f"  Age: {user['age']:3}, First Name: {user['first_name']:10}, Last Name: {user['last_name']:10}\n")
        
        f.write(f"\nSort completed in {sort_time:.6f} seconds\n")
    
    print(f"Output written to output_merge.txt")
    print(f"Sorted {len(users)} users in {sort_time:.6f} seconds")
    
    # Performance testing with varying dataset sizes
    test_sizes = [10, 50, 100, 200, 500, 1000, 2000, 5000]
    times = []
    
    print("\nPerformance Testing...")
    for size in test_sizes:
        # Generate test data
        test_data = []
        for i in range(size):
            test_data.append({
                'age': i % 65 + 18,
                'first_name': f'Name{i % 50}',
                'last_name': f'Last{i % 15}'
            })
        
        # Measure sort time
        start = time.time()
        merge_sort(test_data)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  {size:5} users: {elapsed:.6f} seconds")
    