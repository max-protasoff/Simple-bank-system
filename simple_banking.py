import sqlite3
import random

# Create a database and cursor
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

# Global variable (counter), which value will be in DB column id
id = 0

cur.execute('CREATE TABLE IF NOT EXISTS card(id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);')
conn.commit()

# Creating a new account
def create_account():
    global id
    iin = '400000'
    mii = iin[0]
    can = ''
    for can_digit in range(9):
        can = can + str(random.randint(0,9))
    luhn = iin + can
    check_sum = str(luhn_create(luhn))
    card_num = iin + can + check_sum
    pin = ''
    for pin_digit in range(4):
        pin = pin + str(random.randint(0,9))

    cur.execute(f"SELECT number FROM card WHERE number = '{card_num}'")
    if cur.fetchone() is None:
        cur.execute(f"INSERT INTO card (id, number, pin, balance) VALUES (?, ?, ?, ?)", (id, card_num, pin, 0))
        conn.commit()
        id += 1
    else:
        pass

    return f'''\nYour card has been created
Your card number:
{card_num}
Your card PIN:
{pin}\n'''


# Creates the last (16th) digit in card number according to Luhn algoritm
def luhn_create(luhn):
    luhn_list = [int(luhn[i]) * 2 if i % 2 == 0 else int(luhn[i]) for i in range(0, 15)]
    luhn_list = [x - 9 if x > 9 else x for x in luhn_list]
    luhn_int = sum(luhn_list)
    luhn_num_check = 10 - (luhn_int % 10)
    if luhn_num_check == 10:
        return 0
    else:
        return luhn_num_check

# Checks if the receiver card meets Luhn algoritm requirements
def luhn_check(luhn):
    luhn_list = [int(luhn[i]) * 2 if i % 2 == 0 else int(luhn[i]) for i in range(0, 15)]
    luhn_list = [x - 9 if x > 9 else x for x in luhn_list]
    luhn_int = sum(luhn_list)
    if (luhn_int + int(luhn[15])) % 10 == 0:
        return True
    else:
        pass


# check card number and pin in db and enter menu for valid users
def log_in():
    card_num_user = input('\nEnter your card number:')
    pin_user = input('Enter your PIN:')
    cur.execute(f"SELECT * FROM card WHERE number = {card_num_user}")
    card_check = cur.fetchone()
    if card_check is None:
        print('\nWrong card number or PIN!')
    else:
        if card_check[1] == card_num_user:
            if card_check[2] == pin_user:
                print('\nYou have successfully logged in!')
                menu_logged(card_check)
            else:
                print('Wrong card number or PIN!')



# Main menu
def menu():
    while True:
        query = input('''1. Create an account
2. Log into account
0. Exit\n''')
        if query == '1':
            print(create_account())
        elif query == '2':
            log_in()
            continue
        elif query == '0':
            print('\nBye!')
            conn.close()
            exit()

# Menu after entering valid card number and password
def menu_logged(row_from_db_tuple):
    while True:
        cur.execute(f"SELECT * FROM card WHERE number = {row_from_db_tuple[1]}")
        user_data = cur.fetchone()
        query = input('''\n1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit\n''')
        if query == '1':
            print(balance_check(user_data))
            continue
        elif query == '2':
            add_income(user_data)
            continue
        elif query == '3':
            do_transfer(user_data)
            continue
        elif query == '4':
            print(close_account(user_data))
            menu()
            break
        elif query == '5':
            print('\nYou have successfully logged out!')
            menu()
            break
        elif query == '0':
            print('\nBye!')
            conn.close()
            exit()


# Add extra money to person's DB column balance
def add_income(user_data):
    income = int(input('\nEnter income:\n'))
    cur.execute(f"UPDATE card SET balance = balance + {income} WHERE number = {user_data[1]}")
    conn.commit()
    print('Income was added!')


# check if receiver's card number valid and transfer money
def do_transfer(user_data):
    while True:
        print('\nTransfer')
        receiver_card = input('Enter card number:\n')
        if luhn_check(receiver_card) == True:
            cur.execute(f"SELECT * FROM card WHERE number = {receiver_card}")
            receiver_tuple = cur.fetchone()
            if receiver_tuple == None:
                print('Such a card does not exist.')
                break
            else:
                if user_data[1] == receiver_tuple[1]:
                    print("You can't transfer money to the same account!")
                    break
                else:
                    money_transfer = int(input('Enter how much money you want to transfer:\n'))
                    if money_transfer > user_data[3]:
                        print('Not enough money!')
                        break
                    elif money_transfer <= user_data[3]:
                        cur.execute(f"UPDATE card SET balance = balance + {money_transfer} WHERE number = {receiver_tuple[1]}")
                        conn.commit()
                        cur.execute(f"UPDATE card SET balance = balance - {money_transfer} WHERE number = {user_data[1]}")
                        conn.commit()
                        print('Success!')
                        break

        else:
            print('Probably you made mistake in the card number. Please try again!')
            break





# Delete row containing card id, number, pin and balance and return to the main menu
def close_account(user_data):
    cur.execute(f"DELETE FROM card WHERE number = {user_data[1]}")
    conn.commit()
    return '\nThe account has been closed!\n'

# Asks for fresh column balance value according to card number
def balance_check(user_data):
    cur.execute(f"SELECT * FROM card WHERE number = {user_data[1]}")
    updated_balance = cur.fetchone()
    return f'\nBalance: {updated_balance[3]}'

# Start program
menu()
