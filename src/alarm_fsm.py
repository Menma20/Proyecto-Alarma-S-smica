from myhdl import block, always_seq

# Codificacion de estados de la FSM
ST_DESARMADA = 0
ST_RETARDO_SALIDA = 1
ST_ARMADA = 2
ST_RETARDO_ENTRADA = 3
ST_DISPARADA = 4

@block
def alarm_fsm(clk, rst, btn_pulse, code_ok, sensor_pir, time_up, state, en_timer, clear_timer, siren_en):
    """
    Maquina de estados finitos (FSM) que controla el sistema de alarma:
    0 (ST_DESARMADA): Sistema inactivo, esperando codigo + boton para armar.
    1 (ST_RETARDO_SALIDA): Cuenta regresiva (9..0 s) para que el usuario salga.
    2 (ST_ARMADA): Sistema vigilando el sensor de intrusion (sensor_pir).
    3 (ST_RETARDO_ENTRADA): Al detectar presencia, da cuenta regresiva (9..0 s) para desarmar.
    4 (ST_DISPARADA): Tiempo agotado sin desarmar; activa sirena PWM y LEDs de alerta.
    """
    @always_seq(clk.posedge, reset=rst)
    def logic():
        if state == ST_DESARMADA:
            en_timer.next = 0
            clear_timer.next = 1
            siren_en.next = 0
            if (btn_pulse == 1) and (code_ok == 1):
                state.next = ST_RETARDO_SALIDA
                clear_timer.next = 0
                en_timer.next = 1

        elif state == ST_RETARDO_SALIDA:
            en_timer.next = 1
            clear_timer.next = 0
            siren_en.next = 0
            if (btn_pulse == 1) and (code_ok == 1):
                state.next = ST_DESARMADA
                en_timer.next = 0
                clear_timer.next = 1
            elif time_up == 1:
                state.next = ST_ARMADA
                en_timer.next = 0
                clear_timer.next = 1

        elif state == ST_ARMADA:
            en_timer.next = 0
            clear_timer.next = 1
            siren_en.next = 0
            if (btn_pulse == 1) and (code_ok == 1):
                state.next = ST_DESARMADA
            elif sensor_pir == 1:
                state.next = ST_RETARDO_ENTRADA
                clear_timer.next = 0
                en_timer.next = 1

        elif state == ST_RETARDO_ENTRADA:
            en_timer.next = 1
            clear_timer.next = 0
            siren_en.next = 0
            if (btn_pulse == 1) and (code_ok == 1):
                state.next = ST_DESARMADA
                en_timer.next = 0
                clear_timer.next = 1
            elif time_up == 1:
                state.next = ST_DISPARADA
                en_timer.next = 0
                clear_timer.next = 1
                siren_en.next = 1

        elif state == ST_DISPARADA:
            en_timer.next = 0
            clear_timer.next = 1
            siren_en.next = 1
            if (btn_pulse == 1) and (code_ok == 1):
                state.next = ST_DESARMADA
                siren_en.next = 0

        else:
            state.next = ST_DESARMADA
            en_timer.next = 0
            clear_timer.next = 1
            siren_en.next = 0

    return logic
