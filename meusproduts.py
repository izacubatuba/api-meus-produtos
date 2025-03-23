from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuração do MySQL
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', '127.0.0.1')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '81100404')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'produtos_db')

mysql = MySQL(app)

# ------------------ Endpoints de Produtos ------------------

@app.route('/produto', methods=['POST'])
def add_produto():
    if not request.is_json:
        return jsonify({"error": "A requisição precisa ser em formato JSON"}), 400
    
    data = request.get_json()
    print("Recebido JSON:", data)

    try:
        cursor = mysql.connection.cursor()
        for produto in data if isinstance(data, list) else [data]:
            categoria = produto.get('categoria', 'Desconhecida')
            cod_barras = produto.get('cod_barras')
            descricao_produto = produto.get('descricao_produto', cod_barras)
            imagem = produto.get('imagem', 'placeholder.jpg')

            print(f"Salvando no BD - Categoria: {categoria}, Código: {cod_barras}, Descrição: {descricao_produto}, Imagem: {imagem}")

            cursor.execute("SELECT id FROM produtos WHERE cod_barras = %s", (cod_barras,))
            if cursor.fetchone():
                cursor.execute(
                    "UPDATE produtos SET categoria = %s, descricao_produto = %s, imagem = %s WHERE cod_barras = %s",
                    (categoria, descricao_produto, imagem, cod_barras)
                )
            else:
                cursor.execute(
                    "INSERT INTO produtos (categoria, cod_barras, descricao_produto, imagem) VALUES (%s, %s, %s, %s)",
                    (categoria, cod_barras, descricao_produto, imagem)
                )
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Produtos adicionados ou atualizados com sucesso!"}), 201
    except Exception as e:
        print(f"Erro ao adicionar ou atualizar produto: {str(e)}")  # Log do erro
        return jsonify({"error": str(e)}), 500

@app.route('/produtos', methods=['GET'])
def get_produtos():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, categoria, cod_barras, descricao_produto, imagem FROM produtos")
        produtos = cursor.fetchall()
        cursor.close()
        
        return jsonify([{
            "id": p[0], 
            "categoria": p[1] or "Desconhecida", 
            "cod_barras": p[2], 
            "descricao_produto": p[3] or p[2],
            "imagem": p[4] if p[4] and p[4] != p[3] else "placeholder.jpg"
        } for p in produtos]), 200
    except Exception as e:
        print(f"Erro ao buscar produtos: {str(e)}")  # Log do erro
        return jsonify({"error": str(e)}), 500

@app.route('/produto/<cod_barras>', methods=['GET'])
def get_produto(cod_barras):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, categoria, cod_barras, descricao_produto, imagem FROM produtos WHERE cod_barras = %s", (cod_barras,))
        produto = cursor.fetchone()
        cursor.close()

        if produto:
            return jsonify({
                "id": produto[0],
                "categoria": produto[1] or "Desconhecida",
                "cod_barras": produto[2],
                "descricao_produto": produto[3] or produto[2],
                "imagem": produto[4] if produto[4] and produto[4] != produto[3] else "placeholder.jpg"
            }), 200
        else:
            return jsonify({"error": "Produto não encontrado"}), 404
    except Exception as e:
        print(f"Erro ao buscar produto: {str(e)}")  # Log do erro
        return jsonify({"error": str(e)}), 500

# ------------------ Novo Endpoint: Atualizar Produto ------------------
@app.route('/produto/<cod_barras>', methods=['PUT'])
def update_produto(cod_barras):
    if not request.is_json:
        return jsonify({"error": "A requisição precisa ser em formato JSON"}), 400
    
    data = request.get_json()
    try:
        cursor = mysql.connection.cursor()
        
        categoria = data.get('categoria')
        descricao_produto = data.get('descricao_produto')
        imagem = data.get('imagem')

        cursor.execute("SELECT id FROM produtos WHERE cod_barras = %s", (cod_barras,))
        if cursor.fetchone():
            cursor.execute(
                "UPDATE produtos SET categoria = %s, descricao_produto = %s, imagem = %s WHERE cod_barras = %s",
                (categoria, descricao_produto, imagem, cod_barras)
            )
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "Produto atualizado com sucesso!"}), 200
        else:
            cursor.close()
            return jsonify({"error": "Produto não encontrado"}), 404
    except Exception as e:
        print(f"Erro ao atualizar produto: {str(e)}")  # Log do erro
        return jsonify({"error": str(e)}), 500

# ------------------ Novo Endpoint: Deletar Produto ------------------
@app.route('/produto/<cod_barras>', methods=['DELETE'])
def delete_produto(cod_barras):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM produtos WHERE cod_barras = %s", (cod_barras,))
        produto = cursor.fetchone()

        if produto:
            cursor.execute("DELETE FROM produtos WHERE cod_barras = %s", (cod_barras,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "Produto deletado com sucesso!"}), 200
        else:
            cursor.close()
            return jsonify({"error": "Produto não encontrado"}), 404
    except Exception as e:
        print(f"Erro ao deletar produto: {str(e)}")  # Log do erro
        return jsonify({"error": str(e)}), 500

