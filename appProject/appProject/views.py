import pymysql
from django.shortcuts import render
from django.core.files.base import ContentFile
import random
from Mail import send_email
from django.core.files.storage import default_storage

import os


APP_ROOT = os.path.dirname(os.path.abspath(os.curdir))
APP_ROOT = APP_ROOT + "/appProject/app/static/pictures"


conn = pymysql.connect(host="localhost", user="root", password="root", db="Shopping")
cursor = conn.cursor()


def index(request):
    return render(request, 'index.html')

def alogin(request):
    return render(request, 'alogin.html')

def blogin(request):
    print('hi3')
    return render(request, 'blogin.html')

def alogin1(request):
    Username = request.POST.get('Username', None)
    Password = request.POST.get('Password', None)
    if Username == 'admin@gmail.com' and Password == 'admin':
        request.session['admin'] = "admin"
        return render(request, 'admin.html',{'request':request})
    else:
        return render(request, "msg.html", {"message": 'Invalid Login Details', 'color': 'text-danger'})


def admin(request):
    return render(request, "admin.html")


def bLogin1(request):
    email = request.POST.get('email',None)
    print(email)
    otp = random.randint(1000, 10000)
    print(otp)
    a = cursor.execute("select * from Buyer where email='"+str(email)+"'")
    send_email("Online Shopping", "Use This OTP " + str(otp) + " To Login Your Account", email)
    if a > 0:
        return render(request, 'loginWithOtp.html', {"email": email, "otp": otp})
    else:
        return render(request, 'buyerReg.html',{"email":email,"otp":otp})



def buyReg1(request):
    email = request.POST.get('email',None)
    otp = request.POST.get('otp', None)
    otp2 = request.POST.get('otp2', None)
    name = request.POST.get('name', None)
    phone = request.POST.get('phone',None)
    address = request.POST.get('address',None)
    if otp2 == otp:
        cursor.execute("insert into Buyer (name,email,phone,address) values('"+str(name)+"','"+str(email)+"','"+str(phone)+"','"+str(address)+"')")
        conn.commit()
        Buyer_id = cursor.lastrowid
        request.session['Buyer_id'] = Buyer_id
        request.session['Buyer'] = "Buyer"

        return render(request,"Buyer.html",{'request':request})
    else:
        return render(request, "msg.html",{"message":'Invalid Otp','color':'text-danger'})


def loginWithOtp1(request):
    email = request.POST.get('email', None)
    otp = request.POST.get('otp', None)
    otp2 = request.POST.get('otp2', None)
    if otp2 == otp:
        cursor.execute("select * from Buyer where email='" + str(email) + "'")
        details = cursor.fetchall()
        Buyer_id = details[0][0]
        request.session['Buyer_id'] = Buyer_id
        request.session['Buyer'] = "Buyer"
        return render(request,"Buyer.html",{'request':request})
    else:
        return render(request, "msg.html",{"message":'Invalid Otp','color':'text-danger'})


def logout(request):
    request.session.clear()
    return render(request, "index.html")

def Buyer(request):
    return render(request, "Buyer.html")

def addCategory(request):
    cursor.execute("select * from categories")
    categories = cursor.fetchall()
    return render(request, "addCategory.html",{"categories":categories})


def addCategory1(request):
    category_name = request.POST.get('category_name', None)
    print(category_name)
    result = cursor.execute("select * from categories where category_name = '" + str(category_name) + "'")
    if result > 0:
        return render(request, "amsg.html", {"message": 'Category Already Exists', 'color': 'text-danger',"request":request})
    else:
        result = cursor.execute("insert into categories(category_name) values('" + str(category_name) + "')  ")
        conn.commit()
    return addCategory(request)


def addProduct(request):
    cursor.execute("select * from categories")
    categories = cursor.fetchall()
    return render(request, "addProduct.html",{"categories":categories, "type":type})




def addProduct1(request):
    product_name = request.POST.get('product_name', None)
    price = request.POST.get('price', None)
    available_count = request.POST.get('available_count', None)
    category_id = request.POST.get('category_id', None)
    description = request.POST.get('description', None)
    picture = request.FILES['picture']
    filename = picture.name
    APP_ROOT2 = APP_ROOT +"/"+ filename
    path = default_storage.save(APP_ROOT2, ContentFile(picture.read()))
    cursor.execute("insert into products (product_name,price,available_count,picture,description,category_id) values('" + str(product_name) + "','" + str(price) + "','" + str(
            available_count) + "','" + str(picture) + "','"+str(description)+"','"+str(category_id)+"')")
    conn.commit()
    return render(request, "amsg.html", {"message": ' Product Added Successfully', 'color': 'text-success'})





