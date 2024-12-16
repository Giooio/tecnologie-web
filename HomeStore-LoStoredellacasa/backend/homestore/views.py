from datetime import date
from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.views.decorators.http import require_POST
from django.urls import reverse
from .recommendation import *
from django.http import JsonResponse 
from django.core.mail import send_mass_mail
from django.db import DatabaseError
# Create your views here.

def welcome(request):
    if request.method == 'POST' and 'delete_question' in request.POST:
        question_id = request.POST.get('question_id_to_delete')
        if question_id:
            try:
                question_to_delete = Question.objects.get(id=question_id)
                if question_to_delete.user == request.user:
                    question_to_delete.delete()
                else:
                    messages.error(request, 'Non puoi eliminare questa domanda.')
            except Question.DoesNotExist:
                messages.error(request, 'La domanda che stai cercando di eliminare non esiste.')

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user
            question.save()
    else:
        form = QuestionForm()

    answered_questions = Question.objects.filter(is_answered=True).order_by('-created_at')
    unanswered_questions = Question.objects.filter(is_answered=False).order_by('-created_at')


    return render(request, 'homestore/welcome.html', {
        'form': form,
        'answered_questions': answered_questions,
        'unanswered_questions': unanswered_questions
    })

    
def index(request):
    products = Product.objects.all()
    return render(request, 'homestore/index.html', {'products': products}) 

@staff_member_required
def admin_dashboard(request):
    unanswered_questions_count = Question.objects.filter(answer_text__isnull=True).count()
    pending_orders_count = Order.objects.filter(status='pending').count()
    return render(request, 'homestore/admin_dashboard.html', {
        'unanswered_questions_count': unanswered_questions_count,
        'pending_orders_count': pending_orders_count,
        'show_back_button': True,
        'back_url': '/'
    })

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.filter(username=username).first()
        if user:
            if not user.is_active: 
                messages.error(request, "Il tuo account è stato disattivato. Contatta l'amministratore.")
                return render(request, 'homestore/login.html')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('welcome')
        else:
            messages.error(request, "Nome utente o password non validi.")
            return render(request, 'homestore/login.html')
            
    return render(request, 'homestore/login.html')

def logout_view(request):
    if request.method == 'POST':
        if 'confirm' in request.POST and request.POST['confirm']=='yes':
            logout(request)
            return redirect('welcome')
        else:
            return redirect(request.POST.get('next', '/'))  
    
    context = {'next': request.META.get('HTTP_REFERER', '/')}   
    
    return render(request, 'homestore/logout_confirm.html', context)
    
class CustomUserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput, label='Conferma Password')
    phone_number = forms.CharField(max_length=15, required=False, label="Numero di Telefono")
    address = forms.CharField(max_length=255, required=False, label="Indirizzo")


    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone_number', 'address']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password != password_confirmation:
            self.add_error('password_confirmation', 'Le password non corrispondono.')

def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('welcome')  
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'homestore/register.html', {'form': form})

@login_required
def is_superUser(request):
    if request.user.is_superuser:
        return render(request, 'admin.html')
    else:
        return render(request, 'welcome.html')

def aggiungi_prodotto(request):
    if request.method == 'POST':
        form = ProdottoForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.available = product.stock > 0 
            product.save()
            return redirect('admin_dashboard')  
    else:
        form = ProdottoForm()
    return render(request, 'homestore/aggiungi_prodotto.html', {'form': form, 'show_back_button': True,
        'back_url': '/dashboard/'})

def admin_delete_product(request):
    search_query = request.GET.get('search', '')
    products = Product.objects.filter(nome__icontains=search_query)
    return render(request, 'homestore/elimina_prodotto.html', {
        'products': products,
        'show_back_button': True,
        'back_url': '/dashboard/'  
    })

