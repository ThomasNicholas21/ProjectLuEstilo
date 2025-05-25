import re

def cpf_validator(cpf: str):
    if not cpf.isdigit():
        cpf = re.sub(r'\D', '', cpf)
    
    if not cpf.isdigit():
        return False

    if len(cpf) != 11:
        return False

    if cpf == cpf[::-1]:
        return False

    base_cpf = cpf[:9]
    cpf_with_first_digit = base_cpf + str(first_digit_evaluator(base_cpf))
    cpf_with_second_digit = cpf_with_first_digit + str(second_digit_evaluator(cpf_with_first_digit))

    if cpf_with_second_digit != cpf:
        return False

    return True

def first_digit_evaluator(numbers):
    total = 0
    reverse = 10
    for n in numbers:
        total += int(n) * reverse
        reverse -= 1

    digit = (total * 10) % 11
    digit = digit if digit <= 9 else 0
    return digit

def second_digit_evaluator(numbers):
    total = 0
    reverse = 11
    for n in numbers:
        total += int(n) * reverse
        reverse -= 1

    digit = (total * 10) % 11
    digit = digit if digit <= 9 else 0
    return digit
