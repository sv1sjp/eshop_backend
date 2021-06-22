#####################################################################################################################
from pymongo import MongoClient
import pymongo
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time
from bson import json_util
from bson.objectid import ObjectId

#####################################################################################################################

# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Choose database
db = client['DSMarkets']

# Choose collections
users = db['users']
products = db['products']

# Initiate Flask App
app = Flask(__name__)

users_sessions = {}
cart=[]


#####################################################################################################################

def create_session(email):
    user_uuid = str(uuid.uuid1())
    users_sessions[user_uuid] = (email, time.time())
    return user_uuid  

def is_session_valid(user_uuid):
    return user_uuid in users_sessions



#####################################################################################################################


#####################################################################################################################

# CreateUser 

@app.route('/createUser', methods=['POST'])
def create_user():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "name" in data or not "password" in data or  not "email" in data :
        return Response("Information incomplete",status=500,mimetype="application/json")

    
    if  users.find({"email": data["email"]}).count()==0:
            users.insert_one({"email": data["email"], "name": data["name"] , "password": data["password"] , "category": "user"})
            return Response(data['email']+" was added to the MongoDB",status=200, mimetype='application/json') 
    else:
        return Response("A user with the given email already exists",status=400, mimetype='application/json')
    

#####################################################################################################################



#####################################################################################################################

#Login 

@app.route('/login', methods=['POST'])
def login():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

   
    #Search if email exists
    if users.find_one({"email" : data["email"], "password" : data["password"]}):
        
    
        uuid1=create_session(data["email"])
        screen = {"uuid": uuid1, "email": data['email']}
        return Response(json.dumps(screen),status=200, mimetype='application/json')

    else:
        return Response("Wrong username or password.",status=400,mimetype='application/json') 

#####################################################################################################################

#####################################################################################################################

#  By Name
@app.route('/getProduct/byname', methods=['GET'])
def get_byname():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "name" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

   

    uuid = request.headers.get('authorization')
    #check uuid
    check=is_session_valid(uuid)


    if check==True:
        data = json.loads(request.data)
        if  products.find({"name": data['name']}).count()==1:
           
            rpr= products.find({'name':data['name']}).sort([("name", pymongo.ASCENDING)])
            something=json.loads(json_util.dumps(rpr))
            return Response(json.dumps(something), status=200, mimetype='application/json')
        else:
            return Response("No product found" , status=400,mimetype='application/json')
             
    else:

        return Response("This user hasn't been authorized", status=401,mimetype='application/json')
#####################################################################################################################


# Return and sort from category
@app.route('/getProduct/bycategory', methods=['GET'])
def gsort_category():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "category" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

   

    uuid = request.headers.get('authorization')
    #check uuid
    check=is_session_valid(uuid)


    if check==True:
        data = json.loads(request.data)
        if  products.find({'category': data['category']}).count()>=1:
            pr= products.find({'category':data['category']}).sort([("price", pymongo.ASCENDING)])
            something=json.loads(json_util.dumps(pr))
            return Response(json.dumps(something), status=200, mimetype='application/json')
        else:
            return Response("No product found" , status=400,mimetype='application/json')
             
    else:

        return Response("This user hasn't been authorized", status=401,mimetype='application/json')
#####################################################################################################################

# Return from id
@app.route('/getProduct/byid', methods=['GET'])
def return_id():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "_id" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

   

    uuid = request.headers.get('authorization')
    #check uuid
    check=is_session_valid(uuid)


    if check==True:
        data = json.loads(request.data)
        if  products.find({"_id": ObjectId(data['_id'])}).count()==1:

            aw= products.find({"_id":ObjectId(data["_id"])})
            something=json.loads(json_util.dumps(aw))
            return Response(json.dumps(something), status=200, mimetype='application/json')
        else:
            return Response("No product found" , status=401,mimetype='application/json')
             
    else:

        return Response("This user hasn't been authorized", status=401,mimetype='application/json')
#####################################################################################################################




#####################################################################################################################
 #Add product in cart