def elimina_prodotto(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('homestore/elimina_prodotto.html', )

def confirm_delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('admin_dashboard')
    return render(request, 'homestore/confirm_delete.html', {'product': product, 'show_back_button': True,
        'back_url': '/dashboard/' })

def modifica_prodotto(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        products = Product.objects.filter(nome__icontains=search_query)
        return render(request, 'homestore/modifica_prodotto.html', {'products': products,
        'show_back_button': True,
        'back_url': '/dashboard/'  
    })

def modifica_prodotto_form(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProdottoForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProdottoForm(instance=product)
    return render(request, 'homestore/modifica_prodotto_form.html', {'form': form, 'show_back_button': True,
        'back_url': '/dashboard/' })

def category_list(request):
    category_name = request.GET.get('category_name')  
    order_by = request.GET.get('order', 'price_asc')  
    selected_color_id = request.GET.get('color', None)
    availability = request.GET.get('availability')

    if category_name:
        products = Product.objects.filter(categoria=category_name)
    else:
        products = Product.objects.all()
        category_name = 'Tutti i Prodotti'
    
    if order_by == 'price_asc':
        products = products.order_by('prezzo')  
    elif order_by == 'price_desc':
        products = products.order_by('-prezzo')
        
    if availability == 'available':
        products = products.filter(stock__gt=0)
    elif availability == 'unavailable':
        products = products.filter(stock=0)
        
    if selected_color_id:
        products = products.filter(colori__id=selected_color_id)
        
    colors = Color.objects.all()

    return render(request, 'homestore/category_list.html', {
        'category_name': category_name,
        'products': products,
        'order_by': order_by,
        'selected_color': selected_color_id,  
        'colors': colors, 
        'availability': availability,
    })
    
def all_products(request):
    order_by = request.GET.get('order', 'price_asc')  
    selected_color_id = request.GET.get('color', None)
    availability = request.GET.get('availability')

    if order_by == 'price_asc':
        products = Product.objects.all().order_by('prezzo')  
    elif order_by == 'price_desc':
        products = Product.objects.all().order_by('-prezzo')  
    else:
        products = Product.objects.all()  
        
    if selected_color_id:
        products = products.filter(colori__id=selected_color_id)
        
    if availability == 'available':
        products = products.filter(stock__gt=0)
    elif availability == 'unavailable':
        products = products.filter(stock=0)
        
    colors = Color.objects.all()

    return render(request, 'homestore/all_products.html', {
        'products': products,
        'order_by': order_by,  
        'selected_color': selected_color_id,  
        'colors': colors, 
        'availability': availability,
    })
    
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    available_colors = product.colori.all()
    referer_url = request.META.get('HTTP_REFERER', '/')
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            cart = None
        
        if cart:
            cart_item = CartItem.objects.filter(cart=cart, product=product).first()
            if cart_item:
                if cart_item.quantity > 3:
                    error_message = f"Non puoi aggiungere più di 3 unità di {product.nome} al tuo carrello."
                else:
                    error_message = None
            else:
                error_message = None
            
            if cart.items.count() >= 5:
                error_message = error_message or "Hai già 5 prodotti unici nel carrello. Rimuovi alcuni articoli per aggiungerne di nuovi."

        else:
            error_message = None
    else:
        error_message = None
    
    return render(request, 'homestore/product_detail.html', {
        'product': product, 
        'available_colors': available_colors,
        'show_back_button': True,
        'back_url': referer_url, }
    )

@login_required
def submit_question(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user
            question.save()
            return redirect('welcome')
    else:
        form = QuestionForm()
    return render(request, 'homestore/welcome.html', {'form': form})

@staff_member_required
def manage_questions(request):
    if request.method == 'POST':
        question_id = request.POST.get('question_id')
        answer_text = request.POST.get(f'answer_text_{question_id}')
        
        if question_id and answer_text:
            question = Question.objects.get(id=question_id)
            question.answer_text = answer_text
            question.is_answered = True
            question.save()
            return redirect('manage_questions')  

    questions = Question.objects.all()
    return render(request, 'homestore/manage_questions.html', {'questions': questions, 'show_back_button': True,
        'back_url': '/dashboard/' })
    
@staff_member_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    question.delete()
    
    return redirect('manage_questions')

@login_required
def manage_users(request):
    users = User.objects.all().filter(is_staff=False)
    return render(request, 'homestore/manage_users.html', {'users': users, 'show_back_button': True,
        'back_url': '/dashboard/'  })

@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    referer_url = request.META.get('HTTP_REFERER', '/')
    
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        password_form = PasswordChangeForm(user, request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('manage_users')
        
        if password_form.is_valid():
            password_form.save()
            return redirect('manage_users')
    else:
        form = UserChangeForm(instance=user)
        password_form = PasswordChangeForm(user)

    return render(request, 'homestore/edit_user.html', {'form': form, 'password_form': password_form, 'user': user, 
        'show_back_button': True,
        'back_url': referer_url})

@login_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    status = request.GET.get('status')
    
    if status == 'active':
        user.is_active = True
    elif status == 'inactive':
        user.is_active = False
    user.save()

    return redirect('manage_users')

@login_required
def user_activity(request, user_id):
    user = get_object_or_404(User, id=user_id)
    activities = UserActivity.objects.filter(user=user).order_by('-timestamp')
    return render(request, 'homestore/user_activity.html', {'activities': activities, 'user': user})

@login_required
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'authentication_required'}, status=403)

    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
    
    product = get_object_or_404(Product, id=product_id)
    color = request.POST.get('color', None) 
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1  
    
    if quantity <= 0:
        return redirect('product_detail', product_id=product_id)
    
    unique_product_ids = cart.items.values_list('product', flat=True).distinct()  # Ottieni solo gli ID dei prodotti unici
    print(f"Numero di prodotti unici nel carrello: {len(unique_product_ids)}")
    
    if len(unique_product_ids) >= 5:
        messages.error(request, "Non è possibile aggiungere più di 5 prodotti unici nel carrello.")
        return redirect('view_cart')
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, color=color)
    
    if not created:
        cart_item.quantity = min(cart_item.quantity + quantity, 3)
    else:
        cart_item.quantity = min(quantity, 3)
        
    if created and cart.items.count() >= 5:  
        messages.error(request, "Non è possibile aggiungere più di 5 prodotti unici nel carrello.")
        return redirect('view_cart')
    
    cart_item.save()  

    return redirect('view_cart')

def cart_remove(request, product_id):
    cart = Cart.objects.get(user=request.user)
    
    product = get_object_or_404(Product, id=product_id)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    except CartItem.MultipleObjectsReturned:
        CartItem.objects.filter(cart=cart, product=product).delete()
    
    return redirect('view_cart')


@login_required
def cart_update(request, product_id):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity'))
            if quantity <= 0:
                return JsonResponse({'success': False, 'message': 'La quantità deve essere maggiore di zero'})
            
            cart = Cart.objects.get(user=request.user)
            product = get_object_or_404(Product, id=product_id)
            
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            
            if quantity > 3:
                return JsonResponse({'success': False, 'message': 'Non puoi aggiungere più di 3 unità di questo prodotto'})
            
            cart_item.quantity = quantity
            cart_item.save()

            
            total_price = cart_item.get_total_price()  

            return JsonResponse({
                'success': True,
                'total': total_price
            })
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Quantità non valida'})
    return JsonResponse({'success': False, 'message': 'Metodo non supportato'})

@login_required
def view_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
    
    cart_items = cart.items.all()  
    cart_total = cart.get_total_price() 
    
    orders = Order.objects.all()
    
    cart_product_ids = [item.product.id for item in cart_items]
    product_categories = cart_items.values_list('product__categoria', flat=True).distinct()
    orders_with_products = Order.objects.filter(
        cart_items__product__id__in=cart_product_ids
    ).exclude(user=request.user).distinct()
    
    related_products = Product.objects.filter(
        orderitem__order__in=orders_with_products
    ).exclude(id__in=cart_product_ids).distinct()
    
    recommended_by_association = Product.objects.exclude(id__in=cart_items.values_list('product_id', flat=True)).order_by('-sold_count')[:5]
    recommended_by_category = []
    for category in product_categories:
        products_in_category = Product.objects.filter(
            categoria=category
        ).exclude(id__in=cart_product_ids).distinct()[:3]  
        recommended_by_category.extend(products_in_category)

    recommended_by_category = recommended_by_category[:5]
    recommended_by_collaboration = related_products[:5]
    
    for order in orders_with_products:
        print(f"- Ordine #{order.id} - {order.user.username}")
        for item in order.cart_items.all():
            print(f"  - {item.product.nome} (ID: {item.product.id})")
    
    
    return render(request, 'homestore/view_cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'recommended_by_association': recommended_by_association,
        'recommended_by_category': recommended_by_category,
        'recommended_by_collaboration': recommended_by_collaboration,
        'show_back_button': True,
        'back_url': '/tutti-i-prodotti/'
    })

    """Classe per gestire il carrello nella sessione."""
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.prezzo)
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            cart_item = self.cart[str(product.id)]
            cart_item['product'] = product
            cart_item['total_price'] = Decimal(cart_item['price']) * cart_item['quantity']
            yield cart_item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session['cart']
        self.save()

