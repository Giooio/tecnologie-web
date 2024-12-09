from decimal import ROUND_DOWN
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from homestore.models import *
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

class OrderTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.order = Order.objects.create(
            user=user,
            created_at=timezone.now() - timedelta(days=5),  # 5 giorni fa
            total=100.00
        )

    def test_days_left_for_pickup(self):
        """Testa il calcolo dei giorni rimanenti per il ritiro."""
        expected_deadline = self.order.created_at + timedelta(days=10)
        remaining_days = self.order.days_left_for_pickup()

        # Verifica che i giorni rimanenti siano corretti
        self.assertEqual(remaining_days, (expected_deadline - timezone.now()).days)

    def test_days_left_for_pickup_expired(self):
        """Testa il caso in cui i giorni rimanenti sono 0 o negativi."""
        # Simula un ordine scaduto (11 giorni fa)
        self.order.created_at = timezone.now() - timedelta(days=11)
        self.order.save()

        remaining_days = self.order.days_left_for_pickup()
        self.assertEqual(remaining_days, 0)  # Non possono esserci giorni negativi


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from homestore.models import Product, Cart, CartItem
from django.http import JsonResponse

class CartUpdateTestCase(TestCase):
    
    def setUp(self):
        # Crea un utente di prova
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        # Crea un prodotto di prova
        self.product = Product.objects.create(nome='Test Product', prezzo=10.0)
        
        # Crea un carrello per l'utente
        self.cart = Cart.objects.create(user=self.user)
        
        # Aggiungi un prodotto al carrello
        self.cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        
        # Definisci l'URL della view
        self.url = reverse('cart_update', args=[self.product.id])

    def test_cart_update_authenticated(self):
        """Verifica che un utente autenticato possa aggiornare la quantità del carrello"""
        self.client.login(username='testuser', password='password123')
        
        # Invia una richiesta POST per aggiornare la quantità
        response = self.client.post(self.url, {'quantity': 2})

        # Verifica che la risposta sia una risposta JSON con successo
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'success': True,
            'total': '20.00'  # Prezzo totale per 2 unità di prodotto a 10.0 ciascuna
        })
        
        # Verifica che la quantità nel carrello sia stata aggiornata
        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.quantity, 2)

    def test_cart_update_invalid_quantity(self):
        """Verifica che venga restituito un errore per una quantità non valida"""
        self.client.login(username='testuser', password='password123')
        
        # Invia una richiesta POST con una quantità non valida (es. una stringa)
        response = self.client.post(self.url, {'quantity': 'invalid'})

        # Verifica che la risposta sia un errore
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'success': False,
            'message': 'Quantità non valida'
        })

    def test_cart_update_quantity_zero_or_negative(self):
        """Verifica che venga restituito un errore per una quantità <= 0"""
        self.client.login(username='testuser', password='password123')
        
        # Invia una richiesta POST con una quantità zero
        response_zero = self.client.post(self.url, {'quantity': 0})
        self.assertEqual(response_zero.status_code, 200)
        self.assertJSONEqual(response_zero.content, {
            'success': False,
            'message': 'La quantità deve essere maggiore di zero'
        })
        
        # Invia una richiesta POST con una quantità negativa
        response_negative = self.client.post(self.url, {'quantity': -1})
        self.assertEqual(response_negative.status_code, 200)
        self.assertJSONEqual(response_negative.content, {
            'success': False,
            'message': 'La quantità deve essere maggiore di zero'
        })

    def test_cart_update_quantity_too_high(self):
        """Verifica che venga restituito un errore per una quantità > 3"""
        self.client.login(username='testuser', password='password123')
        
        # Invia una richiesta POST con una quantità maggiore di 3
        response = self.client.post(self.url, {'quantity': 4})
        
        # Verifica che venga restituito un errore
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'success': False,
            'message': 'Non puoi aggiungere più di 3 unità di questo prodotto'
        })

    def test_cart_update_not_authenticated(self):
        """Verifica che un utente non autenticato venga reindirizzato alla pagina di login"""
        # Invia una richiesta POST senza essere autenticato
        response = self.client.post(self.url, {'quantity': 2})
        
        # Verifica che venga effettuato un reindirizzamento alla pagina di login
        self.assertRedirects(response, '/login/?next=' + self.url)