def adminProducts(request):
    product_name = request.GET.get('product_name', None)
    category_id = request.GET.get('category_id', None)
    if product_name is None:
        product_name = ''
    if category_id is None:
        category_id = ''
    sql = "select * from products"
    if category_id == '' and product_name == '':
        sql = "select * from products"
    elif category_id == '' and product_name != '':
        sql = "select * from products where product_name like '%" + str(product_name) + "%'"
    elif category_id != '' and product_name == '':
        sql = "select * from products where category_id = '" + str(category_id) + "'"
    elif category_id != '' and product_name != '':
        sql = "select * from products where category_id = '" + str(category_id) + "' and product_name like '%" + str(product_name) + "%'"
    cursor.execute(sql)
    products = cursor.fetchall()
    cursor.execute("select * from categories")
    categories = cursor.fetchall()
    if category_id is not None and category_id != '':
        category_id = int(category_id)
    data = {"products": products, "product_name": product_name, "categories": categories, "category_id": category_id}
    return render(request, "adminProducts.html", data)


def addToCart(request):
    quantity = request.POST.get('quantity', None)
    product_id = request.POST.get('product_id', None)
    available_count = request.POST.get('available_count', None)
    quantity = request.POST.get('quantity', None)
    buyer_order_id = ''
    Buyer_id = request.session['Buyer_id']
    count = cursor.execute("select * from buyer_orders where Buyer_id= '" + str(Buyer_id) + "' and status='cart'")
    if count == 0:
        cursor.execute("insert into buyer_orders(Buyer_id) values('" + str(Buyer_id) + "')")
        conn.commit()
        buyer_order_id = cursor.lastrowid
    else:
        buyer_orders = cursor.fetchall()
        buyer_order_id = buyer_orders[0][0]
    a = cursor.execute("select * from buyer_order_item where buyer_order_id= '" + str(
        buyer_order_id) + "' and product_id='" + str(product_id) + "'")
    if a > 0:
        cursor.execute("update buyer_order_item set quantity = quantity+ " + str(quantity) + " where buyer_order_id='" + str(buyer_order_id) + "' and product_id='" + str(product_id) + "'")
        conn.commit()
        cursor.execute("update products set available_count = available_count- " + str(quantity) + " where product_id='" + str(product_id) + "'")
        conn.commit()
        return render(request,"bmsg.html", {"message":' Product Updated  In Cart', 'color': 'text-primary'})
    else:
        cursor.execute("select * from products where product_id='" + str(product_id) + "' ")
        products = cursor.fetchall()
        price = products[0][2]
        cursor.execute("insert into buyer_order_item(quantity,product_id,buyer_order_id) values('" + str(quantity) + "','" + str(product_id) + "','" + str(buyer_order_id) + "')")
        conn.commit()
        cursor.execute("update products set available_count = available_count- " + str(quantity) + " where product_id='" + str(product_id) + "'")
        conn.commit()
        return render(request, "bmsg.html", {"message": ' Product Added To Cart', 'color': 'text-success'})




def viewOrders(request):
    status = request.GET.get('status', None)
    query = ''
    print(request.session)
    if 'Buyer' not in request.session and 'admin' not in request.session:
        return blogin(request)
    if 'Buyer' in request.session:
        Buyer_id = request.session['Buyer_id']
        if status == 'cart':
            query = "select * from buyer_orders where Buyer_id = '" + str(Buyer_id) + "' and status='cart'"
        elif status == 'Ordered':
            query = "select * from buyer_orders where Buyer_id = '" + str(Buyer_id) + "' and status='Ordered' or status = 'Order Dispatched'"
        elif status == 'History':
            query = "select * from buyer_orders where Buyer_id = '" + str(Buyer_id) + "' and  status='Order Delivered' or status='Cancelled'"
    elif 'admin' in request.session:
        if status == 'Ordered':
            query = "select * from buyer_orders where  status='Ordered' or status = 'Order Dispatched'"
        elif status == 'History':
            query = "select * from buyer_orders where  status='Order Delivered' or status='Cancelled'"

    cursor.execute(query)
    buyer_orders = cursor.fetchall()
    return render(request, "viewOrders.html", {"buyer_orders": buyer_orders})


