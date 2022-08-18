import concurrent.futures
import time
import threading

class BankAccount:
    def __init__(self):
        self.balance = 100
        self.lock_obj = threading.Lock()

    def update(self, transaction, amount):
        print(f'{transaction} started')

        with self.lock_obj:
            tmp_amount = self.balance
            tmp_amount += amount
            time.sleep(1)
            self.balance = tmp_amount
        print(f'{transaction} ended')

if __name__ == '__main__':
    acc = BankAccount()
    print(f'Main started. acc.balance={acc.balance}')

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        ex.map(acc.update, ('refill', 'withdraw'), (100, -200))

    print(f'End of main. Balance={acc.balance}')
        
