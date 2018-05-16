from flask import Flask , render_template,redirect,jsonify
from flask import request
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
from flask_cors import CORS
import paho.mqtt.publish as publish
broker="iot.eclipse.org"



app = Flask(__name__)
CORS(app)
client = MongoClient('localhost:27017')
db=client.smart_trolley
@app.route('/')
def hello_world():
    url = request.url_root
    return render_template("login.html")

@app.route('/layout')
def layout():
    url = request.url_root
    return render_template("product_add.html")

@app.route('/products/<type>', methods = ['POST', 'GET'])
@app.route('/products/<type>/<id>', methods = ['POST', 'GET'])
def products(type= None, id= None): 
    url = request.url_root
    if type=="add":
        if request.method == 'POST':
            page= "product_add.html"
            result=request.form
            

            db.products.insert_one({"name":result['product_name'],"price":result['price'],"quantity":result['quantity'],"unit":result['unit'],"rfid":result['rfid']})
            # for key ,value in result.items():
            #     print(value)
        else: 
            page= "product_add.html"

    elif type=="edit":
        page = "product_edit.html"
    elif type=="list":
        res = db.products.find({})
        return render_template("product_list.html",datas=res)
    elif type=="delete":
        res = db.products.delete_one({'_id': ObjectId(id)})
        return redirect(url+"products/list")

    return render_template(page)

        
@app.route('/sell/<type>',methods = ['POST', 'GET'])
@app.route('/sell/<type>/<id>',methods = ['POST', 'GET'])
def sell(type= None, id= None):
    url = request.url_root
    if type=="add":
        return render_template("sell_add.html",root_url=url)


    elif type=="edit":
        page = "product_edit.html"
    elif type=="pay":
        if request.method == 'POST':
            
            result=request.form
            
            data= db.invoice.insert_one({"trolle_id":result['pay_trolley_id'],"amount":result['amount'],"paid":result['paid'],"return":result['return']})
            result = db.trolley_items .delete_one({'trolley_id': result['pay_trolley_id']})
            publish.single("smart","0",qos=0,hostname=broker)
            return render_template("sell_add.html",root_url=url)
    return render_template(page)


@app.route('/trolley_items/<type>')
@app.route('/trolley_items/<type>/<id>')
def trolley(type=None ,id= None):
    # res = db.trolley_items.update({'trolley_id': '121212'} , {'$push': {'items': {'pname':'ss','price':'12'}}}, upsert = True)
    

    if type=="get":
        res =get_trolley_items(id)

        return res

    return "ss"
    
def get_trolley_items(id):
    res =db.trolley_items.find_one({'trolley_id':id})
    return dumps(res)

@app.route('/track_trolley_items/')
def track_trolley_items():
    
    url = request.url_root
    return render_template("track_trolley.html",root_url=url)

@app.route('/tm/')
def tm():
    
    url = request.url_root
    return render_template("track_trolley_mobile.html",root_url=url)

@app.route('/trolley/<trolley_id>',methods = ['POST', 'GET'])
def sensor(trolley_id=None):
    if request.method == 'POST':
        content = request.json
        rfid= content['value']
                        
        data = db.products.find_one({'rfid' : str(rfid)})
        price = '0'
        item = ''
        if data == None:
            price='0'
            item= "Item not Exist"
        else:
            price=data["price"]
            item=data["name"]
            res = db.trolley_items.update({'trolley_id': str(trolley_id) } , {'$push': {'items': {'pname':data["name"],'price':data["price"],'quantity':data["quantity"],'unit':data["unit"]}}}, upsert = True)
        response= (price + "," + item)
        
        # print(response)
        return response

if __name__ == '__main__':
   app.run(host ='0.0.0.0',debug = True)    