def viewOrdersAdmin(request):
    status = request.GET.get('status', None)
    query = ''
    print(request.session)
    if 'Buyer' not in request.session and 'admin' not in request.session:
        return blogin(request)
    if 'Buyer' in request.session:
        Buyer_id = request.session['Buyer_id']
        if status == 'cart':
            query = "select * from buyer_orders where Buyer_id = '" + str(Buyer_id) + "' and status='cart'"
        elif status == 'Ordered':
            query = "select * from buyer_orders where Buyer_id = '" + str(Buyer_id) + "' and status='Ordered' or status = 'Order Dispatched'"
        elif status == 'History':
            query = "select * from buyer_orders where Buyer_id = '" + str(Buyer_id) + "' and  status='Order Delivered' or status='Cancelled'"
    elif 'admin' in request.session:
        if status == 'Ordered':
            query = "select * from buyer_orders where  status='Ordered' or status = 'Order Dispatched'"
        elif status == 'History':
            query = "select * from buyer_orders where  status='Order Delivered' or status='Cancelled'"

    cursor.execute(query)
    buyer_orders = cursor.fetchall()
    return render(request, "viewOrdersAdmin.html", {"buyer_orders": buyer_orders})

def editProduct(request):
    product_id = request.POST.get('product_id', None)
    available_count = request.POST.get('available_count', None)
    cursor.execute("select * from products where  product_id='"+str(product_id)+"'")
    products = cursor.fetchall()
    products = products[0]
    return render(request,"editProduct.html",{"products":products,"product_id":product_id,"available_count":available_count})


def editProduct1(request):
    product_id = request.POST.get('product_id', None)
    available_count = request.POST.get('available_count', None)
    available_count2 = request.POST.get('available_count2',None)
    price = request.POST.get('price', None)
    cursor.execute("select * from products where product_id='"+str(product_id)+"'")
    products = cursor.fetchall()
    product_name = products[0][1]
    if int(available_count2) == 0 and int(available_count) != 0:
        cursor.execute("select * from Buyer where Buyer_id in(select Buyer_id from notifications where product_id='"+str(product_id)+"' and status='Subscribed')")
        conn.commit()
        buyers = cursor.fetchall()
        for buyer in buyers:
            email = buyer[2]
            send_email("Online Shopping", "The Product  " + str(product_name) + ", Is Available, You can Shop Now ", email)
    query = "update products set available_count ='" + str(available_count) + "' , price='"+str(price)+"' where product_id='"+str(product_id)+"'"
    cursor.execute(query)
    conn.commit()
    return render(request,"amsg.html",{"message": 'Product updated', 'color': 'text-success'})


def Subscribe_product(request):
    product_id = request.POST.get('product_id', None)
    Buyer_id = request.session['Buyer_id']
    a = cursor.execute("select * from notifications where  product_id='"+str(product_id)+"' and Buyer_id='"+str(Buyer_id)+"'")
    if a == 0:
        cursor.execute("insert into notifications (product_id,Buyer_id,status) values('"+str(product_id)+"','"+str(Buyer_id)+"','Subscribed')")
        conn.commit()
        return render(request, "bmsg.html", {"message": 'Product Subscribed', 'color': 'text-success'})
    else:
        return render(request, "bmsg.html", {"message": 'Already This Product Subscribed', 'color': 'text-danger'})



def removeCart(request):
    conn.commit()
    buyer_order_item_id = request.GET.get('buyer_order_item_id', None)
    cursor.execute("select * from buyer_order_item where buyer_order_item_id = '" + str(buyer_order_item_id) + "'")
    buyer_order_items = cursor.fetchall()
    buyer_order_id = buyer_order_items[0][3]
    cursor.execute("delete from buyer_order_item where buyer_order_item_id = '" + str(buyer_order_item_id) + "'")
    conn.commit()
    cursor.execute("update products set available_count=available_count+'" +str(buyer_order_items[0][1]) + "' where product_id='" + str(buyer_order_items[0][2]) + "' ")
    conn.commit()
    count = cursor.execute("select * from buyer_order_item where buyer_order_id = '" + str(buyer_order_id) + "' ")
    if count == 0:
        cursor.execute("delete from buyer_orders where buyer_order_id = '" + str(buyer_order_id) + "'")
        conn.commit()

    return render(request,"bmsg.html",{"message": 'Product Remove From Cart', 'color': 'text-success'})



def orderNow(request):
    buyer_order_id = request.GET.get("buyer_order_id",None)
    Buyer_id = request.session['Buyer_id']
    cursor.execute("select * from Buyer where Buyer_id='"+str(Buyer_id)+"'")
    buyers = cursor.fetchall()
    address = buyers[0][4]
    return render(request,"orderNow.html",{"address":address,"buyer_order_id":buyer_order_id})


