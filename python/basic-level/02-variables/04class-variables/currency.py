pesos = int(input("Valor de peso: "))
solas = int(input("Valor de solas: "))
reais = int(input("Valor de reais: "))
cop_para_usd = pesos * 0.00025
pen_para_usd = solas * 0.27
brl_para_usd = reais * 0.19

total_usd = cop_para_usd + pen_para_usd + brl_para_usd
print(total_usd)