def add(a, b):
    """
    Adds two numbers together.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The sum of the two numbers.
    """
    return a + b

def subtract(a, b):
    """
    Subtracts the second number from the first number.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The result of subtracting b from a.
    """
    return a - b

def multiply(a, b):
    """
    Multiplies two numbers.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The product of the two numbers.
    """
    return a * b

def divide(a, b):
    """
    Divides the first number by the second number.

    Args:
        a (int or float): The numerator (the number to be divided).
        b (int or float): The denominator (the number by which to divide).

    Returns:
        int or float: The result of the division if b is not zero.
        str: A message indicating that division by zero is not allowed if b is zero.

    Raises:
        ZeroDivisionError: If b is zero and the function is expected to throw an exception instead of returning a string.
    """
    if b == 0:
        raise ZeroDivisionError("Division by zero is not allowed.")  # raise exception here
    return a / b

def process_command(command, a, b):
    """
    Processes a command string and calls the appropriate functions.

    Args:
        command (str): The user's command describing the desired operation.
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        dict: A dictionary containing the results of the operations.
    """
    operations = {
        "add": add,
        "subtract": subtract,
        "multiply": multiply,
        "divide": divide
    }
    command = command.lower()
    results = {}
    if "add" in command:
        results["add"] = add(a, b)
    if "subtract" in command:
        results["subtract"] = subtract(a, b)
    if "multiply" in command:
        results["multiply"] = multiply(a, b)
    if "divide" in command:
        try:
            results["divide"] = divide(a, b)
        except ZeroDivisionError as e:
            results["divide"] = str(e)
    if not results: 
        results["error"] = "No valid operation found in the command."
    return results



