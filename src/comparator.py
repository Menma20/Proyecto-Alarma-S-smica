from myhdl import block, always_comb

@block
def code_comparator(sw_code, key_ref, code_ok):
    """
    Modulo combinacional que compara el codigo ingresado en los switches (4 bits)
    con la clave de referencia (4 bits).
    Equivale a puertas XNOR bit a bit seguidas de una puerta AND.
    """
    @always_comb
    def logic():
        if sw_code == key_ref:
            code_ok.next = 1
        else:
            code_ok.next = 0

    return logic
