
import sqlite3
import hashlib
import os
import hmac
from pathlib import Path


# ==========================================
# LIGACAO A BASE DE DADOS
# ==========================================

pasta = Path(__file__).resolve().parent
ficheiro_bd = pasta / "Jogo_aventura_na_floresta.db"

ligacao = sqlite3.connect(ficheiro_bd)
ligacao.execute("PRAGMA foreign_keys = ON")
cursor = ligacao.cursor()


# ==========================================
# CRIAR HASH DA PALAVRA-PASSE
# ==========================================

def criar_hash(palavra_passe, salt=None):
    if salt is None:
        salt = os.urandom(16)

    resultado = hashlib.pbkdf2_hmac(
        "sha256",
        palavra_passe.encode("utf-8"),
        salt,
        200000
    )

    return salt.hex() + ":" + resultado.hex()


# ==========================================
# VERIFICAR PALAVRA-PASSE
# ==========================================

def verificar_hash(palavra_passe, hash_guardado):
    try:
        salt_hex, resultado_guardado = hash_guardado.split(":")
        salt = bytes.fromhex(salt_hex)

        resultado = hashlib.pbkdf2_hmac(
            "sha256",
            palavra_passe.encode("utf-8"),
            salt,
            200000
        )

        return hmac.compare_digest(
            resultado.hex(),
            resultado_guardado
        )

    except (ValueError, TypeError):
        return False


# ==========================================
# REGISTAR UTILIZADOR
# ==========================================

def registar():
    print("\n--- REGISTAR UTILIZADOR ---")

    username = input("Nome de utilizador: ").strip()
    email = input("Email: ").strip()
    palavra_passe = input("Palavra-passe: ")

    # Verificar campos obrigatorios
    if not username or not email or not palavra_passe:
        print("Erro: todos os campos são obrigatórios.")
        return

    # Validar email
    if "@" not in email or "." not in email:
        print("Erro: introduz um email válido.")
        return

    # Validar palavra-passe
    if len(palavra_passe) < 8:
        print("Erro: a palavra-passe deve ter pelo menos 8 caracteres.")
        return

    # Verificar se o nome ja existe
    cursor.execute(
        "SELECT id_utilizador FROM utilizador WHERE username = ?",
        (username,)
    )

    if cursor.fetchone() is not None:
        print("Erro: esse nome de utilizador já existe.")
        return

    # Procurar o tipo Jogador
    cursor.execute(
        "SELECT id_tipo FROM tipo_utilizador WHERE nome_tipo = ?",
        ("Jogador",)
    )

    resultado = cursor.fetchone()

    if resultado is None:
        print("Erro: o tipo Jogador não existe na base de dados.")
        return

    id_tipo = resultado[0]

    # Proteger a palavra-passe
    palavra_passe_hash = criar_hash(palavra_passe)

    # Guardar os dados na base de dados
    try:
        cursor.execute(
            """
            INSERT INTO utilizador
            (id_tipo, username, password_hash, email)
            VALUES (?, ?, ?, ?)
            """,
            (id_tipo, username, palavra_passe_hash, email)
        )

        ligacao.commit()
        print("Conta criada com sucesso!")

    except sqlite3.IntegrityError:
        ligacao.rollback()
        print("Erro: não foi possível criar a conta.")


# ==========================================
# INICIAR SESSAO
# ==========================================

def iniciar_sessao():
    print("\n--- INICIAR SESSÃO ---")

    username = input("Nome de utilizador: ").strip()
    palavra_passe = input("Palavra-passe: ")

    cursor.execute(
        """
        SELECT utilizador.id_utilizador,
               utilizador.password_hash,
               tipo_utilizador.nome_tipo,
               utilizador.ativo
        FROM utilizador
        JOIN tipo_utilizador
        ON utilizador.id_tipo = tipo_utilizador.id_tipo
        WHERE utilizador.username = ?
        """,
        (username,)
    )

    utilizador = cursor.fetchone()

    # Verificar se o utilizador existe
    if utilizador is None:
        print("Erro: nome de utilizador ou palavra-passe incorretos.")
        return

    id_utilizador, hash_guardado, tipo, ativo = utilizador

    # Verificar se a conta esta ativa e a palavra-passe correta
    if ativo != 1 or not verificar_hash(
        palavra_passe, hash_guardado
    ):
        print("Erro: nome de utilizador ou palavra-passe incorretos.")
        return

    print("\nSessão iniciada com sucesso!")
    print("Bem-vindo,", username)
    print("Tipo de utilizador:", tipo)

    if tipo == "Administrador":
        print("Tens o perfil de Administrador.")
    else:
        print("Tens o perfil de Jogador.")

    menu_conta(id_utilizador)


# ==========================================
# MENU DA CONTA
# ==========================================

def menu_conta(id_utilizador):
    while True:
        print("\n--- MENU DA CONTA ---")
        print("1 - Alterar email")
        print("2 - Alterar palavra-passe")
        print("3 - Terminar sessão")

        opcao = input("Escolhe uma opção: ")

        if opcao == "1":
            alterar_email(id_utilizador)

        elif opcao == "2":
            alterar_palavra_passe(id_utilizador)

        elif opcao == "3":
            print("Sessão terminada.")
            break

        else:
            print("Opção inválida. Tenta novamente.")


# ==========================================
# ALTERAR EMAIL
# ==========================================

def alterar_email(id_utilizador):
    novo_email = input("Novo email: ").strip()

    if not novo_email or "@" not in novo_email or "." not in novo_email:
        print("Erro: introduz um email válido.")
        return

    cursor.execute(
        """
        UPDATE utilizador
        SET email = ?
        WHERE id_utilizador = ?
        """,
        (novo_email, id_utilizador)
    )

    ligacao.commit()
    print("Email alterado com sucesso!")


# ==========================================
# ALTERAR PALAVRA-PASSE
# ==========================================

def alterar_palavra_passe(id_utilizador):
    palavra_passe = input("Nova palavra-passe: ")

    if len(palavra_passe) < 8:
        print("Erro: a palavra-passe deve ter pelo menos 8 caracteres.")
        return

    # Criar um novo hash
    novo_hash = criar_hash(palavra_passe)

    cursor.execute(
        """
        UPDATE utilizador
        SET password_hash = ?
        WHERE id_utilizador = ?
        """,
        (novo_hash, id_utilizador)
    )

    ligacao.commit()
    print("Palavra-passe alterada com sucesso!")


# ==========================================
# MENU PRINCIPAL
# ==========================================

def menu_principal():
    while True:
        print("\n==============================")
        print("     AVENTURA NA FLORESTA")
        print("==============================")
        print("1 - Registar utilizador")
        print("2 - Iniciar sessão")
        print("3 - Sair")

        opcao = input("Escolhe uma opção: ")

        if opcao == "1":
            registar()

        elif opcao == "2":
            iniciar_sessao()

        elif opcao == "3":
            print("Até à próxima!")
            break

        else:
            print("Opção inválida. Tenta novamente.")


# ==========================================
# EXECUTAR O PROGRAMA
# ==========================================

try:
    menu_principal()

finally:
    ligacao.close()
