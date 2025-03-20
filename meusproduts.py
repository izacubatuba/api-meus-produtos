from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import os
from flask_cors import CORS
from urllib.parse import unquote

app = Flask(__name__)
CORS(app)

# Configuração do MySQL
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', '127.0.0.1')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '81100404')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'produtos_db')

mysql = MySQL(app)

# Rota para adicionar ou atualizar produtos
@app.route('/produto', methods=['POST'])
def add_produto():
    if not request.is_json:
        return jsonify({"error": "A requisição precisa ser em formato JSON"}), 400
    
    data = request.get_json()
    print("Recebido JSON:", data)  # Log para depuração
    
    try:
        cursor = mysql.connection.cursor()
        for produto in data if isinstance(data, list) else [data]:
            categoria = produto.get('categoria', 'Desconhecida')
            cod_barras = produto.get('cod_barras')
            descricao_produto = produto.get('descricao_produto', cod_barras)
            imagem = produto.get('imagem', 'placeholder.jpg')  # Garantindo que a imagem não seja a descrição
            
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
        return jsonify({"error": str(e)}), 500

# Rota para listar todos os produtos
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
            "imagem": p[4] if p[4] and p[4] != p[3] else "placeholder.jpg"  # Garante que a imagem não seja a descrição
        } for p in produtos]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota para buscar um produto específico pelo código de barras
@app.route('/produto/<codigo_barras>', methods=['GET'])
def get_produto(codigo_barras):
    try:
        codigo_barras = unquote(codigo_barras)  # Caso o código de barras venha codificado
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, categoria, cod_barras, descricao_produto, imagem FROM produtos WHERE cod_barras = %s", (codigo_barras,))
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
        return jsonify({"error": str(e)}), 500

# Rota para atualizar um produto específico pelo código de barras
@app.route('/produto/<codigo_barras>', methods=['PUT'])
def atualizar_produto(codigo_barras):
    if not request.is_json:
        return jsonify({"error": "A requisição precisa ser em formato JSON"}), 400
    
    data = request.get_json()
    print("Atualizando produto com código de barras:", codigo_barras)
    
    try:
        cursor = mysql.connection.cursor()
        categoria = data.get('categoria', 'Desconhecida')
        descricao_produto = data.get('descricao_produto', codigo_barras)
        imagem = data.get('imagem', 'placeholder.jpg')

        cursor.execute(
            "UPDATE produtos SET categoria = %s, descricao_produto = %s, imagem = %s WHERE cod_barras = %s",
            (categoria, descricao_produto, imagem, codigo_barras)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Produto não encontrado"}), 404
        
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Produto atualizado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota para deletar um produto específico pelo código de barras
@app.route('/produto/<codigo_barras>', methods=['DELETE'])
def delete_produto(codigo_barras):
    try:
        # Decodificando o código de barras caso ele venha codificado
        codigo_barras = unquote(codigo_barras)

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM produtos WHERE cod_barras = %s", (codigo_barras,))
        produto = cursor.fetchone()

        if produto:
            cursor.execute("DELETE FROM produtos WHERE cod_barras = %s", (codigo_barras,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "Produto excluído com sucesso!"}), 200
        else:
            return jsonify({"error": "Produto não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
