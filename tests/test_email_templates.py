from ops.email_templates import teste, entrada, saida

def test_templates():
    a,b = teste("a@a.com","b@b.com")
    assert "[AUTOTRADER]" in a and "Remetente" in b
    a,b = entrada("BTCUSDT","LONG", 100.0, 110.0, 3.21)
    assert "ENTRADA" in a and "BTCUSDT" in b
    a,b = saida("BTCUSDT", 105.0, 110.0, 5.55)
    assert "SAÍDA" in a and "BTCUSDT" in b