@login_required
def purchase_summary(request):
    if request.method == 'POST':
        cart_items = CartItem.objects.filter(cart__user=request.user)

        if not cart_items:
            return redirect('view_cart')  
        
        cart_total = sum(item.get_total_price() for item in cart_items)
        order = Order.objects.create(user=request.user, total=cart_total)
        

        for item in cart_items:
            color = request.POST.get(f'product_color_{item.product.id}')
            order.items.create(product=item.product, quantity=item.quantity, color=color)

            product = item.product
            if product.stock < item.quantity:
                return redirect('view_cart')
            product.stock -= item.quantity
            product.sold_count += item.quantity
            product.save() 
            
        cart_items.delete()
        
        return render(request, 'homestore/purchase_summary.html', {
            'order': order,  
            'cart_total': cart_total,  
        })
    
    return redirect('view_cart')

@login_required
def update_pickup_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    days_left = order.days_left_for_pickup()
    if days_left == 0 and order.pickup_status == 'pending':
        order.pickup_status = 'cancelled'
    elif request.POST.get('mark_as_picked'):
        order.pickup_status = 'picked'

    order.save()
    return redirect('orders')

@login_required
def view_orders(request):
    selected_status = request.GET.get('status', None)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')  # Ordina per data di creazione, discendente
    
    if selected_status:
        orders = orders.filter(status=selected_status)
    for order in orders:
        order.total = sum(item.product.prezzo * item.quantity for item in order.items.all())
    
    return render(request, 'homestore/view_orders.html', {'orders': orders, 'selected_status': selected_status, 'show_back_button': True,
        'back_url': '/'})

