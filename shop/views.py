import stripe

from django.urls import reverse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.utils import IntegrityError
from django.core.mail import send_mail

from .models import Category, Product, Review, FavoriteProducts, Mail, Customer
from .forms import LoginForm, RegistrationForm, ReviewForm, ShippingForm, CustomerForm
from .utils import CartForAuthenticatedUser, get_cart_data
from app import settings


class Index(ListView):
    """Главная страница"""
    model = Product
    context_object_name = 'categories'
    extra_context = {'title': 'Главная страница'}
    template_name = 'shop/index.html'

    def get_queryset(self):
        """Вывод родительской категории"""
        categories = Category.objects.filter(parent=None)
        return categories

    def get_context_data(self, *, object_list=None, **kwargs):
        """Вывод на страницу дополнительных элементов"""
        context = super().get_context_data()
        context['top_products'] = Product.objects.order_by('-watched')[:3]
        return context


class SubCategories(ListView):
    """Вывод подкатегории на отдельной странице"""
    paginate_by = 2
    model = Product
    context_object_name = 'products'
    template_name = 'shop/category_page.html'

    def get_queryset(self):
        """Получение всех товаров подкатегории"""
        type_field = self.request.GET.get('type')
        if type_field:
            products = Product.objects.filter(category__slug=type_field)
            return products

        parent_category = Category.objects.get(slug=self.kwargs['slug'])
        subcategories = parent_category.subcategories.all()
        products = Product.objects.filter(category__in=subcategories)

        sort_field = self.request.GET.get('sort')
        if sort_field:
            products = products.order_by(sort_field)

        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        """Дополнительные элементы"""
        context = super().get_context_data()
        parent_category = Category.objects.get(slug=self.kwargs['slug'])
        context['category'] = parent_category
        context['title'] = parent_category.title
        return context


class ProductPage(DetailView):
    """Вывод товара на отдельной странице"""
    model = Product
    context_object_name = 'product'
    template_name = 'shop/product_page.html'

    def get_context_data(self, **kwargs):
        """Вывод на страницу дополнительных элементов"""
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        products = Product.objects.all().exclude(slug=self.kwargs['slug']).filter(category=product.category)[:5]
        context['title'] = product.title
        context['products'] = products
        context['reviews'] = Review.objects.filter(product=product).order_by('-pk')

        # Показывать форму отзыва, если пользователь прошел авторизацию
        if self.request.user.is_authenticated:
            context['review_form'] = ReviewForm

        return context


class FavoriteProductsView(LoginRequiredMixin, ListView):
    """Для вывода избранных на страницу"""
    model = FavoriteProducts
    context_object_name = 'products'
    template_name = 'shop/favorite_products.html'
    login_url = 'user_registration'

    def get_queryset(self):
        """Получаем товары конкретного пользователя"""
        user = self.request.user
        favs = FavoriteProducts.objects.filter(user=user)
        products = [i.product for i in favs]
        return products


def login_registration(request):
    """Страница Входа/Регистрации"""
    context = {
        'title': 'Войти/Зарегистрироваться',
        'login_form': LoginForm,
        'registration_form': RegistrationForm
    }
    return render(request, 'shop/login_registration.html', context)


def user_login(request):
    """Авторизация пользователя"""
    form = LoginForm(data=request.POST)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('index')
    else:
        messages.error(request, 'Неверное имя пользователя или пароль')
        return redirect('login_registration')