@app.route('/addincart', methods=['GET'])
def addInCart():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "_id" in data or not "stock" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

   


    uuid=request.headers.get("authorization")
    check=is_session_valid(uuid)

    if check==True:
        
            t=products.find({"_id" : ObjectId(data['_id'])})


            if check==True:

                key=False
                i=0
                while i<len(cart) and i>=0:
                    if data['_id']==cart[i]['_id']:
                        location=i
                        key=True
                        i=-2
                    i=i+1




            if t.count()==0:
                return Response("No products found.", status=400, mimetype='application/json')
            else:
                #Update our db
                if int(t[0]['stock'])>=int(data['stock']) and key==False:
                    cart.append({"_id": data['_id'], "name": t[0]['name'] , "stock" : data['stock'] , 'price' : t[0]['price'] })
                    return Response("Added Successfully in cart", status=200, mimetype='application/json')
                elif key==True:
                    if int(t[0]['stock'])>= (((int(data['stock'])) + int(cart[location]['stock']))):
                        cart[location]['stock']=int(data['stock'])+int(cart[location]['stock'])

                    
                    
                    
                    return Response("Added Successfully in cart", status=200, mimetype='application/json')
                else:
                    return Response("Product not found", status=400, mimetype='application/json')
        


           

            
    else: 
        return Response("You have to login first.", status=401, mimetype='application/json')

#####################################################################################################################

 #Remove product from cart
@app.route('/removeincart', methods=['GET'])
def removeFromCart():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "_id":
        return Response("Information incomplete",status=500,mimetype="application/json")

   


    uuid=request.headers.get("authorization")
    check=is_session_valid(uuid)

    if check==True:
        
                t=products.find_one({"_id" : ObjectId(data['_id'])})

                key=False
                for item in cart:
                    if data['_id']==item['_id']:
                        key=True

            
                if len(t.keys())==0 or key==False :
                    return Response("No products found.", status=400, mimetype='application/json')
                else:
                    i=0
                    while i<len(cart) and i>=0:
                        if data['_id']==cart[i]['_id']:
                            cart.pop(i)
                            i=-1
                        else:
                            i=i+1

                    
                    return Response("Successfully removed from cart", status=200, mimetype='application/json')


                for i in cart:
                    total_cost= total_cost + int(cart[i]['stock'])*float(cart[i]['price'])
               
        


           

            
    else: 
        return Response("You have to login first.", status=401, mimetype='application/json')

#####################################################################################################################



#####################################################################################################################
 #Show all products in cart
@app.route('/showincart', methods=['GET'])
def showInCart():
    global cart
    uuid=request.headers.get("authorization")
    check=is_session_valid(uuid)
    total_cost=0
    if check==True:
        for item in cart:
            total_cost= total_cost + int(item['stock'])*float(item['price'])


        return Response("List" + str(cart) + "\n Total Cost is : " +str(total_cost),  status=401, mimetype='application/json')
    else:
        return Response("You have to login first.", status=401, mimetype='application/json')


#####################################################################################################################

#####################################################################################################################
 #Buy
@app.route('/buy', methods=['POST'])
def buying():

    uuid=request.headers.get("authorization")
    check=is_session_valid(uuid)

    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "card":
        return Response("Information incomplete",status=500,mimetype="application/json")

    if check==True:
        
                #Update our db
                
                if int(data["card"]) >= 1000000000000000 or int(data["card"]) <=9999999999999999:
                    #view all purchased items and total cost
                    users.update_one({"email" : users_sessions[uuid][0]}, {'$set': {'history' : cart}})
                    for item in cart:

                        w=products.find_one({"_id" : ObjectId(item['_id'])})
                        prod= int(w['stock']) -int(item['stock'])

                        products.update_one({"_id" : ObjectId(item['_id'])}, {'$set': {'stock' : prod }})
                    cart.clear()
                    return Response("Card is accepted. Thank you!!!", status=200, mimetype='application/json')
                else:
                    return Response("Invalid card.", status=400, mimetype='application/json')

            
            
    else: 
        return Response("You have to login first.", status=401, mimetype='application/json')

#####################################################################################################################

#####################################################################################################################
 #Show history
