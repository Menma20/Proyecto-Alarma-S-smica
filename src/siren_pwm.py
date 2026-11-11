from myhdl import block, Signal, intbv, always_seq

@block
def siren_generator(clk, rst, siren_en, state, aud_pwm, aud_sd, leds, rgb_led, tone_half_period=50_000):
    """
    Genera la alerta sonora (onda cuadrada para el amplificador PWM de audio)
    y controla los LEDs de estado y de alarma cuando siren_en == 1.
    - tone_half_period = 50_000 a 100 MHz genera un tono de 1 kHz.
    """
    tw = max(2, (tone_half_period + 1).bit_length())
    tone_cnt = Signal(intbv(0)[tw:])
    tone_reg = Signal(bool(0))

    @always_seq(clk.posedge, reset=rst)
    def logic():
        # Control del LED tricolor segun estado:
        # Bit 0: Azul, Bit 1: Verde, Bit 2: Rojo
        if state == 0:
            rgb_led.next = 0b010  # Verde: Desarmada
        elif (state == 1) or (state == 3):
            rgb_led.next = 0b110  # Amarillo (Rojo+Verde): En retardo
        elif state == 2:
            rgb_led.next = 0b001  # Azul: Armada vigilando
        else:
            rgb_led.next = 0b100  # Rojo: Disparada

        # Generador de tono y parpadeo de 16 LEDs en estado de alarma
        if siren_en == 1:
            aud_sd.next = 1
            if tone_cnt == tone_half_period - 1:
                tone_cnt.next = 0
                tone_reg.next = not tone_reg
            else:
                tone_cnt.next = tone_cnt + 1

            aud_pwm.next = tone_reg
            if tone_reg == 1:
                leds.next = 0xAAAA
            else:
                leds.next = 0x5555
        else:
            aud_sd.next = 0
            tone_cnt.next = 0
            tone_reg.next = 0
            aud_pwm.next = 0
            leds.next = 0x0000

    return logic
