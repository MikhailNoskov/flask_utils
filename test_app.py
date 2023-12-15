import os
from my_app import create_app, db
import unittest
import tempfile
import coverage


class CatalogTestCase(unittest.TestCase):

    def setUp(self):
        test_config = {}
        self.test_db_file = tempfile.mkstemp()[1]
        test_config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.test_db_file
        test_config['TESTING'] = True
        test_config['WTF_CSRF_ENABLED'] = False

        self.app = create_app(test_config)
        db.init_app(self.app)

        with self.app.app_context():
            db.create_all()

        from my_app.catalog.views import catalog
        self.app.register_blueprint(catalog)
        from my_app.auth.views import auth_route
        self.app.register_blueprint(auth_route)

        self.client = self.app.test_client()

    def tearDown(self):
        os.remove(self.test_db_file)

    # def test_home(self):
    #     response = self.client.get('/home')
    #     self.assertEqual(response.status_code, 200)

    def test_products(self):
        """Test Products list page"""
        response = self.client.get('/products')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Previous Page' in response.data.decode("utf-8"))
        self.assertTrue('Next Page' in response.data.decode("utf-8"))

    def test_create_category(self):
        """Test creation of new category"""
        response = self.client.get('/category-create')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/category-create', data={'name': 'Pads'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/categories')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Pads' in response.data.decode("utf-8"))

        response = self.client.get('/category/1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Pads' in response.data.decode("utf-8"))

    def test_create_product(self):
        """Test creation of new product"""
        response = self.client.get('/product-create')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/category-create', data={'name': 'Phones'})
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/product-create', data={
            'name': 'iPhone 5',
            'price': 549.49,
            'company': 'Apple',
            'category': 1,
            'image': tempfile.NamedTemporaryFile()
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/products')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('iPhone 5' in response.data.decode("utf-8"))

    def test_search_product(self):
        """Test searching product"""
        #  Create a category to be used in product creation
        response = self.client.post('/category-create', data={
            'name': 'Phones'}
        )
        self.assertEqual(response.status_code, 200)

        # Create a product
        response = self.client.post('/product-create', data={
            'name': 'iPhone 5',
            'price': 549.49,
            'company': 'Apple',
            'category': 1,
            'image': tempfile.NamedTemporaryFile()
        })
        self.assertEqual(response.status_code, 302)

        # Create another product
        response = self.client.post('/product-create', data={
            'name': 'Galaxy S5',
            'price': 549.49,
            'company': 'Samsung',
            'category': 1,
            'image': tempfile.NamedTemporaryFile()
        })
        self.assertEqual(response.status_code, 302)

        self.client.get('/products')   # to close create alerts

        response = self.client.get('/product-search?name=iPhone')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('iPhone 5' in response.data.decode("utf-8"))
        self.assertFalse('Galaxy S5' in response.data.decode("utf-8"))

        response = self.client.get('/product-search?name = iPhone 6')
        self.assertEqual(response.status_code, 200)
        self.assertFalse('iPhone 6' in response.data.decode("utf-8"))


cov = coverage.coverage(
    omit = [
        '/home/mike/PycharmProjects/flask_utils'
        '/Users/apple/workspace/flask-cookbook-3//lib/python3.10/site-packages/*',
        'test_app.py'
    ]
)
cov.start()


if __name__ == '__main__':
    try:
        unittest.main()
    finally:
        cov.stop()
        cov.save()
        cov.report()
        cov.html_report(directory='coverage')
        cov.erase()