def user_registration(request):
    """Регистрация пользователя"""
    form = RegistrationForm(data=request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Аккаунт пользователя успешно создан! Пожалуйста войдите в свой аккаунт!')
        return redirect('login_registration')
    else:
        for error in form.errors:
            messages.error(request, form.errors[error].as_text())
        return redirect('login_registration')


def user_logout(request):
    """Выход пользователя из личного кабинета"""
    logout(request)
    return redirect('login_registration')


def save_review(request, product_pk):
    """Сохранение отзыва"""
    form = ReviewForm(data=request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.author = request.user
        product = Product.objects.get(pk=product_pk)
        review.product = product
        review.save()
        return redirect('product_page', product.slug)


def save_favorite_product(request, product_slug):
    """Добавление/удаление товара с избранных"""
    user = request.user if request.user.is_authenticated else None
    product = Product.objects.get(slug=product_slug)
    favorite_products = FavoriteProducts.objects.filter(user=user)
    if user:
        if product in [i.product for i in favorite_products]:
            fav_product = FavoriteProducts.objects.get(user=user, product=product)
            fav_product.delete()
        else:
            FavoriteProducts.objects.create(user=user, product=product)

        next_page = request.META.get('HTTP_REFERER', 'category_detail')
        return redirect(next_page)


def save_subscribers(request):
    """Собиратель почтовых адресов"""
    email = request.POST.get('email')
    user = request.user if request.user.is_authenticated else None
    if email:
        try:
            Mail.objects.create(mail=email, user=user)
            messages.success(request, 'Ваш почтовый адрес успешно зарегистрирован')
        except IntegrityError:
            messages.error(request, 'Вы уже являетесь подписчиком')
    return redirect('index')


def cart(request):
    """Страница корзины"""
    cart_info = get_cart_data(request)
    context = {
        'order': cart_info['order'],
        'order_products': cart_info['order_products'],
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'title': 'Корзина'
    }
    return render(request, 'shop/cart.html', context)


def to_cart(request, product_id, action):
    """Добавляет товар в корзину"""
    if request.user.is_authenticated:
        CartForAuthenticatedUser(request, product_id, action)
        return redirect('cart')
    else:
        messages.error(request, 'Авторизуйтесь или зарегистрируйтесь, чтобы совершать покупки')
        return redirect('login_registration')


def checkout(request):
    """Страница оформления заказа"""
    cart_info = get_cart_data(request)
    context = {
        'order': cart_info['order'],
        'order_products': cart_info['order_products'],
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'customer_form': CustomerForm(),
        'shipping_form': ShippingForm(),
        'title': 'Оформление заказа'
    }
    return render(request, 'shop/checkout.html', context)


def create_checkout_session(request):
    """Оплата на Stripe"""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()
        customer_form = CustomerForm(data=request.POST)
        if customer_form.is_valid():
            customer = Customer.objects.get(user=request.user)
            customer.first_name = customer_form.cleaned_data['first_name']
            customer.last_name = customer_form.cleaned_data['last_name']
            customer.email = customer_form.cleaned_data['email']
            customer.phone = customer_form.cleaned_data['phone']
            customer.save()
        shipping_form = ShippingForm(data=request.POST)
        if shipping_form.is_valid():
            address = shipping_form.save(commit=False)
            address.customer = Customer.objects.get(user=request.user)
            address.order = user_cart.get_cart_info()['order']
            address.save()

        total_price = cart_info['cart_total_price']
        total_quantity = cart_info['cart_total_quantity']

        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {'currency': 'usd',
                               'product_data': {'name': 'Товары с shop lux'},
                               'unit_amount': int(total_price * 100)},
                'quantity': total_quantity}],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('success'))
        )
        return redirect(session.url, 303)


def successPayment(request):
    """Оплата прошла успешно"""
    user_cart = CartForAuthenticatedUser(request)
    user_cart.clear()
    messages.success(request, 'Оплата прошла успешно')
    return render(request, 'shop/success.html')


def send_mail_to_subscribers(request):
    """Отправка писем подписчикам"""
    if request.method == 'POST':
        text = request.POST.get('text')
        mail_list = Mail.objects.all()
        for email in mail_list:
            send_mail(
                subject='У нас новая акция',
                message=text,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email.mail],
                fail_silently=False
            )
            print(f'Сообщение отправлено на почту: {email} ------ {bool(send_mail)}')

    context = {'title': 'Спаммер'}
    return render(request, 'shop/send_email.html', context)

