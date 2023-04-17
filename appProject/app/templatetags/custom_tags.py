import requests
from django import template

register = template.Library()


from django.template.defaultfilters import stringfilter

import pymysql

conn = pymysql.connect(host="localhost", user="root", password="root", db="Shopping")
cursor = conn.cursor()

@register.filter(name='lower')
@stringfilter
def lower(value):
    return value.lower()


@register.filter(is_safe=True)
def myfilter(value):
    return value


@register.filter(name='get_category_by_product_id')
@stringfilter
def get_category_by_category_id(category_id):
    conn.commit()
    cursor.execute("select * from categories where category_id='" + str(category_id) + "'")
    categories = cursor.fetchall()
    return categories[0][1]


@register.filter(name='get_buyer_by_Buyer_id')
@stringfilter
def get_buyer_by_Buyer_id(Buyer_id):
    conn.commit()
    cursor.execute("select * from Buyer where Buyer_id='" + str(Buyer_id) + "'")
    buyer = cursor.fetchall()
    return buyer[0][1]

@register.filter(name='get_review_by_product_id')
@stringfilter
def get_review_by_product_id(product_id):
    conn.commit()
    cursor.execute("select  avg(rating) from reviews where product_id = '"+str(product_id)+"'")
    review = cursor.fetchall()
    print(review)
    if review[0][0] == None:
        return "No Ratings"
    return review[0][0]

@register.filter(name='get_buyer_by_total_review')
@stringfilter
def get_buyer_by_total_review(Buyer_id):
    conn.commit()
    cursor.execute("select  * from  Buyer where Buyer_id = '"+str(Buyer_id)+"'")
    Buyer = cursor.fetchall()
    return Buyer[0][1]




@register.filter(name='get_buyer_order_item_by_buyer_order_id')
@stringfilter
def get_buyer_order_item_by_buyer_order_id(buyer_order_id):
    conn.commit()
    cursor.execute("select * from buyer_orders where buyer_order_id='"+str(buyer_order_id)+"'")
    buyer_orders = cursor.fetchall()
    buyer_order = buyer_orders[0]
    print(buyer_order)
    conn.commit()

    cursor.execute("select p.picture, p.product_name, c.category_name, p.price, o.quantity,(p.price*o.quantity),o.buyer_order_item_id, p.product_id from products p, buyer_order_item o, categories c where p.product_id=o.product_id and c.category_id=p.category_id and o.buyer_order_id='"+str(buyer_order_id)+"'")
    buyer_order_items = cursor.fetchall()
    print(buyer_order_items)
    conn.commit()
    if buyer_order[1] == 'cart':
        strResult = '''<table class="table table-bordered">
                            <tr>
                                <th>Product Picture</th>
                                <th>Product Name</th>
                                <th>Category</th>
                                <th>Price</th>
                                <th>Quantity</th>
                                <th>Total Price</th>
                                <th>Remove</th>
                            </tr>
                            '''
    elif buyer_order[1] == 'Order Delivered':
        strResult = '''<table class="table table-bordered">
                                    <tr>
                                        <th>Product Picture</th>
                                        <th>Product Name</th>
                                        <th>Category</th>
                                        <th>Price</th>
                                        <th>Quantity</th>
                                        <th>Total Price</th>
                                        <th>Review & Rating</th>
                                    </tr>
                                    '''

    else:
        strResult = '''<table class="table table-bordered">
                            <tr>
                                <th>Product Picture</th>
                                <th>Product Name</th>
                                <th>Category</th>
                                <th>Price</th>
                                <th>Quantity</th>
                                <th>Total Price</th>
                            </tr>
                            '''

    total_price = 0
    for buyer_order_item in buyer_order_items:
        if buyer_order[1]=='cart':
            strResult = strResult + '''
                                <tr>
                                    <td><img src="../static/pictures/''' + buyer_order_item[0] + '''" style="height:40px; max-width:100%"></td>
                                    <td>''' + str(buyer_order_item[1]) + '''</td>
                                    <td>''' + str(buyer_order_item[2]) + '''</td>
                                    <td>$ ''' + str(buyer_order_item[3]) + '''</td>
                                    <td>''' + str(buyer_order_item[4]) + '''</td>
                                    <td>$ ''' + str(buyer_order_item[5]) + '''</td>
                                    <td><a class="btn btn-danger" href ="../removeCart/?buyer_order_item_id='''+str(buyer_order_item[6])+'''">Remove</a> </td>
                                </tr>
                    '''
        elif buyer_order[1] == 'Order Delivered':
            print(buyer_orders)
            print(buyer_order_item)
            count = cursor.execute("select * from reviews where Buyer_id='"+str(buyer_order[3])+"' and product_id='"+str(buyer_order_item[7])+"'")
            conn.commit()
            if count > 0:
                strResult = strResult + '''
                                                            <tr>
                                                                <td><img src="../static/pictures/''' + buyer_order_item[
                    0] + '''" style="height:40px; max-width:100%"></td>
                                                                <td>''' + str(buyer_order_item[1]) + '''</td>
                                                                <td>''' + str(buyer_order_item[2]) + '''</td>
                                                                <td>$ ''' + str(buyer_order_item[3]) + '''</td>
                                                                <td>''' + str(buyer_order_item[4]) + '''</td>
                                                                <td>$ ''' + str(buyer_order_item[5]) + '''</td>
                                                                <td> </td>
                                                            </tr>
                                                '''
            else:
                strResult = strResult + '''
                                                            <tr>
                                                                <td><img src="../static/pictures/''' + buyer_order_item[
                    0] + '''" style="height:40px; max-width:100%"></td>
                                                                <td>''' + str(buyer_order_item[1]) + '''</td>
                                                                <td>''' + str(buyer_order_item[2]) + '''</td>
                                                                <td>$ ''' + str(buyer_order_item[3]) + '''</td>
                                                                <td>''' + str(buyer_order_item[4]) + '''</td>
                                                                <td>$ ''' + str(buyer_order_item[5]) + '''</td>
                                                                <td><a class="btn btn-primary" href ="../give_rating/?buyer_order_item_id=''' + str(
                    buyer_order_item[6]) + '''">Review & Rating</a> </td>
                                                            </tr>
                                                '''

        else:
            strResult = strResult + '''
                                <tr>
                                    <td><img src="../static/pictures/''' + buyer_order_item[0] + '''" style="height:40px; max-width:100%"></td>
                                    <td>''' + str(buyer_order_item[1]) + '''</td>
                                    <td>''' + str(buyer_order_item[2]) + '''</td>
                                    <td>$ ''' + str(buyer_order_item[3]) + '''</td>
                                    <td>''' + str(buyer_order_item[4]) + '''</td>
                                    <td>$ ''' + str(buyer_order_item[5]) + '''</td>
                                    
                                </tr>
                    '''

        total_price = total_price + float(buyer_order_item[5])
    if buyer_order[1] == 'cart':
        strResult = strResult + '''
                    <tr>
                        <td colspan="4"></td>
                        <td>Total Price</td>
                        <td>$ ''' + str(total_price) + '''</td>
                        <td></td>
                    </tr></table>
            '''
    elif buyer_order[1] == 'Order Delivered':
        strResult = strResult + '''
                            <tr>
                                <td colspan="4"></td>
                                <td>Total Price</td>
                                <td><b>$''' + str(total_price) + '''</b></td>
                                <td></td>
                            </tr></table>
                    '''
    else:
        strResult = strResult + '''
                    <tr>
                        <td colspan="4"></td>
                        <td>Total Price</td>
                        <td>$''' + str(total_price) + '''</td>
                        
                    </tr></table>
            '''

    return strResult


