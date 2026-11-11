import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from myhdl import Signal, ResetSignal, intbv, delay, always, instance, Simulation, StopSimulation
from comparator import code_comparator
from debounce import debounce_sync
from countdown_timer import countdown_timer
from alarm_fsm import alarm_fsm, ST_DESARMADA, ST_RETARDO_SALIDA, ST_ARMADA, ST_RETARDO_ENTRADA, ST_DISPARADA
from sevensegdec import sevensegdec, SEG_TABLE
from top_alarm import top_alarm


# T01: Prueba unitaria exhaustiva del comparador de codigo (16 combinaciones)
def test_t01_comparator_exhaustive():
    sw_code = Signal(intbv(0)[4:])
    key_ref = Signal(intbv(0b1010)[4:])
    code_ok = Signal(bool(0))

    dut = code_comparator(sw_code, key_ref, code_ok)

    @instance
    def stim():
        for i in range(16):
            sw_code.next = i
            yield delay(10)
            if i == 0b1010:
                assert int(code_ok) == 1, f"Fallo en clave correcta {i}"
            else:
                assert int(code_ok) == 0, f"Falso positivo en {i}"
        raise StopSimulation

    Simulation(dut, stim).run()


# T02: Prueba unitaria exhaustiva del decodificador de 7 segmentos
def test_t02_sevenseg_exhaustive():
    count = Signal(intbv(0)[4:])
    state = Signal(intbv(1)[3:])  # Estado 1 (retardo) muestra los digitos 0..9
    seg = Signal(intbv(0)[7:])
    seg_n = Signal(intbv(0)[7:])
    an_n = Signal(intbv(0)[8:])

    dut = sevensegdec(count, state, seg, seg_n, an_n)

    @instance
    def stim():
        # Verificar digitos 0..9 en modo cuenta regresiva
        for d in range(10):
            count.next = d
            yield delay(10)
            assert int(seg) == SEG_TABLE[d]
            assert int(seg_n) == ((~SEG_TABLE[d]) & 0x7F)

        # Verificar letras de estado: Desarmada ('d'), Armada ('A'), Disparada ('E')
        state.next = ST_DESARMADA
        yield delay(10)
        assert int(seg) == SEG_TABLE[13]

        state.next = ST_ARMADA
        yield delay(10)
        assert int(seg) == SEG_TABLE[10]

        state.next = ST_DISPARADA
        yield delay(10)
        assert int(seg) == SEG_TABLE[14]
        raise StopSimulation

    Simulation(dut, stim).run()


# T03: Prueba unitaria del temporizador de cuenta regresiva con period reducido
def test_t03_countdown_timer():
    clk = Signal(bool(0))
    rst = ResetSignal(1, active=0, isasync=False)
    en_timer = Signal(bool(0))
    clear_timer = Signal(bool(0))
    count = Signal(intbv(9)[4:])
    time_up = Signal(bool(0))

    dut = countdown_timer(clk, rst, en_timer, clear_timer, count, time_up, period=3, start_val=3)

    @always(delay(5))
    def clkgen():
        clk.next = not clk

    @instance
    def stim():
        def tick(n=1):
            for _ in range(n):
                yield clk.posedge
                yield delay(1)

        # Reset inicial
        rst.next = 0
        yield from tick(2)
        rst.next = 1
        clear_timer.next = 1
        yield from tick(1)
        clear_timer.next = 0
        en_timer.next = 1

        # Cuenta inicial = 3; cada 3 ciclos baja 1 segundo
        assert int(count) == 3
        for expected in (2, 1, 0):
            yield from tick(3)
            assert int(count) == expected

        assert int(time_up) == 1
        raise StopSimulation

    Simulation(dut, clkgen, stim).run()