@app.route('/history', methods=['GET'])
def showhistory():

    uuid=request.headers.get("authorization")
    check=is_session_valid(uuid)
    
    if check==True:
       
        x=users.find_one({'email' : users_sessions[uuid][0]})


        return Response( str(x['products']),  status=401, mimetype='application/json')
    else:
        return Response("You have to login first.", status=401, mimetype='application/json')


#####################################################################################################################


#####################################################################################################################
    # Remove user
@app.route('/deleteuser', methods=['DELETE'])
def delete_user():
    # Request JSON data



    uuid = request.headers.get('authorization')
    check=is_session_valid(uuid)

    if check==True:
        
        
        users.delete_one({"email" : users_sessions[uuid][0]})
        users_sessions.pop(uuid)
        cart.clear()

        return Response("User has been removed Successfully", status=200, mimetype='application/json')
        
            

    else:

        return Response("This user hasn't been authorized", status=401,mimetype='application/json')


#####################################################################################################################


#####################################################################################################################

#ADMINISTATOR FUNCTIONS
#####################################################################################################################

# Add products
@app.route('/addProducts', methods=['POST'])
def add_products():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "name" in data or not "price" in data or not "description" in data or not "category" in data or not "stock" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

   


    uuid = request.headers.get('authorization')
    #check uuid
    check=is_session_valid(uuid)
    newmail=users_sessions[uuid][0]
    x=users.find_one({'email' : newmail})
    if check==True and x['category']=="admin":
        products.insert_one({"name": data["name"] , "price": data["price"] , "description": data["description"] , "category": data["category"] , "stock": data["stock"]})
            
        return Response("Successfully imported", status=200, mimetype='application/json')
    else: 
        return Response("You have to login first.", status=401, mimetype='application/json')

#####################################################################################################################

#####################################################################################################################
    # Remove Product via id
@app.route('/removeid', methods=['DELETE'])
def delete_product():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "_id" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")



    uuid = request.headers.get('authorization')
    #check uuid
    check=is_session_valid(uuid)
    newmail=users_sessions[uuid][0]
    x=users.find_one({'email' : newmail})
    if check==True and x['category']=="admin":
       
        if  products.find({"_id": ObjectId(data['_id'])}).count()==1:
           
            products.delete_one({"_id": ObjectId(data['_id'])})
            msg= "User" + str(products['name']) + "has been removed"


            return Response(msg, status=200, mimetype='application/json')
        else:
            msg="This Product can't be found"
            return Response(msg , status=401,mimetype='application/json')
            

    else:

        return Response("This user hasn't been authorized", status=401,mimetype='application/json')


#####################################################################################################################



# Edit products
@app.route('/patchproducts', methods=['PATCH'])
def patch_products():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if  not( "_id" in data) and not ( "name" in data or  "price" in data or "category" in data or "stock" in data or "description" in data):
        return Response("Information incomplete",status=500,mimetype="application/json")

   


    uuid = request.headers.get('authorization')
    #check uuid
    check=is_session_valid(uuid)
    newmail=users_sessions[uuid][0]
    x=users.find_one({'email' : newmail})
    if check==True and x['category']=="admin":
        z=products.find_one({"_id" : ObjectId(data['_id'])})
        if z[ '_id'] in data:
            return Response("This Product can't be found.", status=400, mimetype='application/json')
        else:
            #Update our db
            if "name" in data:
                products.update_one({'name':z['name']}, {'$set' : {"name": data['name']}})
            if "price" in data:
                products.update_one({'price':z['price']}, {'$set' : {"price": data['price']}})
            if "description" in data:
                products.update_one({{'description':z['description']}}, {'$set' : {"description": data['description']}})
            if "category" in data:
                products.update_one({{'category':z['category']}, {'$set' : {"category": data['category']}}})
            if "stock" in data:
                products.update_one({'stock':z['stock']}, {'$set' : {"stock": data['stock']}})
            
            return Response("Successfully modified", status=200, mimetype='application/json')
    else: 
        return Response("You have to login first.", status=401, mimetype='application/json')

#####################################################################################################################




#####################################################################################################################
# Run flask in debugging mode in port 5000
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)