@register.filter(name='get_buyer_order_item_by_buyer_order_id2')
@stringfilter
def get_buyer_order_item_by_buyer_order_id2(buyer_order_id):
    conn.commit()
    cursor.execute("select * from buyer_orders where buyer_order_id='" + str(buyer_order_id) + "'")
    buyer_orders = cursor.fetchall()
    buyer_order = buyer_orders[0]
    print(buyer_order)
    conn.commit()

    cursor.execute(
        "select p.picture, p.product_name, c.category_name, p.price, o.quantity,(p.price*o.quantity),o.buyer_order_item_id from products p, buyer_order_item o, categories c where p.product_id=o.product_id and c.category_id=p.category_id and o.buyer_order_id='" + str(
            buyer_order_id) + "'")
    buyer_order_items = cursor.fetchall()
    print(buyer_order_items)
    conn.commit()
    if buyer_order[1] == 'cart':
        strResult = '''<table class="table table-bordered">
                            <tr>
                                <th>Product Picture</th>
                                <th>Product Name</th>
                                <th>Category</th>
                                <th>Price</th>
                                <th>Quantity</th>
                                <th>Total Price</th>
                                <th>Remove</th>
                            </tr>
                            '''

    else:
        strResult = '''<table class="table table-bordered">
                            <tr>
                                <th>Product Picture</th>
                                <th>Product Name</th>
                                <th>Category</th>
                                <th>Price</th>
                                <th>Quantity</th>
                                <th>Total Price</th>
                            </tr>
                            '''

    total_price = 0
    for buyer_order_item in buyer_order_items:
        if buyer_order[1] == 'cart':
            strResult = strResult + '''
                                <tr>
                                    <td><img src="../static/pictures/''' + buyer_order_item[0] + '''" style="height:40px; max-width:100%"></td>
                                    <td>''' + str(buyer_order_item[1]) + '''</td>
                                    <td>''' + str(buyer_order_item[2]) + '''</td>
                                    <td>$ ''' + str(buyer_order_item[3]) + '''</td>
                                    <td>''' + str(buyer_order_item[4]) + '''</td>
                                    <td>$ ''' + str(buyer_order_item[5]) + '''</td>
                                    <td><a class="btn btn-danger" href ="../removeCart/?buyer_order_item_id=''' + str(
                buyer_order_item[6]) + '''">Remove</a> </td>
                                </tr>
                    '''
        else:
            strResult = strResult + '''
                                <tr>
                                    <td><img src="../static/pictures/''' + buyer_order_item[0] + '''" style="height:40px; max-width:100%"></td>
                                    <td>''' + str(buyer_order_item[1]) + '''</td>
                                    <td>''' + str(buyer_order_item[2]) + '''</td>
                                    <td>$ ''' + str(buyer_order_item[3]) + '''</td>
                                    <td>''' + str(buyer_order_item[4]) + '''</td>
                                    <td>$ ''' + str(buyer_order_item[5]) + '''</td>

                                </tr>
                    '''

        total_price = total_price + float(buyer_order_item[5])
    if buyer_order[1] == 'cart':
        strResult = strResult + '''
                    <tr>
                        <td colspan="4"></td>
                        <td>Total Price</td>
                        <td>$ ''' + str(total_price) + '''</td>
                        <td></td>
                    </tr></table>
            '''
    else:
        strResult = strResult + '''
                    <tr>
                        <td colspan="4"></td>
                        <td>Total Price</td>
                        <td>$''' + str(total_price) + '''</td>

                    </tr></table>
            '''

    return strResult
