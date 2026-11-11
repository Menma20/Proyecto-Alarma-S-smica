# Sistema de Alarma Digital con Retardo (FPGA Nexys 4 DDR)

Repositorio oficial para el proyecto final de **Sistemas Digitales (Electrónica Digital)** de la Universidad de San Buenaventura Bogotá. Implementa un sistema de control de acceso y alarma con retardo de entrada/salida y máquina de estados finitos (FSM) diseñado en **MyHDL** y desplegado sobre una tarjeta **Digilent Nexys 4 DDR (FPGA Xilinx Artix-7)**[cite: 1, 13, 127].

---

## 📋 Descripción del Proyecto (Propuesta 12)

El sistema simula una alarma de seguridad residencial o comercial utilizando los periféricos integrados de la tarjeta Nexys 4 DDR sin necesidad de componentes externos[cite: 1, 127]. Está gobernado por una Máquina de Estados Finitos (FSM) con 5 modos operativos[cite: 1, 36]:

1. **`DESARMADA` (Estado 0):** Sistema en reposo. El display de 7 segmentos muestra la letra **`d`** y el LED tricolor brilla en **Verde**[cite: 1, 81, 127]. Se arma ingresando la clave secreta (`1010`) en los *switches* (`SW3..SW0`) y presionando el botón central (`BTNC`)[cite: 1, 127].
2. **`RETARDO_SALIDA` (Estado 1):** Cuenta regresiva de **`9` a `0` segundos** en el display (LED tricolor en **Amarillo**) para permitir la salida del usuario[cite: 1, 127].
3. **`ARMADA` (Estado 2):** Vigilancia activa. El display muestra la letra **`A`** y el LED tricolor cambia a **Azul**[cite: 1, 81, 127]. Si se activa el sensor de intrusión (`SW15`), la alarma pasa a retardo de entrada[cite: 1, 127].
4. **`RETARDO_ENTRADA` (Estado 3):** Cuenta regresiva de **`9` a `0` segundos** (LED tricolor en **Amarillo**) para que el usuario ingrese la clave correcta y desarme el sistema antes de que se dispare[cite: 1, 127].
5. **`DISPARADA` (Estado 4):** Si el tiempo expira sin desarmar, el display muestra **`E`**, el LED tricolor pasa a **Rojo**, los 16 LEDs parpadean y se activa la sirena de audio de **1 kHz** por el puerto PWM de la placa[cite: 1, 127, 132].

---

## 🛠️ Estructura del Repositorio

```text
alarma_fpga_nexys4/
│
├── constraints/
│   └── top_alarm.xdc        # Mapeo físico de pines para la Nexys 4 DDR (Artix-7)
│
├── src/
│   ├── alarm_fsm.py         # Máquina de Estados Finitos (FSM) central
│   ├── comparator.py        # Comparador combinacional de clave (4 bits)
│   ├── countdown_timer.py   # Temporizador de cuenta regresiva con prescaler
│   ├── debounce.py          # Sincronizador y filtro antirrebote de botones
│   ├── sevensegdec.py       # Decodificador LUT para el display de 7 segmentos
│   ├── siren_pwm.py         # Generador de tono PWM (sirena) y control de LEDs
│   └── top_alarm.py         # Módulo superior estructural (Top-Level) y convertidor a Verilog
│
├── tests/
│   └── test_alarm_system.py # Suite completa de pruebas unitarias y de integración (pytest)
│
├── apio.ini                 # Configuración del entorno Open Source (Apio / Yosys)
└── top_alarm.v              # Archivo de hardware en Verilog generado para síntesis