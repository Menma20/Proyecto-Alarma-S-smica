from myhdl import block, Signal, intbv, always_seq

@block
def countdown_timer(clk, rst, en_timer, clear_timer, count, time_up, period=100_000_000, start_val=9):
    """
    Temporizador de cuenta regresiva (por defecto de 9 a 0 segundos).
    period define cuantos ciclos de reloj equivalen a 1 segundo:
    - En placa Nexys 4 DDR (100 MHz): period = 100_000_000
    - En simulacion (pytest): period = 3 (para pruebas rapidas)
    """
    pw = max(2, period.bit_length())
    presc = Signal(intbv(0)[pw:])

    @always_seq(clk.posedge, reset=rst)
    def logic():
        if clear_timer == 1:
            presc.next = 0
            count.next = start_val
            time_up.next = 0
        elif en_timer == 1:
            if count == 0:
                time_up.next = 1
                presc.next = 0
            else:
                time_up.next = 0
                if presc == period - 1:
                    presc.next = 0
                    if count == 1:
                        count.next = 0
                        time_up.next = 1
                    else:
                        count.next = count - 1
                else:
                    presc.next = presc + 1
        else:
            presc.next = 0
            time_up.next = 0

    return logic
