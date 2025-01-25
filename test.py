# Taxa de juros anual em formato decimal (por exemplo, 12% = 0.12)
taxa_anual = 0.12

# Calculando a taxa de juros mensal
taxa_mensal = (1 + taxa_anual) ** (1 / 12) - 1

# Exibindo o resultado em formato percentual
print(f"Taxa de juros mensal equivalente: {taxa_mensal * 100:.2f}%")
