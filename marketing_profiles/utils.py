import random
import string


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def unique_invoice_id_generator(instance_marketing, instance_add_on):
    """
    This is for a Django project with an order_id field
    """
    invoice_new_id = random_string_generator()

    qs_marketing_exists = instance_marketing.objects.filter(invoice_id=invoice_new_id).exists()
    qs_add_on_exists = instance_add_on.objects.filter(invoice_id=invoice_new_id).exists()
    if qs_marketing_exists or qs_add_on_exists:
        return unique_invoice_id_generator(instance_marketing,instance_add_on)
    return invoice_new_id