from myhdl import block, Signal, ResetSignal, intbv, instances
from comparator import code_comparator
from debounce import debounce_sync
from countdown_timer import countdown_timer
from alarm_fsm import alarm_fsm
from sevensegdec import sevensegdec
from siren_pwm import siren_generator

@block
def top_alarm(
    clk,
    rst,
    sw_code,
    sw_pir,
    btnc,
    seg_n,
    an_n,
    leds,
    rgb_led,
    aud_pwm,
    aud_sd,
    timer_period=100_000_000,
    debounce_cycles=50_000,
    tone_half_period=50_000
):
    """
    Modulo Top-Level del Sistema de Alarma con Retardo (Propuesta 12)
    para la tarjeta Digilent Nexys 4 DDR (Artix-7).
    Clave por defecto fijada en hardware: 4'b1010 (10 en decimal, SW3=1, SW2=0, SW1=1, SW0=0).
    """
    key_ref = Signal(intbv(0b1010)[4:])
    code_ok = Signal(bool(0))
    btn_pulse = Signal(bool(0))

    en_timer = Signal(bool(0))
    clear_timer = Signal(bool(1))
    count = Signal(intbv(9)[4:])
    time_up = Signal(bool(0))

    state = Signal(intbv(0)[3:])
    siren_en = Signal(bool(0))
    seg_pos = Signal(intbv(0)[7:])

    u_comp = code_comparator(sw_code, key_ref, code_ok)
    u_deb = debounce_sync(clk, rst, btnc, btn_pulse, stable_cycles=debounce_cycles)
    u_timer = countdown_timer(clk, rst, en_timer, clear_timer, count, time_up, period=timer_period, start_val=9)
    u_fsm = alarm_fsm(clk, rst, btn_pulse, code_ok, sw_pir, time_up, state, en_timer, clear_timer, siren_en)
    u_seg7 = sevensegdec(count, state, seg_pos, seg_n, an_n)
    u_siren = siren_generator(clk, rst, siren_en, state, aud_pwm, aud_sd, leds, rgb_led, tone_half_period=tone_half_period)

    return instances()


if __name__ == "__main__":
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

    inst = top_alarm(clk, rst, sw_code, sw_pir, btnc, seg_n, an_n, leds, rgb_led, aud_pwm, aud_sd)
    inst.convert(hdl="Verilog", name="top_alarm")
    print("Archivo top_alarm.v generado exitosamente.")