def add_two_numbers(query: str) -> int:
    """Adds two numbers and returns the sum."""
    # Handle both comma and plus formats
    if '+' in query:
        numbers = query.split('+')
    else:
        numbers = query.split(',')
    
    a = int(numbers[0].strip())
    b = int(numbers[1].strip())
    return a + b