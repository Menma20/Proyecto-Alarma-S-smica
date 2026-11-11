from myhdl import block, always_comb

# Tabla LUT de 7 segmentos (a..g en bits 6..0, logica positiva 1=encendido):
# Indices: 0-9, 10(A=Armada), 11(b), 12(C), 13(d=Desarmada), 14(E=Error/Disparada), 15(F)
SEG_TABLE = (
    0b1111110, # 0
    0b0110000, # 1
    0b1101101, # 2
    0b1111001, # 3
    0b0110011, # 4
    0b1011011, # 5
    0b1011111, # 6
    0b1110000, # 7
    0b1111111, # 8
    0b1111011, # 9
    0b1110111, # 10 -> A (Armada)
    0b0011111, # 11 -> b
    0b1001110, # 12 -> C
    0b0111101, # 13 -> d (Desarmada)
    0b1001111, # 14 -> E (Alarma Disparada)
    0b1000111  # 15 -> F
)

@block
def sevensegdec(count, state, seg, seg_n, an_n):
    """
    Decodificador combinacional para el display de 7 segmentos de la Nexys 4 DDR.
    Sin variables locales intermedias para garantizar conversion directa a Verilog en MyHDL.
    """
    @always_comb
    def logic():
        an_n.next = 0b11111110  # Habilita el digito 0 (AN0, activo en bajo)
        if state == 0:
            # 'd' (Desarmada)
            seg.next = 0b0111101
            seg_n.next = 0b1000010
        elif state == 2:
            # 'A' (Armada)
            seg.next = 0b1110111
            seg_n.next = 0b0001000
        elif state == 4:
            # 'E' (Alarma Disparada)
            seg.next = 0b1001111
            seg_n.next = 0b0110000
        else:
            # Estados de retardo (1 o 3): muestra la cuenta regresiva (0..9)
            if count == 0:
                seg.next = 0b1111110
                seg_n.next = 0b0000001
            elif count == 1:
                seg.next = 0b0110000
                seg_n.next = 0b1001111
            elif count == 2:
                seg.next = 0b1101101
                seg_n.next = 0b0010010
            elif count == 3:
                seg.next = 0b1111001
                seg_n.next = 0b0000110
            elif count == 4:
                seg.next = 0b0110011
                seg_n.next = 0b1001100
            elif count == 5:
                seg.next = 0b1011011
                seg_n.next = 0b0100100
            elif count == 6:
                seg.next = 0b1011111
                seg_n.next = 0b0100000
            elif count == 7:
                seg.next = 0b1110000
                seg_n.next = 0b0001111
            elif count == 8:
                seg.next = 0b1111111
                seg_n.next = 0b0000000
            else:
                seg.next = 0b1111011
                seg_n.next = 0b0000100

    return logic