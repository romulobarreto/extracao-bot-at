def clean_key_column(col):
    """
    Padroniza colunas de chave (INSTALACAO, MEDIDOR, etc)

    - converte para string
    - remove .0
    - remove espaços
    """
    return (
        col.astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
    )


def clean_numeric_column(col):
    return (
        col.astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
    )
