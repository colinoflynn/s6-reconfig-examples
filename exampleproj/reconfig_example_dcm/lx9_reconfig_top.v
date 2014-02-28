`timescale 1ns / 1ps

/* Do NOT allow undeclared nets */
`default_nettype none

/*
Example for June 2014 - Programmable Logic In Practice.

Copyright Colin O'Flynn 2014. All Rights Reserved.
*/

module lx9_reconfig_top(
	 //Inputs
	 input wire 	USER_RESET,
	 input wire 	USER_CLOCK,
	 
	 //PMod Connection: J5, Pin 1
	 output wire 	PMOD1_P1,
	 
	 //Serial Connection (if used)
	 input wire 	USB_RS232_RXD,
	 output wire 	USB_RS232_TXD,
	 
	 //LEDs
	 output wire   GPIO_LED1,
	 output wire   GPIO_LED2
    );

	 wire reset;
	 wire inpclk;
	 wire oupclk;
	 
	 assign reset = USER_RESET;
	 
	 BUFG bufg_inst (
		.O(inpclk), // 1-bit output: Clock buffer output
		.I(USER_CLOCK) // 1-bit input: Clock buffer input
	 );
	 
	 reg [24:0] counterinp;
	 reg [24:0] counteroup;
	 
	 assign GPIO_LED1 = counterinp[24];
	 assign GPIO_LED2 = counteroup[24];
	 
	 always @(posedge inpclk) begin
		counterinp <= counterinp + 25'd1;
	 end

	 always @(posedge oupclk) begin
		counteroup <= counteroup + 25'd1;
	 end

	 //DCM Block we will be reconfiguring with partial reconfiguration
	 generate_clock gclock_i
    (
      .CLK_IN1(inpclk),     
      .CLK_OUT1(oupclk),    
      .RESET(reset)
	 );
	 
	 //Outputing clock on S6 device only requires this
	 ODDR2 #(
		.DDR_ALIGNMENT("NONE"),
		.INIT(1'b0),
		.SRTYPE("SYNC")
	) ODDR2_inst (
		.Q (PMOD1_P1), // 1-bit DDR output data
		.C0 (oupclk), // 1-bit clock input
		.C1 (~oupclk), // 1-bit clock input
		.CE (1'b1), // 1-bit clock enable input
		.D0 (1'b1),
		.D1 (1'b0),
		.R (1'b0), // 1-bit reset input
		.S (1'b0));

	 wire sysclk;
	 assign sysclk = inpclk;

	 /***** Serial Interface *****/
	 wire cmdfifo_rxf;
	 wire cmdfifo_txe;
	 wire cmdfifo_rd;
	 wire cmdfifo_wr;
	 wire cmdfifo_isout;
	 wire [7:0] cmdfifo_din;
	 wire [7:0] cmdfifo_dout;
	 serial_reg_iface cmdfifo_serial(.reset_i(reset),
										  .clk_i(sysclk),
										  .rx_i(USB_RS232_RXD),
										  .tx_o(USB_RS232_TXD),
										  .cmdfifo_rxf(cmdfifo_rxf),
										  .cmdfifo_txe(cmdfifo_txe),
										  .cmdfifo_rd(cmdfifo_rd),
										  .cmdfifo_wr(cmdfifo_wr),
										  .cmdfifo_din(cmdfifo_din),
										  .cmdfifo_dout(cmdfifo_dout));	

	 /***** Register Interface *****/
	 wire reg_clk;
	 wire [5:0] reg_address;
	 wire [15:0] reg_bytecnt;
	 wire [7:0] reg_datao;
	 wire [15:0] reg_size;
	 wire reg_read;
	 wire reg_write;
	 wire reg_addrvalid;
	 wire [5:0] reg_hypaddress;
	 wire reg_stream;	 
	 wire [15:0] reg_hyplen;
	 wire [7:0] reg_datai_reconfig;	 
	 
	 reg_main registers_mainctl (
		.reset_i(reset), 
		.clk(sysclk), 
		.cmdfifo_rxf(cmdfifo_rxf), 
		.cmdfifo_txe(cmdfifo_txe), 
		.cmdfifo_rd(cmdfifo_rd), 
		.cmdfifo_wr(cmdfifo_wr), 
		.cmdfifo_din(cmdfifo_din), 
		.cmdfifo_dout(cmdfifo_dout), 
		.cmdfifo_isout(cmdfifo_isout), 
		.reg_clk(reg_clk), 
		.reg_address(reg_address), 
		.reg_bytecnt(reg_bytecnt), 
		.reg_datao(reg_datao), 
		.reg_datai(reg_datai_reconfig), 
		.reg_size(reg_size), 
		.reg_read(reg_read), 
		.reg_write(reg_write), 
		.reg_addrvalid(reg_addrvalid), 
		.reg_stream(reg_stream),
		.reg_hypaddress(reg_hypaddress), 
		.reg_hyplen(reg_hyplen)
	);	
	
	/***** Reconfiguration Registers *****/
		
	reg_reconfig reconfiguration(
		.reset_i(reset),
		.clk(reg_clk),
		.reg_address(reg_address), 
		.reg_bytecnt(reg_bytecnt), 
		.reg_datao(reg_datai_reconfig), 
		.reg_datai(reg_datao), 
		.reg_size(reg_size), 
		.reg_read(reg_read), 
		.reg_write(reg_write), 
		.reg_addrvalid(reg_addrvalid), 
		.reg_stream(reg_stream),
		.reg_hypaddress(reg_hypaddress), 
		.reg_hyplen(reg_hyplen)
	);

endmodule
