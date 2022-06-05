def percentage(value):
    return value / 100


def percentage_account(value, percent):
    return value + value * percentage(percent)


def percentage_discount(value, percent):
    return value - value * percentage(percent)
