_ones = [
    '', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
    'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
    'Seventeen', 'Eighteen', 'Nineteen',
]
_tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']


def _two(n):
    if n < 20:
        return _ones[n]
    return (_tens[n // 10] + (' ' + _ones[n % 10] if n % 10 else '')).strip()


def _three(n):
    if n >= 100:
        rest = n % 100
        return _ones[n // 100] + ' Hundred' + (' ' + _two(rest) if rest else '')
    return _two(n)


def amount_to_words(amount):
    amount = int(round(float(amount)))
    if amount == 0:
        return 'Zero Rupees Only'

    parts = []
    crore, amount = divmod(amount, 10_000_000)
    lakh, amount = divmod(amount, 100_000)
    thousand, amount = divmod(amount, 1_000)

    if crore:
        parts.append(_three(crore) + ' Crore')
    if lakh:
        parts.append(_three(lakh) + ' Lakh')
    if thousand:
        parts.append(_three(thousand) + ' Thousand')
    if amount:
        parts.append(_three(amount))

    return ' '.join(parts) + ' Rupees Only'
