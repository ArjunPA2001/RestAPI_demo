from flask import Flask, render_template, g, url_for, redirect, request, jsonify
import mysql.connector
from flasgger import Swagger, swag_from

app = Flask(__name__)
app.app_context().push()
swagger = Swagger(app)

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
        host="host.docker.internal",
        user="root",
        password="pass",
        port = 3333
        )
        with g.db.cursor() as curr:
            curr.execute("use sys;")
        return g.db
    
    else:
        return g.db
    
def execute_procedure(proc,*args, has_crud = False):
    try:
        mydb = get_db()
        with mydb.cursor() as curr:
            curr.callproc(proc,args)
            if has_crud:
                mydb.commit()
            if proc == "DeleteCustomer":
                return {}
            res = next(curr.stored_results())
            result = res.fetchall()
        return result

    except Exception as e:
        print("an exception occured:")
        s = f"%s: %s" % (type(e).__name__,e)
        print(s)
        return {"error_type" : type(e).__name__, "error" : str(e)}

@app.route("/api/customer", methods=["GET","POST","DELETE","PUT"])
@swag_from("../static/swagger_customer_table.yml")
def customer_table_apis():
    if request.method == 'GET':
        print(request)
        data = execute_procedure('GetCustomer',None)
        print(type(data))
        if "error_type" not in data:
            return jsonify({"datas":data})
    elif request.method == 'POST':
        data = request.get_json()
        c_id = data['customer_id']
        c_name = data['customer_name']
        c_type = data['customer_type']
        dt = data['datetime']
        data = execute_procedure('CreateCustomer',c_id,c_name,c_type,dt,has_crud=True)
        if "error_type" not in data:
            return jsonify({'message':f'Customer with id %d Created succesfully'%(data[0][0])})
    elif request.method == 'DELETE':
        data = request.get_json()
        c_id = data['customer_id']
        data = execute_procedure('DeleteCustomer',c_id,has_crud=True)
        if "error_type" not in data:
            return jsonify({'message':f'Customer with id %d Deleted succesfully'%(c_id)})
    elif request.method == 'PUT':
        data = request.get_json()
        c_id = data['customer_id']
        c_name = data['customer_name']
        c_type = data['customer_type']
        dt = data['datetime']
        data = execute_procedure('UpdateCustomer',c_id,c_name,c_type,dt,has_crud=True)
        if "error_type" not in data:
            return jsonify({'message':f'Customer with id %d Updated succesfully'%(data[0][0])})
    return jsonify(data)

@app.route("/api/customer/<int:customer_id>", methods = ["GET"])
@swag_from('../static/swagger_customer_id.yml')
def customer_id_apis(customer_id):
    if request.method == "GET":
        data = execute_procedure('GetCustomer',customer_id)
        if "error_type" not in data:
            return jsonify({"datas":data})
    return jsonify(data)