from src.utils import read_file
from src.views import main_page
from src.reports import spending_by_category
from src.services import search_by_client_name, search_by_phone, search_by_word


def main():
    transactions = read_file("operations.xlsx")
    transactions_dict = transactions.to_dict(orient="records")

    print(main_page(input_date="2021-05-20 17:30:24"))
    print(search_by_word(transactions_dict, "перевод"))
    print(search_by_phone(transactions_dict))
    print(search_by_client_name(transactions_dict))
    print(spending_by_category(transactions, category="Супермаркеты", date="2021-12-31"))


if __name__ == "__main__":
    main()
