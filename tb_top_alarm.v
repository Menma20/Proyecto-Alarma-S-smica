module tb_top_alarm;

reg clk;
reg rst;
reg [3:0] sw_code;
reg sw_pir;
reg btnc;
wire [6:0] seg_n;
wire [7:0] an_n;
wire [15:0] leds;
wire [2:0] rgb_led;
wire aud_pwm;
wire aud_sd;

initial begin
    $from_myhdl(
        clk,
        rst,
        sw_code,
        sw_pir,
        btnc
    );
    $to_myhdl(
        seg_n,
        an_n,
        leds,
        rgb_led,
        aud_pwm,
        aud_sd
    );
end

top_alarm dut(
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
    aud_sd
);

endmodule
