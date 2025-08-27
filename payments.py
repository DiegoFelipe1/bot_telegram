# encoding: utf-8

from efipay import EfiPay

credentials = {
    'client_id': 'Client_Id_2ccded7f2e17a695c6f4caafc74cec83fd02f290',
    'client_secret': 'Client_Secret_0fa11f1e0014a8b186e8fae7fcefd2901eaff157',
    'sandbox': False,
    'certificate': r'C:\Users\fdieg\Desktop\Nova pasta\certificadoPROD3.pem'
}

efi = EfiPay(credentials)

body = {
    'calendario': {
        'expiracao': 3600
    },
    'devedor': {
        'cpf': '12345678909',
        'nome': 'Francisco da Silva'
    },
    'valor': {
        'original': '123.45'
    },
    'chave': '62aa69e4-974e-49e6-8d50-0f8aea701bd0',
    'solicitacaoPagador': 'Cobrança dos serviços prestados.'
}

response =  efi.pix_create_immediate_charge(body=body)
print(response)