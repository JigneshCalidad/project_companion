"""Module A - Sample Python module for testing."""

import os
from typing import List, Optional


def calculate_sum(numbers: List[int]) -> int:
    """Calculate the sum of a list of numbers.
    
    Args:
        numbers: List of integers
        
    Returns:
        Sum of all numbers
    """
    return sum(numbers)


def calculate_average(numbers: List[int]) -> float:
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


class Calculator:
    """A simple calculator class."""
    
    def __init__(self, initial_value: int = 0):
        """Initialize calculator with an initial value."""
        self.value = initial_value
    
    def add(self, number: int) -> int:
        """Add a number to the current value."""
        self.value += number
        return self.value
    
    def multiply(self, number: int) -> int:
        """Multiply the current value by a number."""
        self.value *= number
        return self.value
    
    def reset(self):
        """Reset the calculator to zero."""
        self.value = 0


# TODO: Add division and subtraction methods
# FIXME: Handle overflow cases

def main():
    """Main entry point."""
    calc = Calculator(10)
    result = calc.add(5)
    print(f"Result: {result}")


if __name__ == "__main__":
    main()

