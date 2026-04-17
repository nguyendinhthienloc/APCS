def bubble_sort(arr, stats=None):
    if stats is None:
        stats = {'comparisons': 0, 'swaps': 0, 'max_memory': 0, 'max_depth': 0}
    
    n = len(arr)
    # Bubble sort uses O(1) auxiliary memory (in-place)
    stats['max_memory'] = 1
    # Bubble sort is iterative, no recursion
    stats['max_depth'] = 0
    
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            stats['comparisons'] += 1
            # Compare by age first, then first_name, then last_name
            if (arr[j]['age'] > arr[j + 1]['age'] or
                (arr[j]['age'] == arr[j + 1]['age'] and arr[j]['first_name'] > arr[j + 1]['first_name']) or
                (arr[j]['age'] == arr[j + 1]['age'] and arr[j]['first_name'] == arr[j + 1]['first_name'] and arr[j]['last_name'] > arr[j + 1]['last_name'])):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                stats['swaps'] += 1
                swapped = True
        if not swapped:
            break
    return arr


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
    import time
    
    # Load users from file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    users_file = os.path.join(script_dir, 'users.txt')
    output_file = os.path.join(script_dir, 'output_bubble.txt')
    users = load_users(users_file)
    
    # Sort users and measure time
    start_time = time.time()
    sorted_users = bubble_sort(users.copy())
    sort_time = time.time() - start_time
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Sorted by Age → First Name → Last Name:\n")
        for user in sorted_users:
            f.write(f"  Age: {user['age']:3}, First Name: {user['first_name']:10}, Last Name: {user['last_name']:10}\n")
        
        f.write(f"\nSort completed in {sort_time:.6f} seconds\n")
    
    print(f"Output written to output_bubble.txt")
    print(f"Sorted {len(users)} users in {sort_time:.6f} seconds")
