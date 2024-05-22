import threading
import queue

from .models import Transaction

payment_queue = queue.Queue()


def process_payment():
    while True:
        transaction = payment_queue.get()
        print("=" * 50)
        print(transaction)
        trans_object = Transaction.objects.get(reference=transaction.get("tx_ref"))

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
