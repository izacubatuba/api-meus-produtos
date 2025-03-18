from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

# Configuração do MySQL (Alterar para o banco de dados na nuvem)
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'seu-banco-de-dados-em-nuvem-host.com')  # Variável de ambiente
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')  # Variável de ambiente
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '81100404')  # Variável de ambiente
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'produtos_db')  # Variável de ambiente

mysql = MySQL(app)

@app.route('/produto', methods=['POST'])
def add_produto():
    if not request.is_json:
        return jsonify({"error": "A requisição precisa ser em formato JSON"}), 400
    
    data = request.get_json()
    try:
        cursor = mysql.connection.cursor()
        for produto in data if isinstance(data, list) else [data]:
            categoria = produto.get('categoria')
            cod_barras = produto.get('cod_barras')
            descricao_produto = produto.get('descricao_produto')
            imagem = produto.get('imagem')
            
            cursor.execute("SELECT * FROM produtos WHERE cod_barras = %s", (cod_barras,))
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

@app.route('/produtos', methods=['GET'])
def get_produtos():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM produtos")
        produtos = cursor.fetchall()
        cursor.close()
        return jsonify([{
            "id": p[0], "categoria": p[1], "cod_barras": p[2], "descricao_produto": p[3], "imagem": p[4]} for p in produtos
        ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handler(event, context):
    """Função de entrada para a Vercel."""
    return app(event, context)

if __name__ == '__main__':
    app.run(debug=True)
