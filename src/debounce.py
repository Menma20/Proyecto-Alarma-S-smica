from myhdl import block, Signal, intbv, always_seq

@block
def debounce_sync(clk, rst, btn_in, btn_pulse, stable_cycles=4):
    """
    Sincroniza la entrada asincrona de un boton con el reloj del sistema,
    filtra rebotes mecanicos y genera un pulso limpio de 1 ciclo de reloj
    en el flanco de subida.
    """
    cnt_width = max(2, (stable_cycles + 1).bit_length())
    cnt = Signal(intbv(0)[cnt_width:])
    sync_0 = Signal(bool(0))
    sync_1 = Signal(bool(0))
    btn_stable = Signal(bool(0))
    btn_prev = Signal(bool(0))

    @always_seq(clk.posedge, reset=rst)
    def logic():
        # Doble flip-flop para evitar metastabilidad
        sync_0.next = btn_in
        sync_1.next = sync_0

        # Filtro antirrebote por conteo de ciclos estables
        if sync_1 != btn_stable:
            if cnt == stable_cycles - 1:
                btn_stable.next = sync_1
                cnt.next = 0
            else:
                cnt.next = cnt + 1
        else:
            cnt.next = 0

        # Detector de flanco de subida (genera pulso de 1 ciclo)
        btn_prev.next = btn_stable
        if (btn_stable == 1) and (btn_prev == 0):
            btn_pulse.next = 1
        else:
            btn_pulse.next = 0

    return logic