from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from homestore.models import Question
from homestore.forms import QuestionForm

class SubmitQuestionTestCase(TestCase):

    def setUp(self):
        """Setup iniziale per creare un utente e preparare il test."""
        # Crea un utente di test
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # URL della vista
        self.url = reverse('submit_question')

    def test_submit_question_authenticated_valid_form(self):
        """Verifica che un utente autenticato possa inviare una domanda valida."""
        self.client.login(username='testuser', password='password')
        
        # Dati validi per il form
        data = {'question_text': 'Questa è una domanda di test.'}
        
        response = self.client.post(self.url, data)
        
        # Verifica il reindirizzamento alla pagina 'welcome'
        self.assertRedirects(response, reverse('welcome'))
        
        # Verifica che la domanda sia stata salvata
        question = Question.objects.first()
        self.assertIsNotNone(question)
        self.assertEqual(question.user, self.user)
        self.assertEqual(question.question_text, 'Questa è una domanda di test.')

    def test_submit_question_authenticated_invalid_form(self):
        """Verifica che un form non valido non venga salvato."""
        self.client.login(username='testuser', password='password')
        
        # Dati non validi per il form (campo vuoto)
        data = {'question_text': ''}
        
        response = self.client.post(self.url, data)
        
        # Verifica che la risposta contenga il form con errori
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homestore/welcome.html')
        self.assertContains(response, 'Questo campo è obbligatorio.')  # Messaggio di errore previsto
        
        # Verifica che nessuna domanda sia stata salvata
        self.assertEqual(Question.objects.count(), 0)



from django.test import TestCase
from django.urls import reverse
from homestore.models import Product, Color