def orderNow1(request):
    address = request.POST.get("address",None)
    buyer_order_id = request.POST.get("buyer_order_id",None)
    Buyer_id = request.session['Buyer_id']
    cursor.execute("update buyer_orders set address='"+str(address)+"', status='Ordered' where buyer_order_id='"+str(buyer_order_id)+"'")
    conn.commit()
    cursor.execute("select * from Buyer where Buyer_id='"+str(Buyer_id)+"'")
    conn.commit()
    Buyer = cursor.fetchall()
    email = Buyer[0][2]
    cursor.execute("select  p.product_name, o.quantity,(p.price*o.quantity) from products p, buyer_order_item o  where p.product_id=o.product_id  and o.buyer_order_id='"+str(buyer_order_id)+"'")
    conn.commit()
    details = cursor.fetchall()
    a = cursor.execute("select * from buyer_orders where status='Ordered' and buyer_order_id='"+str(buyer_order_id)+"'")
    if a>0:
        send_email("Order Placed", "You Ordered  Is Placed Successfully  You can Cancel Your order by with this  link  \n  http://127.0.0.1:8000/CancelOrder/?buyer_order_id="+str(buyer_order_id), email)
    return render(request,"bmsg.html",{"message": 'Order Placed Successfully', 'color': 'text-success'})


def CancelOrder(request):
    conn.commit()
    buyer_order_id = request.GET.get("buyer_order_id",None)
    print(buyer_order_id)
    a = cursor.execute("select * from buyer_orders where status='Ordered' and buyer_order_id='"+str(buyer_order_id)+"'")
    if a > 0:
        cursor.execute("update buyer_orders set status='Cancelled' where buyer_order_id='"+str(buyer_order_id)+"'")
        conn.commit()
        cursor.execute("select * from buyer_order_item where buyer_order_id='"+str(buyer_order_id)+"'")
        buyer_order_items = cursor.fetchall();
        conn.commit()
        for buyer_order_item in buyer_order_items:
            cursor.execute("update products set available_count=available_count+" + str(buyer_order_item[1]) + " where product_id='" + str(buyer_order_item[2]) + "'")
            conn.commit()
        return render(request, "bmsg.html", {"message": 'Order Cancelled', 'color': 'text-success'})
    else:
        return render(request, "bmsg.html", {"message": 'Order can not Cancelled', 'color': 'text-danger'})

def dispatch(request):
    buyer_order_id = request.GET.get("buyer_order_id",None)
    cursor.execute("update buyer_orders set status='Order Dispatched' where buyer_order_id='"+str(buyer_order_id)+"'")
    conn.commit()
    return render(request,"bmsg.html",{"message": 'Order Dispatched', 'color': 'text-success'})

def makeAsReceived(request):
    buyer_order_id = request.GET.get("buyer_order_id",None)
    cursor.execute("update buyer_orders set status='Order Delivered' where buyer_order_id='"+str(buyer_order_id)+"'")
    conn.commit()
    Buyer_id = request.session['Buyer_id']
    cursor.execute("select * from Buyer where Buyer_id='" + str(Buyer_id) + "'")
    conn.commit()
    Buyer = cursor.fetchall()
    email = Buyer[0][2]
    a = cursor.execute("select * from buyer_orders where status='Order Delivered' and buyer_order_id='"+str(buyer_order_id)+"'")
    if a > 0:
        send_email("Order Delivered", "You have Recieved Your Ordered Successsfuly  Click here below Link To Give Review And Rating  \n  http://127.0.0.1:8000/viewOrders/?status=History", email)
    return render(request,"bmsg.html",{"message": 'Order Collected', 'color': 'text-success'})


def give_rating(request):
    conn.commit()
    buyer_order_item_id = request.GET.get("buyer_order_item_id",None)
    cursor.execute("select * from buyer_order_item where buyer_order_item_id='"+str(buyer_order_item_id)+"'")
    conn.commit()
    buyer_order_item = cursor.fetchall()
    product_id = buyer_order_item[0][2]
    return render(request,"give_rating.html", {"product_id":product_id})


def give_rating1(request):
    Buyer_id = request.session['Buyer_id']
    product_id = request.POST.get("product_id",None)
    rating = request.POST.get("rating",None)
    Comment = request.POST.get("Comment",None)
    cursor.execute("insert into reviews(rating,comment,product_id,Buyer_id) values('"+str(rating)+"','"+str(Comment)+"','"+str(product_id)+"','"+str(Buyer_id)+"')")
    conn.commit()
    return render(request,"bmsg.html",{"message": 'Rating Given For Product', 'color': 'text-success'})


def total_reviews(request):
    product_id = request.GET.get("product_id",None)
    count = cursor.execute("SELECT * FROM reviews WHERE product_id = '" + str(product_id)+"' order by date desc " )

    conn.commit()
    if count == 0:
         return  render(request, "bmsg.html", {"message": 'Reviews Not Available For This Product', 'color': 'text-primary'})
    total_reviews = cursor.fetchall()
    return render(request,"total_reviews.html",{"total_reviews":total_reviews})