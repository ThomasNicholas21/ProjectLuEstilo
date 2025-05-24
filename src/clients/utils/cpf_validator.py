import re


def cpf_validador(cpf: str):
    if not cpf.isdigit():
        cpf = re.sub(r'\D', '', cpf)
    
    if not cpf.isdigit():
        return False

    if len(cpf) != 11:
        return False

    if cpf == cpf[::-1]:
        return False
            
    
    novo_cpf1 = cpf[:9]
    novo_cpf2 = novo_cpf1 + str(avaliador1(novo_cpf1))
    novo_cpf3 = novo_cpf2 + str(avaliador2(novo_cpf2))

    if novo_cpf3 != cpf:
        return False
    
    return True
            
    
def avaliador1(argumentos):
    total = 0
    reverso = 10
    for i in argumentos:
        total += int(i) * reverso
        reverso -= 1
    
    digito = (total * 10) % 11
    digito = digito if digito <= 9 else 0
    return digito

def avaliador2(argumentos):
    total = 0
    reverso = 11
    for i in argumentos:
        total += int(i) * reverso
        reverso -= 1
    
    digito = (total * 10) % 11
    digito = digito if digito <= 9 else 0
    return digito