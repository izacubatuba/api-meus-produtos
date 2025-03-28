from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Isso permite CORS para todas as rotas.

# Configuração do MySQL
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'hcm4e9frmbwfez47.cbetxkdyhwsb.us-east-1.rds.amazonaws.com')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'clojfuq754wxkoul')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'u9jhnosis81qcka8')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'duq208de2k20mv5y')
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

# ------------------ Rota de Carrinho ------------------

carrinho = []  # Lista para armazenar os itens do carrinho

@app.route('/carrinho', methods=['GET', 'POST'])
def gerenciar_carrinho():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({'error': 'A requisição precisa ser em formato JSON'}), 400

        data = request.get_json()
        cod_barras = data.get('cod_barras')
        quantidade = data.get('quantidade', 1)

        if not cod_barras:
            return jsonify({'error': 'Código de barras não fornecido'}), 400

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, categoria, cod_barras, descricao_produto, imagem FROM produtos WHERE cod_barras = %s', (cod_barras,))
        produto = cursor.fetchone()
        cursor.close()

        if produto:
            carrinho.append({
                'id': produto[0],
                'categoria': produto[1],
                'cod_barras': produto[2],
                'descricao_produto': produto[3] or produto[2],
                'imagem': produto[4] if produto[4] and produto[4] != produto[3] else 'placeholder.jpg',
                'quantidade': quantidade
            })
            return jsonify({'message': 'Produto adicionado ao carrinho'}), 201
        else:
            return jsonify({'error': 'Produto não encontrado'}), 404

    return jsonify(carrinho), 200

@app.route('/carrinho/<string:codigo_barras>', methods=['DELETE'])
def deletar_produto_do_carrinho(codigo_barras):
    global carrinho
    carrinho = [item for item in carrinho if item['cod_barras'] != codigo_barras]
    return jsonify({'message': 'Produto removido do carrinho'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
