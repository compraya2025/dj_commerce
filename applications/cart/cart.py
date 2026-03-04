from applications.store.models import Product, Profile


class Cart:
    def __init__(self, request):
        self.session = request.session

        self.request = request

        cart = self.session.get('cart')

        if not cart:
            cart = self.session['cart'] = {}

        self.cart = cart
    
    def db_add(self,product, quantity):
        product_id = str(product)
        product_qty = str(quantity)

        if product_id in self.cart:
            pass
        else:
            #self.cart[product_id] = {'price': str(product.sale_price)}
            self.cart[product_id] = int(product_qty)
        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user_id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            current_user.update(old_cart = str(carty))

    def add(self, product, quantity=1):
        product_id = str(product.id)
        product_qty = str(quantity)

        if product_id not in self.cart:
            self.cart[product_id] = quantity
        else:
            self.cart[product_id] += quantity

        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user_id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            current_user.update(old_cart = str(carty))


    def __len__(self):
        return sum(self.cart.values())

    def get_products(self):
        product_ids = self.cart.keys()
        return Product.objects.filter(id__in=product_ids)

    def get_quantities(self):
        quantities = self.cart
        return quantities

    def update(self, product_id, quantity):
        product_id = str(product_id)
        self.cart[product_id] = quantity
        self.session.modified = True

    def delete(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
        self.session.modified = True

    def cart_total(self):
        product_ids = self.cart.keys()

        products = Product.objects.filter(id__in=product_ids).values(
            'id', 'price', 'sale_price', 'promotion'
        )

        total = 0

        for product in products:
            price = product['sale_price'] if product['promotion'] and product['sale_price'] else product['price']
            qty = self.cart.get(str(product['id']), 0)
            total += price * qty

        return total