# T04: Prueba unitaria de la FSM (Armado, Retardo, Intrusion, Disparo y Desarme)
def test_t04_alarm_fsm_sequence():
    clk = Signal(bool(0))
    rst = ResetSignal(1, active=0, isasync=False)
    btn_pulse = Signal(bool(0))
    code_ok = Signal(bool(0))
    sensor_pir = Signal(bool(0))
    time_up = Signal(bool(0))

    state = Signal(intbv(0)[3:])
    en_timer = Signal(bool(0))
    clear_timer = Signal(bool(1))
    siren_en = Signal(bool(0))

    dut = alarm_fsm(clk, rst, btn_pulse, code_ok, sensor_pir, time_up, state, en_timer, clear_timer, siren_en)

    @always(delay(5))
    def clkgen():
        clk.next = not clk

    @instance
    def stim():
        def tick(n=1):
            for _ in range(n):
                yield clk.posedge
                yield delay(1)

        # 1. Reset a DESARMADA
        rst.next = 0
        yield from tick(2)
        rst.next = 1
        yield from tick(1)
        assert int(state) == ST_DESARMADA

        # 2. Ingreso de clave correcta -> RETARDO_SALIDA
        code_ok.next = 1
        btn_pulse.next = 1
        yield from tick(1)
        btn_pulse.next = 0
        assert int(state) == ST_RETARDO_SALIDA
        assert int(en_timer) == 1

        # 3. Fin del retardo de salida -> ARMADA
        time_up.next = 1
        yield from tick(1)
        time_up.next = 0
        assert int(state) == ST_ARMADA

        # 4. Deteccion de intruso (sensor_pir=1) -> RETARDO_ENTRADA
        sensor_pir.next = 1
        yield from tick(1)
        sensor_pir.next = 0
        assert int(state) == ST_RETARDO_ENTRADA
        assert int(en_timer) == 1

        # 5. Se agota el tiempo sin meter clave -> DISPARADA (sirena activa)
        code_ok.next = 0
        time_up.next = 1
        yield from tick(1)
        time_up.next = 0
        assert int(state) == ST_DISPARADA
        assert int(siren_en) == 1

        # 6. Usuario ingresa clave correcta y presiona boton -> DESARMADA
        code_ok.next = 1
        btn_pulse.next = 1
        yield from tick(1)
        btn_pulse.next = 0
        assert int(state) == ST_DESARMADA
        assert int(siren_en) == 0
        raise StopSimulation

    Simulation(dut, clkgen, stim).run()


# T05: Prueba de integracion del Top-Level completo
def test_t05_top_integration():
    clk = Signal(bool(0))
    rst = ResetSignal(1, active=0, isasync=False)
    sw_code = Signal(intbv(0)[4:])
    sw_pir = Signal(bool(0))
    btnc = Signal(bool(0))

    seg_n = Signal(intbv(0)[7:])
    an_n = Signal(intbv(0)[8:])
    leds = Signal(intbv(0)[16:])
    rgb_led = Signal(intbv(0)[3:])
    aud_pwm = Signal(bool(0))
    aud_sd = Signal(bool(0))

    dut = top_alarm(
        clk, rst, sw_code, sw_pir, btnc,
        seg_n, an_n, leds, rgb_led, aud_pwm, aud_sd,
        timer_period=2, debounce_cycles=2, tone_half_period=2
    )

    @always(delay(5))
    def clkgen():
        clk.next = not clk

    @instance
    def stim():
        def tick(n=1):
            for _ in range(n):
                yield clk.posedge
                yield delay(1)

        rst.next = 0
        yield from tick(2)
        rst.next = 1
        yield from tick(2)
        # Estado inicial: Verde (0b010)
        assert int(rgb_led) == 0b010

        # Poner clave correcta (1010) y presionar boton durante 8 ciclos
        sw_code.next = 0b1010
        btnc.next = 1
        yield from tick(8)
        btnc.next = 0
        # Debe estar en RETARDO_SALIDA (Amarillo = 0b110)
        assert int(rgb_led) == 0b110

        # Esperar cuenta regresiva completa (9 a 0 con timer_period=2 -> 25 ciclos)
        yield from tick(25)
        # Ahora debe estar en ARMADA (Azul = 0b001)
        assert int(rgb_led) == 0b001

        # Activar sensor de intrusion (SW15 / sw_pir) durante 3 ciclos
        sw_pir.next = 1
        yield from tick(3)
        sw_pir.next = 0
        assert int(rgb_led) == 0b110  # Retardo de entrada (Amarillo)

        # Dejar que expire el tiempo sin desarmar
        sw_code.next = 0b0000
        yield from tick(25)
        # Estado DISPARADA: LED Rojo (0b100) y amplificador de audio habilitado
        assert int(rgb_led) == 0b100
        assert int(aud_sd) == 1
        raise StopSimulation

    Simulation(dut, clkgen, stim).run()