# ------------------ Endpoints de Fornecedores ------------------

@app.route('/fornecedores', methods=['GET'])
def get_fornecedores():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, nome_vendedor, nome_empresa, contato FROM fornecedores")
        fornecedores = cursor.fetchall()
        cursor.close()
        
        return jsonify([{
            "id": f[0],
            "nome_vendedor": f[1],
            "nome_empresa": f[2],
            "contato": f[3]
        } for f in fornecedores]), 200
    except Exception as e:
        print(f"Erro ao buscar fornecedores: {str(e)}")  # Log do erro
        return jsonify({"error": str(e)}), 500

@app.route('/fornecedor', methods=['POST'])
def add_fornecedor():
    if not request.is_json:
        return jsonify({"error": "A requisição precisa ser em formato JSON"}), 400
    
    data = request.get_json()
    print("Recebido JSON:", data)

    try:
        cursor = mysql.connection.cursor()
        
        fornecedores = data if isinstance(data, list) else [data]

        for fornecedor in fornecedores:
            nome_vendedor = fornecedor.get('nome_vendedor')
            nome_empresa = fornecedor.get('nome_empresa')
            contato = fornecedor.get('contato')

            if not nome_vendedor or not nome_empresa or not contato:
                return jsonify({"error": "Todos os campos são obrigatórios"}), 400

            cursor.execute(
                "INSERT INTO fornecedores (nome_vendedor, nome_empresa, contato) VALUES (%s, %s, %s)",
                (nome_vendedor, nome_empresa, contato)
            )

        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Fornecedor(es) adicionados com sucesso!"}), 201

    except Exception as e:
        print(f"Erro ao adicionar fornecedor: {str(e)}")  # Log do erro
        return jsonify({"error": str(e)}), 500

# ------------------ Novo Endpoint: Buscar Fornecedor por ID ------------------
@app.route('/fornecedor/<int:id>', methods=['GET'])
def get_fornecedor(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, nome_vendedor, nome_empresa, contato FROM fornecedores WHERE id = %s", (id,))
        fornecedor = cursor.fetchone()
        cursor.close()

        if fornecedor:
            return jsonify({
                "id": fornecedor[0],
                "nome_vendedor": fornecedor[1],
                "nome_empresa": fornecedor[2],
                "contato": fornecedor[3]
            }), 200
        else:
            return jsonify({"error": "Fornecedor não encontrado"}), 404
    except Exception as e:
        print(f"Erro ao buscar fornecedor: {str(e)}")  # Log do erro
        return jsonify({"error": str(e)}), 500

# ------------------ Novo Endpoint: Atualizar Fornecedor ------------------
@app.route('/fornecedor/<int:id>', methods=['PUT'])
def update_fornecedor(id):
    if not request.is_json:
        return jsonify({"error": "A requisição precisa ser em formato JSON"}), 400
    
    data = request.get_json()
    try:
        cursor = mysql.connection.cursor()

        # Extrai os dados que podem ser atualizados
        nome_vendedor = data.get('nome_vendedor')
        nome_empresa = data.get('nome_empresa')
        contato = data.get('contato')

        # Verifica se o fornecedor existe no banco de dados
        cursor.execute("SELECT id FROM fornecedores WHERE id = %s", (id,))
        fornecedor = cursor.fetchone()

        if fornecedor:
            # Atualiza o fornecedor no banco de dados
            cursor.execute(
                "UPDATE fornecedores SET nome_vendedor = %s, nome_empresa = %s, contato = %s WHERE id = %s",
                (nome_vendedor, nome_empresa, contato, id)
            )
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "Fornecedor atualizado com sucesso!"}), 200
        else:
            cursor.close()
            return jsonify({"error": "Fornecedor não encontrado"}), 404
    except Exception as e:
        print(f"Erro ao atualizar fornecedor: {str(e)}")  # Log do erro
        return jsonify({"error": str(e)}), 500

# ------------------ Novo Endpoint: Deletar Fornecedor ------------------
@app.route('/fornecedor/<int:id>', methods=['DELETE'])
def delete_fornecedor(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM fornecedores WHERE id = %s", (id,))
        fornecedor = cursor.fetchone()

        if fornecedor:
            cursor.execute("DELETE FROM fornecedores WHERE id = %s", (id,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "Fornecedor deletado com sucesso!"}), 200
        else:
            cursor.close()
            return jsonify({"error": "Fornecedor não encontrado"}), 404
    except Exception as e:
        print(f"Erro ao deletar fornecedor: {str(e)}")  # Log do erro
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
