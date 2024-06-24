import threading
import queue

from .models import Transaction

payment_queue = queue.Queue()


def process_payment():
    while True:
        transaction = payment_queue.get()
        trans_object = Transaction.objects.filter(reference=transaction.get("tx_ref"))
        if trans_object.exists():
            trans_object = trans_object.first()
        else:
            trans_object = None

        if trans_object and not trans_object.is_success:
            if (
                transaction.get("status") == "successful"
                and transaction.get("currency") == trans_object.currency
                and transaction.get("amount") == trans_object.amount
            ):
                # Do the transaction payment processing here
                trans_object.is_success = True
                trans_object.save()

        payment_queue.task_done()


# Start the thread
threading.Thread(target=process_payment, daemon=True).start()
