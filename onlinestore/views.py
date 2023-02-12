from django.shortcuts import render, HttpResponse, redirect, \
    get_object_or_404, reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from jewel import settings
from django.db.models import F
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from .models import Product, Order, LineItem, User
from . import cart
from .forms import CartForm, CheckoutForm, RatingForm
from django.shortcuts import render
from . tokens import generate_token
from django.core.exceptions import ValidationError

# Create your views here.
def index(request):
    data=Product.objects.all()
    return render(request, "onlinestore/index.html")

def create_user(self, username, email, password):
        user = self.model(
            username=username,
            email=email,
            password=password
        )
        user.save(using=self._db)
        return user

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        address = request.POST['address']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('index')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('index')
        
        if len(username) > 20:
            messages.error(request, "Username must be under 20 characters!!")
            return redirect('index')

        if len(address) > 50:
            messages.error(request, "Address must be under 50 characters!!")
            return redirect('index')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't match!!")
            return redirect('index')
        
        if not username.isalnum():
            messages.error(request, "Username must be alphanumeric!!")
            return redirect('index')
        
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.address = address
        myuser.is_active = False
        #myuser.set_password(pass1)
        myuser.save()
        messages.success(request, "Your account has been created successfully!! Please check your email to confirm your email address in order to activate your account.")
        
        # Welcome Email
        subject = "Welcome to Jewel Store Login!!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to Jewel Store!! \nThank you for visiting our website. We have also sent you a confirmation email, please confirm your email address. \n\nThank you\nShravya Kakkireni"        
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        
        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email @ Jewelstore - Django Login!!"
        message2 = render_to_string('email_confirmation.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
        email_subject,
        message2,
        settings.EMAIL_HOST_USER,
        [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        return redirect('signin')
    
        
    return render(request, "onlinestore/signup.html")


def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        #user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request,'activation_failed.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(request, username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            messages.success(request, "Logged In Sucessfully!!")
            return render(request, "onlinestore/index.html",{"fname":fname})
        else:
            messages.error(request, "Account does not exist!!")
            return redirect('home')
    
    return render(request, "onlinestore/signin.html")

def index(request):
    all_products = Product.objects.all()
    return render(request, "onlinestore/index.html", {
                                    'all_products': all_products,
                                    })

                                    
def show_product(request, product_id, product_slug):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = CartForm(request, request.POST)
        if form.is_valid():
            request.form_data = form.cleaned_data
            cart.add_item_to_cart(request)
            return redirect('show_cart')

    form = CartForm(request, initial={'product_id': product.id})
    return render(request, 'onlinestore/product_detail.html', {
                                            'product': product,
                                            'form': form,
                                            })
"""def show_product(request, product_id, product_slug):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        cart_form = CartForm(request, request.POST)
        rating_form = RatingForm(request.POST)
        if cart_form.is_valid() and rating_form.is_valid():
            request.form_data = cart_form.cleaned_data
            cart.add_item_to_cart(request)
            rating = rating_form.cleaned_data['rating']
            product.rating = rating
            product.save()
            return redirect('show_cart')

    cart_form = CartForm(request, initial={'product_id': product.id})
    rating_form = RatingForm()
    return render(request, 'onlinestore/product_detail.html', {
                                            'product': product,
                                            'cart_form': cart_form,
                                            'rating_form': rating_form,
                                            })"""
  
def show_cart(request):

    if request.method == 'POST':
        if request.POST.get('submit') == 'Update':
            cart.update_item(request)
        if request.POST.get('submit') == 'Remove':
            cart.remove_item(request)

    cart_items = cart.get_all_cart_items(request)
    cart_subtotal = cart.subtotal(request)
    return render(request, 'onlinestore/cart.html', {
        'cart_items':cart_items, 'cart_subtotal': cart_subtotal,
    })


def checkout(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            o = Order(
                name = cleaned_data.get('name'),
                email = cleaned_data.get('email'),
                #postal_code = cleaned_data.get('postal_code'),
                address = cleaned_data.get('address'),
            )
            o.save()

            all_items = cart.get_all_cart_items(request)
            for cart_items in all_items:
                li = LineItem(
                    product_id = cart_items.product_id,
                    price = cart_items.price,
                    quantity = cart_items.quantity,
                    order_id = o.id
                )

                li.save()

            cart.clear(request)

            request.session['order_id'] = o.id
            messages.add_message(request, messages.INFO, 'Order Placed! Thank you for shopping with us!')
         
            subject = "Order Placed!!"
            cancellation_link = request.build_absolute_uri(reverse('cancel_order', args=[o.cancellation_token]))
            rating_link = request.build_absolute_uri(reverse('rating'))
            
            message = "Hello!\n" + "Order Placed! Thank you for shopping with us!\n" + "If you want to cancel your order please click on this link: " + cancellation_link + "   And if you want to rate your order please click on this link: " + rating_link
            #message = "Hello !! \n" + "Order Placed! Thank you for shopping with us!"        
            from_email = settings.EMAIL_HOST_USER
            to_list = [cleaned_data.get('email')]
            send_mail(subject, message, from_email, to_list, fail_silently=True)

            return redirect('signout')
    else:
        user = request.user
        user_details = {
            'email': user.email,
            'name': user.first_name,
            'address': user.address
        }
        form = CheckoutForm(initial=user_details)

        return render(request, 'onlinestore/checkout.html', {'form': form})

def rating_view(request):
    return render(request, 'onlinestore/submit_rating.html')


def cancel_order(request, token):
    order = Order.objects.get(cancellation_token=token)
    order.cancelled = True
    order.save()
    messages.add_message(request, messages.INFO, 'Your order has been cancelled.')
    return render(request, 'onlinestore/cancelled.html')#return redirect('order_status')


def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('index')