class CategoryListViewTest(TestCase):
    def setUp(self):
        # Creazione di colori
        self.color_red = Color.objects.create(name="Rosso", code="#FF0000")
        self.color_blue = Color.objects.create(name="Blu", code="#0000FF")

        # Creazione di prodotti
        self.product1 = Product.objects.create(
            nome="Prodotto 1",
            categoria="Categoria 1",
            prezzo=10.0,
            stock=5,
            descrizione="Descrizione del prodotto 1",
        )
        self.product1.colori.add(self.color_red)

        self.product2 = Product.objects.create(
            nome="Prodotto 2",
            categoria="Categoria 1",
            prezzo=20.0,
            stock=0,
            descrizione="Descrizione del prodotto 2",
        )
        self.product2.colori.add(self.color_blue)

        self.product3 = Product.objects.create(
            nome="Prodotto 3",
            categoria="Categoria 2",
            prezzo=15.0,
            stock=10,
            descrizione="Descrizione del prodotto 3",
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/category-list/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homestore/category_list.html')

    def test_filter_by_category(self):
        response = self.client.get(reverse('category_list') + '?category_name=Categoria 1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prodotto 1")
        self.assertContains(response, "Prodotto 2")
        self.assertNotContains(response, "Prodotto 3")

    def test_filter_by_color(self):
        response = self.client.get(reverse('category_list') + f'?color={self.color_red.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prodotto 1")
        self.assertNotContains(response, "Prodotto 2")
        self.assertNotContains(response, "Prodotto 3")

    def test_filter_by_availability(self):
        response = self.client.get(reverse('category_list') + '?availability=available')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prodotto 1")
        self.assertContains(response, "Prodotto 3")
        self.assertNotContains(response, "Prodotto 2")

        response = self.client.get(reverse('category_list') + '?availability=unavailable')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prodotto 2")
        self.assertNotContains(response, "Prodotto 1")
        self.assertNotContains(response, "Prodotto 3")

    def test_order_by_price(self):
        response = self.client.get(reverse('category_list') + '?order=price_asc')
        self.assertEqual(response.status_code, 200)
        products = list(response.context['products'])
        self.assertEqual(products[0], self.product1)  # Prezzo 10.0
        self.assertEqual(products[1], self.product3)  # Prezzo 15.0
        self.assertEqual(products[2], self.product2)  # Prezzo 20.0

        response = self.client.get(reverse('category_list') + '?order=price_desc')
        self.assertEqual(response.status_code, 200)
        products = list(response.context['products'])
        self.assertEqual(products[0], self.product2)  # Prezzo 20.0
        self.assertEqual(products[1], self.product3)  # Prezzo 15.0
        self.assertEqual(products[2], self.product1)  # Prezzo 10.0

    def test_default_view(self):
        response = self.client.get(reverse('category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prodotto 1")
        self.assertContains(response, "Prodotto 2")
        self.assertContains(response, "Prodotto 3")




from django.test import TestCase
from django.urls import reverse
from homestore.models import Product
from homestore.forms import ProdottoForm  # Suppongo che il form si chiami ancora ProdottoForm

class AggiungiProdottoViewTest(TestCase):
    
    def setUp(self):
        # Dati di esempio per il form
        self.valid_data = {
            'nome': 'Test Product',  # Adatta i campi ai nomi effettivi del tuo modello
            'descrizione': 'This is a test product.',
            'prezzo': 10.99,
            'stock': 5,
            'categoria': 'Test Category' 
        }
        self.invalid_data = {
            'nome': '',
            'descrizione': '',
            'prezzo': -5,  # Prezzo non valido
            'stock': 0
        }

    def test_view_renders_correct_template(self):
        """
        Test che la view renderizzi il template corretto.
        """
        response = self.client.get(reverse('admin_add_product'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homestore/aggiungi_prodotto.html')

    def test_view_displays_form(self):
        """
        Test che la view mostri il form.
        """
        response = self.client.get(reverse('admin_add_product'))
        self.assertIsInstance(response.context['form'], ProdottoForm)

    def test_valid_form_submission_creates_product(self):
        """
        Test che un form valido crei un nuovo prodotto.
        """
        response = self.client.post(reverse('admin_add_product'), data=self.valid_data)
        self.assertEqual(response.status_code, 302)  # Redirezione
        self.assertEqual(Product.objects.count(), 1)  # Prodotto creato
        product = Product.objects.first()
        self.assertEqual(product.nome, self.valid_data['nome'])
        self.assertEqual(product.prezzo.quantize(Decimal('0.01'), rounding=ROUND_DOWN), Decimal(self.valid_data['prezzo']).quantize(Decimal('0.01'), rounding=ROUND_DOWN))
        self.assertTrue(product.available)

    def test_invalid_form_submission_does_not_create_product(self):
        """
        Test che un form non valido non crei un nuovo prodotto.
        """
        response = self.client.post(reverse('admin_add_product'), data=self.invalid_data)
        self.assertEqual(response.status_code, 200)  # Rende di nuovo il form con errori
        self.assertEqual(Product.objects.count(), 0)  # Nessun prodotto creato
        self.assertFormError(response, 'form', 'nome', 'This field is required.')





from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Order, CartItem, Product, Cart
from datetime import timedelta
from django.utils import timezone

class ManageOrdersViewTest(TestCase):

    def setUp(self):
        # Crea utenti di test
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

        # Crea un prodotto per i test
        self.product1 = Product.objects.create(nome="Prodotto 1", prezzo=10.00)
        self.product2 = Product.objects.create(nome="Prodotto 2", prezzo=15.00)

        # Crea un carrello per i test
        self.cart1 = Cart.objects.create(user=self.user1)
        self.cart2 = Cart.objects.create(user=self.user2)

        # Crea cart items per gli ordini
        self.cart_item1 = CartItem.objects.create(cart=self.cart1, product=self.product1, quantity=1)
        self.cart_item2 = CartItem.objects.create(cart=self.cart1, product=self.product2, quantity=2)

        # Crea ordini associati agli utenti e a cart_items
        self.order1 = Order.objects.create(user=self.user1, status='pending', total=40.00)
        self.order1.cart_items.add(self.cart_item1, self.cart_item2)

        cart_item3 = CartItem.objects.create(cart=self.cart2, product=self.product2, quantity=1)
        self.order2 = Order.objects.create(user=self.user1, status='completed', total=30.00)
        self.order2.cart_items.add(self.cart_item1)

        cart_item4 = CartItem.objects.create(cart=self.cart2, product=self.product1, quantity=1)
        self.order3 = Order.objects.create(user=self.user2, status='pending', total=50.00)
        self.order3.cart_items.add(self.cart_item2)

        self.order4 = Order.objects.create(user=self.user2, status='cancelled', total=0.00)
        self.order4.cart_items.add(self.cart_item2)

    def test_manage_orders_no_filters(self):
        """
        Test che la vista restituisca tutti gli ordini quando non vengono applicati filtri.
        """
        response = self.client.get(reverse('manage_orders'))

        self.assertEqual(response.status_code, 200)

        orders = list(response.context['orders'])
        self.assertEqual(len(orders), 4)  # 4 ordini creati
        self.assertEqual(str(orders[0]), f"Ordine #{self.order4.id} - user2")
        self.assertEqual(str(orders[1]), f"Ordine #{self.order3.id} - user2")
        self.assertEqual(str(orders[2]), f"Ordine #{self.order2.id} - user1")
        self.assertEqual(str(orders[3]), f"Ordine #{self.order1.id} - user1")

    def test_manage_orders_filter_by_user(self):
        """
        Test che la vista filtri gli ordini per utente selezionato.
        """
        response = self.client.get(reverse('manage_orders') + '?user=' + str(self.user1.id))

        self.assertEqual(response.status_code, 200)

        orders = list(response.context['orders'])
        self.assertEqual(len(orders), 2)  # 2 ordini per user1
        self.assertEqual(str(orders[0]), f"Ordine #{self.order2.id} - user1")
        self.assertEqual(str(orders[1]), f"Ordine #{self.order1.id} - user1")

    def test_manage_orders_filter_by_status(self):
        """
        Test che la vista filtri gli ordini per stato selezionato.
        """
        response = self.client.get(reverse('manage_orders') + '?status=pending')

        self.assertEqual(response.status_code, 200)

        orders = list(response.context['orders'])
        self.assertEqual(len(orders), 2)  # 2 ordini con stato 'pending'
        self.assertEqual(str(orders[0]), f"Ordine #{self.order3.id} - user2")
        self.assertEqual(str(orders[1]), f"Ordine #{self.order1.id} - user1")

    def test_manage_orders_filter_by_user_and_status(self):
        """
        Test che la vista filtri gli ordini per utente e stato selezionato.
        """
        response = self.client.get(reverse('manage_orders') + '?user=' + str(self.user1.id) + '&status=pending')

        self.assertEqual(response.status_code, 200)

        orders = list(response.context['orders'])
        self.assertEqual(len(orders), 1)  # 1 ordine per user1 con stato 'pending'
        self.assertEqual(str(orders[0]), f"Ordine #{self.order1.id} - user1")

    def test_manage_orders_no_filters_empty(self):
        """
        Test che la vista restituisca una lista vuota quando non ci sono ordini.
        """
        Order.objects.all().delete()
        response = self.client.get(reverse('manage_orders'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['orders'], [])

    def test_manage_orders_user_and_status_context(self):
        """
        Test che il contesto contenga gli utenti e i parametri selezionati.
        """
        response = self.client.get(reverse('manage_orders') + '?user=' + str(self.user1.id) + '&status=completed')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_user'], str(self.user1.id))
        self.assertEqual(response.context['selected_status'], 'completed')
        self.assertIn(self.user1, response.context['users'])
        self.assertIn(self.user2, response.context['users'])

    def test_get_cart_item_total_price(self):
        """
        Test che il metodo `get_total_price` calcoli correttamente il totale per il cart item.
        """
        # Test cart_item1
        expected_total1 = Decimal('10.00')  # 10.00 * 1
        self.assertEqual(self.cart_item1.get_total_price(), expected_total1)

        # Test cart_item2
        expected_total2 = Decimal('30.00')  # 15.00 * 2
        self.assertEqual(self.cart_item2.get_total_price(), expected_total2)

    def test_get_combined_cart_total(self):
        """
        Test che il totale combinato del carrello sia corretto (cart_item1 + cart_item2)
        """
        # Calcola il totale del carrello
        total = self.cart_item1.get_total_price() + self.cart_item2.get_total_price()
        expected_combined_total = Decimal('40.00')  # 10.00 + 30.00
        self.assertEqual(total, expected_combined_total)