@login_required
def order_details(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    order_items = order.cart_items.all()  
    return render(request, 'homestore/order_details.html', {
        'order': order, 
        'order_items': order_items, 
        'show_back_button': True,
        'back_url': reverse('view_orders')
    })


def manage_orders(request):
    selected_user = request.GET.get('user', '')
    selected_status = request.GET.get('status', None)

    users = User.objects.all().filter(is_staff=False)

    orders = Order.objects.all().order_by('-created_at')

    if selected_user:
        orders = orders.filter(user_id=selected_user)

    if selected_status:
        orders = orders.filter(status=selected_status)
    
    context = {
        'orders': orders,
        'users': users,
        'selected_user': selected_user,
        'selected_status': selected_status,
        'show_back_button': True,
        'back_url': '/dashboard/',
    }

    return render(request, 'homestore/manage_orders.html', context)

def toggle_ready_for_pickup(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.ready_for_pickup = not order.ready_for_pickup
    order.save()
    
    return redirect('homestore/manage_orders.html')


def mark_ready_for_pickup(request, order_id):
    if request.method == 'POST':
        print(f"Request ricevuta per ordine {order_id}")
        try:
            order = get_object_or_404(Order, id=order_id)
            
            if not order.ready_for_pickup:
                order.ready_for_pickup = True
                order.save()

                days_left = 10
                order.pickup_deadline = date.today() + timedelta(days=days_left)
                order.save()

                subject = "Il tuo ordine è pronto per il ritiro"
                message = f"""
                Ciao {order.user.username},

                Il tuo ordine #{order.id} è stato aggiornato e ora è pronto per il ritiro.

                Ti invitiamo a passare al più presto a ritirarlo presso il nostro negozio.

                Grazie per aver scelto il nostro servizio.

                Cordiali saluti,
                HomeStore
                """
                user_email = order.user.email  


                send_mail(
                    subject,
                    message,
                    'noreply@homestore.com',  
                    [user_email],
                    fail_silently=False,  
                )

                return JsonResponse({'success': True, 'days_left': days_left})

            return JsonResponse({'success': False, 'error': 'L\'ordine è già pronto per il ritiro.'})
        except Exception as e:
            print(f"Errore: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Metodo non valido.'})


def order_details_admin(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
        'show_back_button': True,  
        'back_url': '/orders/'
    }
    return render(request, 'homestore/order_details_admin.html', context)

def update_order_status(request, order_id, status):
    order = get_object_or_404(Order, id=order_id)
    if status in dict(Order.STATUS_CHOICES):  
        order.status = status
        order.save()

    orders = Order.objects.all().order_by('-created_at')
    for order in orders:
        order.days_left = order.days_left_for_pickup() 
    return render(request, 'homestore/manage_orders.html', {'orders': orders, 'show_back_button': True,
        'back_url': '/dashboard/'})


def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'homestore/cancel_order.html', {'order': order})

def confirm_cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status != 'cancelled':
        order.status = 'cancelled'
        order.save()
    return redirect('manage_orders')

def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('manage_orders') 

